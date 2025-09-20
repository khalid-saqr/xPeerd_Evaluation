# === xPeerd Pipeline (Clean Fixed Version with Revised Plotting) ===
# CSV → JSON(cases) → ASJC Supergroups → Analytics/Stats → JSON(results) → PNG Figures
# Colab-ready

import os, re, json, glob, math
from datetime import datetime, UTC
from typing import List, Tuple
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from scipy import stats as spstats
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache
from google.colab import files
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# 0) Setup
# -----------------------------
OUT_DIR = "/content/xpeerd_outputs"
os.makedirs(OUT_DIR, exist_ok=True)
for f in glob.glob(os.path.join(OUT_DIR, "*")):
    try:
        os.remove(f)
    except:
        pass

ALLOWED   = ["/HCReview","/DAReview","/DBReviewSim","/PRR","/ConfReview"]
DEC_ORDER = ["Reject","Revise","Accept"]
SHORT_MIN_W = 200
ANCHOR_RULE = 0.2

# --- Regex Salvage ---
TYPE_PAT       = re.compile(r'/(HCReview|DAReview|DBReviewSim|PRR|ConfReview)\b', re.I)
DEC_LINE_PAT   = re.compile(r'(?im)^\s*(?:\*\*?\s*)?(?:Final\s+)?(?:Overall\s+)?'
                            r'(?:Recommendation|Decision|Verdict|Outcome|Evaluation|Editor\s*Decision)\s*[:\-—]\s*([A-Za-z ]+)\s*$')
REC_INLINE_PAT = re.compile(r'(?i)\brecommend(?:ation)?\s+(?:is\s+)?(?:a\s+)?(reject|revise|accept|approve|minor|major)\b')

ACCEPT_CUES = re.compile(r'\baccept(?:ed|ance)?\b', re.I)
REJECT_CUES = re.compile(r'\breject|decline|desk\s*reject|fatal\s+flaw|plagiar|misconduct|ethic', re.I)
REVISE_CUES = re.compile(r'\brev(ise|ision)|resubmit|conditional', re.I)

PAGE_CUE    = re.compile(r'(\bpage\s*\d+\b|\bp\.\s*\d+\b|fig(?:ure)?\s*\d+|table\s*\d+|section\s*\d+)', re.I)

def s(x):
    return x if isinstance(x,str) else ""

def safe_iso(x):
    try:
        return datetime.fromisoformat(s(x).replace("Z","+00:00")).isoformat()
    except:
        return ""

def detect_type_from_prompt(prompt: str) -> str:
    p = s(prompt)
    m = TYPE_PAT.search(p)
    return "/"+m.group(1) if m else "/HCReview"

# --- Semantic issue detection ---
MAJOR_CUES = re.compile(r"(serious|fatal|critical|blocking|irreproducible|plagiarism|fraud|unethical|invalid)", re.I)
MINOR_CUES = re.compile(r"(minor|typo|grammar|format|clarity|style|small|editorial)", re.I)

def count_maj_min(txt: str) -> Tuple[int,int,list,list]:
    majors, minors = [], []
    for sent in re.split(r'(?<=[.!?])\s+', s(txt)):
        if MAJOR_CUES.search(sent):
            majors.append(sent.strip())
        elif MINOR_CUES.search(sent):
            minors.append(sent.strip())
    if not majors and not minors:
        minors.append("General comment – needs clarification")
    return len(majors), len(minors), majors, minors

def page_anchor_fraction(majors, minors):
    items = list(majors)+list(minors)
    if not items:
        return 0.0
    return sum(1 for t in items if PAGE_CUE.search(s(t)))/len(items)

def normalize_dec_string(x: str) -> str:
    t = s(x).lower()
    if "accept" in t: return "Accept"
    if "reject" in t: return "Reject"
    if "revise" in t or "minor" in t or "major" in t: return "Revise"
    return ""

def extract_editorial_decision_and_text_from_completion(cmpl: str):
    txt = s(cmpl)
    m = DEC_LINE_PAT.findall(txt)
    if m:
        dec = normalize_dec_string(m[-1])
        return (dec if dec else np.nan), m[-1].strip()
    m2 = REC_INLINE_PAT.search(txt)
    if m2:
        dec = normalize_dec_string(m2.group(1))
        return (dec if dec else np.nan), m2.group(0).strip()
    tail = txt[-1000:]
    if REJECT_CUES.search(tail): return "Reject", ""
    if ACCEPT_CUES.search(tail): return "Accept", ""
    if REVISE_CUES.search(tail): return "Revise", ""
    return np.nan, ""

def aggregate_db_from_completion(cmpl: str):
    blocks = re.findall(r'(?is)Reviewer\s*#?\s*([12])\b(.*?)(?=Reviewer\s*#?\s*[12]\b|$)', s(cmpl))
    if not blocks: return np.nan, np.nan
    vals=[]
    for rid, body in blocks:
        if REJECT_CUES.search(body): vals.append(("Reject", rid))
        elif ACCEPT_CUES.search(body): vals.append(("Accept", rid))
        elif REVISE_CUES.search(body): vals.append(("Revise", rid))
    if not vals: return np.nan, np.nan
    votes = [v for v,_ in vals]
    agg = votes[0] if all(v==votes[0] for v in votes) else "Revise"
    return agg, int(len(set(votes))>1)

# -----------------------------
# 1) Upload CSV
# -----------------------------
print("Upload CSV with columns: Prompt, Completion. Time optional.")
uploaded = files.upload()
if not uploaded: raise RuntimeError("No file uploaded.")
csv_name = list(uploaded.keys())[-1]
df = pd.read_csv(csv_name, dtype=str, keep_default_na=False)
print(f"Loaded: {csv_name} rows={len(df)} cols={list(df.columns)}")

colmap = {c.lower(): c for c in df.columns}
PROMPT_COL, COMPL_COL = colmap.get("prompt"), colmap.get("completion")
TIME_COL               = colmap.get("time")
if not PROMPT_COL or not COMPL_COL:
    raise ValueError("CSV must have Prompt and Completion columns (case-insensitive).")

def clean_markdown(text: str) -> str:
    if not isinstance(text, str): return ""
    text = re.sub(r'[#*_`>~\-]{1,}', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df[PROMPT_COL] = df[PROMPT_COL].apply(clean_markdown)
df[COMPL_COL]  = df[COMPL_COL].apply(clean_markdown)

# -----------------------------
# 2) Extract → JSON (cases)
# -----------------------------
reports=[]
ex_report = {"total_rows": int(len(df)), "excluded_missing_fields":0,
             "excluded_too_short":0,"excluded_misfire":0,"no_decision_detected":0}

for i, r in tqdm(df.iterrows(), total=len(df)):
    prompt = s(r.get(PROMPT_COL,"")).strip()
    cmpl   = s(r.get(COMPL_COL,"")).strip()
    rtype = detect_type_from_prompt(prompt)

    if not cmpl or rtype not in ALLOWED:
        ex_report["excluded_missing_fields"] += 1; continue
    if len(cmpl.split()) < SHORT_MIN_W:
        ex_report["excluded_too_short"] += 1; continue

    nmaj,nmin,maj_list,min_list = count_maj_min(cmpl)
    par = page_anchor_fraction(maj_list, min_list)

    dec_cat, rec_text = ("Reject","") if rtype=="/PRR" else extract_editorial_decision_and_text_from_completion(cmpl)
    if pd.isna(dec_cat) or dec_cat=="":
        if "accept" in cmpl.lower(): dec_cat="Accept"
        elif "reject" in cmpl.lower(): dec_cat="Reject"
        elif "revise" in cmpl.lower() or "minor" in cmpl.lower() or "major" in cmpl.lower(): dec_cat="Revise"
        else: dec_cat=np.nan
        if pd.isna(dec_cat): ex_report["no_decision_detected"] += 1

    db_disagree=np.nan
    if rtype=="/DBReviewSim":
        agg, db_disagree = aggregate_db_from_completion(cmpl)
        if pd.isna(agg): agg, db_disagree="Revise",1
        dec_cat=agg

    reports.append({
        "report_id": f"row{i}","review_type":rtype,
        "peer_review_report":cmpl,"prompt":prompt,
        "decision": dec_cat if dec_cat==dec_cat else None,
        "recommendation_text": rec_text,
        "major": maj_list,"minor": min_list,
        "counts": {"majors":nmaj,"minors":nmin,"total_issues":nmaj+nmin},
        "grounding": {"page_anchor_fraction": float(par)},
        "dbreviewsim": {"disagreement": db_disagree} if rtype=="/DBReviewSim" else {},
        "len_words": len(cmpl.split()),
        "time_iso": safe_iso(r.get(TIME_COL,"")) if TIME_COL else ""
    })

EXTRACTED_JSON = os.path.join(OUT_DIR,"extracted_cases.json")
with open(EXTRACTED_JSON,"w",encoding="utf-8") as f:
    json.dump(reports,f,indent=2,ensure_ascii=False)
print(f"Saved {EXTRACTED_JSON} cases={len(reports)}")

# -----------------------------
# 3) ASJC Classification
# -----------------------------
MULTI="Multidisciplinary"
ASJC_CORE=["Life Sciences","Physical Sciences","Health Sciences","Social Sciences","Humanities"]

ASJC_DEFS = {
    "Life Sciences": "Research on living organisms including biology, ecology, genetics, neuroscience, microbiology, environment.",
    "Physical Sciences": "Research on non-living systems including physics, chemistry, mathematics, computer science, engineering.",
    "Health Sciences": "Research on human and animal health including medicine, nursing, pharmacology, toxicology, and biomedical fields.",
    "Social Sciences": "Research on society and human behavior including economics, political science, sociology, psychology, and education.",
    "Humanities": "Research on human culture and thought including history, philology, hermeneutics, interpretation, aesthetics."
}

ASJC_SEEDS = {
    "Life Sciences": ["biology","ecology","genetics","zoology","microbiology","immunology","neuroscience","conservation"],
    "Physical Sciences": ["physics","chemistry","mathematics","engineering","algorithm","simulation","materials"],
    "Health Sciences": ["clinical","patient","trial","therapy","diagnosis","epidemiology","nursing","pharmacology","oncology"],
    "Social Sciences": ["economics","sociology","psychology","education","policy","management","culture"],
    "Humanities": ["philology","hermeneutics","aesthetics","semiotics","iconography","rhetoric","archaeology"]
}

@lru_cache(maxsize=None)
def _seed_patterns():
    pats={}
    for grp,terms in ASJC_SEEDS.items():
        compiled=[(t,re.compile(r"\b"+re.escape(t)+r"(e?s|al|ic|ics|ing|ed|s)?\b",re.I)) for t in terms]
        pats[grp]=compiled
    return pats

_asjc_model = SentenceTransformer("all-MiniLM-L6-v2")
_core_emb   = _asjc_model.encode([ASJC_DEFS[g] for g in ASJC_CORE],convert_to_tensor=True,normalize_embeddings=True)

def _softmax(x):
    e=np.exp(x-np.max(x)); return e/(e.sum()+1e-12)
def _entropy(p):
    q=p[p>0]; return float(-(q*np.log(q)).sum())
def _zscore(v):
    v=np.asarray(v,float); return (v-v.mean())/(v.std()+1e-12)

def _prep_text(prompt,completion,max_w=800):
    words=(completion or "").split()
    if len(words)>max_w:
        step=len(words)//3
        sample=words[:step//2]+words[step:step+step//2]+words[-step:]
        trunc=sample[:max_w]
    else: trunc=words
    return ((prompt or "")+" \n "+" ".join(trunc)).strip()

def _lexical_scores(doc):
    pats=_seed_patterns(); L=max(len(doc.split()),1); scores=[]
    for grp in ASJC_CORE:
        s=0.0
        for term,pat in pats[grp]:
            s+=math.log1p(len(pat.findall(doc)))
        scores.append(s/(L**0.5))
    return np.array(scores,float)

def classify_asjc_refined(completion_text,prompt_text=None,
                          min_conf=0.20,min_gap=0.12,ent_warn=1.45,
                          force_multi=0.01,topk=3):
    doc=_prep_text(prompt_text,completion_text)
    if not doc: return MULTI,[(MULTI,1.0)],1.0,float("nan"),True
    lex=_lexical_scores(doc); lex_n=_zscore(lex); hits=(lex>0).sum()
    doc_emb=_asjc_model.encode([doc],convert_to_tensor=True,normalize_embeddings=True)
    sims=util.cos_sim(doc_emb,_core_emb).cpu().numpy().ravel()
    sims_n=_zscore(sims)
    alpha=0.5*(0.5+0.5*hits/len(ASJC_CORE)) if hits else 0.0
    hybrid=alpha*lex_n+(1-alpha)*sims_n; probs=_softmax(hybrid)
    order=np.argsort(-probs); i0,i1=order[0],order[1]
    main=ASJC_CORE[i0]; p_top,p_sec=float(probs[i0]),float(probs[i1]); gap=p_top-p_sec; H=_entropy(probs)
    if p_top<force_multi or (H>=1.58 and gap<0.02):
        return MULTI,[(MULTI,1.0)],p_top,p_sec,True
    uncertain=not (p_top>=min_conf and gap>=min_gap and H<=ent_warn)
    top_list=[(ASJC_CORE[i],float(probs[i])) for i in order[:min(topk,len(ASJC_CORE))]]
    return main,top_list,p_top,p_sec,bool(uncertain)

for e in reports:
    main,top,conf,conf2,unc=classify_asjc_refined(e.get("peer_review_report",""),e.get("prompt",""))
    e["ASJC_supergroup"]=main; e["ASJC_top3"]=top
    e["ASJC_conf"]=float(conf); e["ASJC_conf2"]=float(conf2); e["ASJC_uncertain"]=bool(unc)

with open(EXTRACTED_JSON,"w",encoding="utf-8") as f:
    json.dump(reports,f,indent=2,ensure_ascii=False)
print("Updated extracted_cases.json with ASJC classifications")

# -----------------------------
# 4) Analytics + Correlations
# -----------------------------
SUPERGROUPS=ASJC_CORE+[MULTI]
data=pd.DataFrame(reports)
data["ASJC_supergroup"]=pd.Categorical(data["ASJC_supergroup"],categories=SUPERGROUPS)
data["review_type"]=pd.Categorical(data["review_type"],categories=ALLOWED)
data["decision"]=pd.Categorical(data["decision"],categories=DEC_ORDER)

data["majors"]=data["major"].apply(lambda x:len(x) if isinstance(x,list) else 0)
data["minors"]=data["minor"].apply(lambda x:len(x) if isinstance(x,list) else 0)
data["total_issues"]=data["counts"].apply(lambda x:x.get("total_issues",np.nan))
data["page_anchor_rate"]=data["grounding"].apply(lambda x:x.get("page_anchor_fraction",0.0))
data["db_disagree"]=data["dbreviewsim"].apply(lambda x:x.get("disagreement",np.nan) if isinstance(x,dict) else np.nan)
data["has_evidence"]=(data["majors"]+data["minors"])>0

from scipy.stats import chi2_contingency, kruskal
correlation_results={}

if data["decision"].notna().any():
    table=pd.crosstab(data["ASJC_supergroup"],data["decision"])
    if not table.empty and table.sum().sum()>0:
        chi2,p,dof,_=chi2_contingency(table)
        correlation_results["decision_vs_asjc"]={"chi2":float(chi2),"p":float(p),"dof":int(dof)}
    table=pd.crosstab(data["review_type"],data["decision"])
    if not table.empty and table.sum().sum()>0:
        chi2,p,dof,_=chi2_contingency(table)
        correlation_results["decision_vs_review_type"]={"chi2":float(chi2),"p":float(p),"dof":int(dof)}

def safe_kruskal(groups):
    valid=[g for g in groups if len(g)>1 and g.std()>0]
    if len(valid)>1:
        stat,p=kruskal(*valid); return float(stat),float(p)
    return None

comp_bin=(data["page_anchor_rate"]>=ANCHOR_RULE).astype(int)
res=safe_kruskal([comp_bin[data["ASJC_supergroup"]==g] for g in SUPERGROUPS])
if res: correlation_results["compliance_vs_asjc"]={"kruskal":res[0],"p":res[1]}
res=safe_kruskal([comp_bin[data["review_type"]==t] for t in ALLOWED])
if res: correlation_results["compliance_vs_review_type"]={"kruskal":res[0],"p":res[1]}

for metric in ["majors","minors","total_issues"]:
    series=data[metric].fillna(0)
    res=safe_kruskal([series[data["ASJC_supergroup"]==g] for g in SUPERGROUPS])
    if res: correlation_results[f"{metric}_vs_asjc"]={"kruskal":res[0],"p":res[1]}
    res=safe_kruskal([series[data["review_type"]==t] for t in ALLOWED])
    if res: correlation_results[f"{metric}_vs_review_type"]={"kruskal":res[0],"p":res[1]}

print("Analytics + correlations complete.")

# -----------------------------
# 5) Statistics
# -----------------------------
stats_results={}
ex_report["final_cases"]=int(len(reports))
stats_results["extraction_report"]=ex_report

mask=data["page_anchor_rate"].notna() & data["len_words"].notna()
if int(mask.sum())>5 and data.loc[mask,"len_words"].std()>0 and data.loc[mask,"page_anchor_rate"].std()>0:
    rho,p=spstats.spearmanr(data.loc[mask,"len_words"],data.loc[mask,"page_anchor_rate"])
    stats_results["len_vs_anchor_spearman"]={"rho":float(rho),"p":float(p)}

# -----------------------------
# 6) JSON-safe exports
# -----------------------------
aggregates = {
    "asjc_counts": data["ASJC_supergroup"].value_counts().reindex(SUPERGROUPS).fillna(0).astype(int).to_dict(),
    "counts_by_type": data["review_type"].value_counts().reindex(ALLOWED).fillna(0).astype(int).to_dict()
}

evaluation = {
    "meta": { "source_csv": csv_name, "generated_at": datetime.now(UTC).isoformat(), "extraction_report": ex_report },
    "cases": reports, "aggregates": aggregates, "statistics": stats_results, "correlations": correlation_results
}

EVAL_JSON = os.path.join(OUT_DIR,"evaluation_results.json")
with open(EVAL_JSON,"w",encoding="utf-8") as f:
    json.dump(evaluation,f,indent=2,ensure_ascii=False)
print(f"Saved {EVAL_JSON}")

# ---------------------------------------------------
# 7) Nature-Grade Plotting (Revised PNG Output)
# ---------------------------------------------------
print("\nGenerating Nature-grade plots...")

# --- Nature-Grade Plotting Settings ---
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_theme(style="ticks")

try:
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 10, 'axes.labelsize': 12, 'axes.titlesize': 14,
        'xtick.labelsize': 10, 'ytick.labelsize': 10, 'legend.fontsize': 10,
        'figure.titlesize': 16, 'savefig.dpi': 300,
        'pdf.fonttype': 42, 'ps.fonttype': 42
    })
except Exception as e:
    print(f"Could not set plotting parameters, using defaults. Error: {e}")

# --- Ensure correct data types and order for plotting ---
data['decision'] = pd.Categorical(data['decision'], categories=DEC_ORDER, ordered=True)
data['ASJC_supergroup'] = pd.Categorical(data['ASJC_supergroup'], categories=SUPERGROUPS, ordered=True)
data['review_type'] = pd.Categorical(data['review_type'], categories=ALLOWED, ordered=True)


# --- Figure 1: ASJC Classification Counts and Confidence ---
if 'ASJC_supergroup' in data.columns:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.suptitle('ASJC Supergroup Classification and Confidence', fontsize=16)

    # (a) Bar plot of ASJC classification categories
    asjc_counts = data['ASJC_supergroup'].value_counts().sort_index()
    sns.barplot(x=asjc_counts.index, y=asjc_counts.values, ax=ax1, palette='viridis')
    ax1.set_title('(a) Classification Counts')
    ax1.set_xlabel('ASJC Supergroup')
    ax1.set_ylabel('Number of Cases')
    ax1.tick_params(axis='x', rotation=45)
    for container in ax1.containers:
        ax1.bar_label(container, size=9) # Add count labels on bars

    # (b) Violin plot for the confidence of classification
    sns.violinplot(data=data.dropna(subset=['ASJC_conf', 'ASJC_supergroup']),
                   x='ASJC_supergroup', y='ASJC_conf', cut=0, inner="quartile", ax=ax2,
                   linewidth=1.5, palette='viridis')
    ax2.axhline(y=0.2, color='r', linestyle='--', label='Critical Threshold (0.2)')
    ax2.set_title('(b) Classification Confidence')
    ax2.set_xlabel('ASJC Supergroup')
    ax2.set_ylabel('Confidence Score')
    ax2.tick_params(axis='x', rotation=45)
    ax2.legend()

    sns.despine()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent suptitle overlap
    plt.savefig(os.path.join(OUT_DIR, "Figure1.png"))
    plt.close(fig)
    print("✓ Saved Figure1.png (ASJC Counts and Confidence).")


# --- Figure 2: Editorial Decisions by ASJC Supergroup ---
if 'decision' in data.columns and 'ASJC_supergroup' in data.columns:
    decision_proportions = data.groupby('ASJC_supergroup', observed=True)['decision'].value_counts(normalize=True).unstack(fill_value=0)
    decision_colors = {'Reject': '#d62728', 'Revise': '#ff7f0e', 'Accept': '#2ca02c'}

    fig, ax = plt.subplots(figsize=(10, 6))
    decision_proportions[DEC_ORDER].plot(kind='bar', stacked=True, ax=ax,
                                         color=[decision_colors.get(d, '#7f7f7f') for d in DEC_ORDER])

    ax.set_title('Distribution of Editorial Decisions by ASJC Supergroup')
    ax.set_xlabel('ASJC Supergroup')
    ax.set_ylabel('Proportion of Decisions')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(title='Decision', bbox_to_anchor=(1.05, 1), loc='upper left')
    sns.despine()
    plt.savefig(os.path.join(OUT_DIR, "Figure2.png"), bbox_inches='tight')
    plt.close(fig)
    print("✓ Saved Figure2.png (Decisions by ASJC).")


# --- Figure 3: Report Length vs. Page Anchor Rate ---
if 'len_words' in data.columns and 'page_anchor_rate' in data.columns:
    plot_data = data[['len_words', 'page_anchor_rate']].dropna()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(data=plot_data, x='len_words', y='page_anchor_rate',
                scatter_kws={'alpha': 0.5, 's': 25, 'edgecolor': 'w', 'linewidths': 0.5},
                line_kws={'color': '#d62728', 'linestyle': '--'}, ax=ax)

    if "len_vs_anchor_spearman" in stats_results:
        rho = stats_results["len_vs_anchor_spearman"]["rho"]
        p = stats_results["len_vs_anchor_spearman"]["p"]
        p_text = f"p < 0.001" if p < 0.001 else f"p = {p:.3f}"
        ax.text(0.05, 0.95, f"Spearman's ρ = {rho:.2f}\n{p_text}",
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.7))

    ax.set_title('Report Length vs. Page Anchor Rate')
    ax.set_xlabel('Completion Length (Words)')
    ax.set_ylabel('Page Anchor Fraction')
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(left=0)
    sns.despine()
    plt.savefig(os.path.join(OUT_DIR, "Figure3.png"), bbox_inches='tight')
    plt.close(fig)
    print("✓ Saved Figure3.png (Length vs. Anchor Scatter).")


# --- Figure 4: Total Issues by Review Type ---
if 'total_issues' in data.columns and 'review_type' in data.columns:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.violinplot(data=data.dropna(subset=['total_issues', 'review_type']),
                   x='review_type', y='total_issues', cut=0, inner="quartile", ax=ax, palette="mako")
    sns.stripplot(data=data.dropna(subset=['total_issues', 'review_type']),
                  x='review_type', y='total_issues', jitter=0.2, color='black', size=3, alpha=0.4, ax=ax)

    ax.set_title('Total Issues Detected by Review Type')
    ax.set_xlabel('Review Type')
    ax.set_ylabel('Total Issues (Major + Minor)')
    ax.tick_params(axis='x', rotation=25)
    sns.despine()
    plt.savefig(os.path.join(OUT_DIR, "Figure4.png"), bbox_inches='tight')
    plt.close(fig)
    print("✓ Saved Figure4.png (Total Issues by Review Type).")


# --- Figure 5: Compliance with Page Anchoring Rule ---
if 'page_anchor_rate' in data.columns:
    data['is_compliant'] = data['page_anchor_rate'] >= ANCHOR_RULE
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    fig.suptitle(f'Compliance with Page Anchoring Rule (Fraction ≥ {ANCHOR_RULE})', fontsize=16)

    # (a) Compliance by ASJC Supergroup
    sns.barplot(data=data, x='ASJC_supergroup', y='is_compliant', ax=ax1,
                palette='crest', errorbar=('ci', 95), capsize=.1)
    ax1.set_title('(a) Compliance by ASJC Supergroup')
    ax1.set_xlabel('ASJC Supergroup')
    ax1.set_ylabel('Compliance Rate')
    ax1.tick_params(axis='x', rotation=45)
    mean_comp = data['is_compliant'].mean()
    ax1.axhline(y=mean_comp, color='r', linestyle='--', label=f"Overall Mean ({mean_comp:.2f})")
    ax1.legend()
    ax1.set_ylim(0, 1)

    # (b) Compliance by Review Type
    sns.barplot(data=data, x='review_type', y='is_compliant', ax=ax2,
                palette='flare', errorbar=('ci', 95), capsize=.1)
    ax2.set_title('(b) Compliance by Review Type')
    ax2.set_xlabel('Review Type')
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=mean_comp, color='r', linestyle='--', label=f"Overall Mean ({mean_comp:.2f})")
    ax2.legend()

    sns.despine()
    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    plt.savefig(os.path.join(OUT_DIR, "Figure5.png"))
    plt.close(fig)
    print("✓ Saved Figure5.png (Anchoring Compliance).")


print(f"\nPlotting complete. All charts have been saved to the '{OUT_DIR}' directory.")
