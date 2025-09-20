# xPeerd Analysis Pipeline

This repository contains a comprehensive Python script designed for analyzing peer review reports. The pipeline processes a CSV file of review data, extracts structured information, classifies each review into an academic supergroup, performs statistical analysis, and generates a series of publication-quality visualizations.

## Overview

The core functionality of this script is to transform unstructured peer review text into quantitative data and insightful visualizations. The end-to-end pipeline follows these steps:

**CSV → JSON (cases) → ASJC Supergroups → Analytics/Stats → JSON (results) → PNG Figures**

1.  **Ingestion**: Loads peer review data from a user-uploaded CSV file containing `Prompt` and `Completion` columns.
2.  **Extraction**: Parses each review to identify the review type, editorial decision (Accept, Revise, Reject), major and minor issues, and other metadata.
3.  **Classification**: Assigns each review to an All Science Journal Classification (ASJC) supergroup (e.g., "Life Sciences", "Physical Sciences") using a sophisticated hybrid model that combines lexical analysis and sentence embeddings.
4.  **Analysis**: Conducts statistical tests (Chi-squared, Kruskal-Wallis, Spearman's rank correlation) to uncover correlations between variables like review type, academic discipline, decision, and report quality metrics.
5.  **Export**: Saves all processed data, aggregated statistics, and correlation results into a structured JSON file (`evaluation_results.json`).
6.  **Visualization**: Generates a set of five professional, "Nature-grade" plots to visually represent the findings and saves them as PNG files.

---

## How It Works: The Pipeline in Detail

### 0. Setup

-   **Environment**: Initializes the output directory (`/content/xpeerd_outputs`) and clears any pre-existing files.
-   **Constants**: Defines key parameters for the analysis:
    -   `ALLOWED`: A list of valid review types to process.
    -   `DEC_ORDER`: The categorical order for editorial decisions.
    -   `SHORT_MIN_W`: The minimum word count for a review to be included.
    -   `ANCHOR_RULE`: The threshold for the "page anchor fraction," a metric for report quality.
-   **Regular Expressions**: Pre-compiles several regex patterns to efficiently find and extract information like review types, editorial decisions, and specific textual cues (e.g., "accept", "reject", page numbers, figures).

### 1. Upload & Preprocessing

-   **File Upload**: Uses Google Colab's `files.upload()` utility to prompt the user to upload their source CSV file.
-   **Data Loading**: Reads the CSV into a Pandas DataFrame. It intelligently maps the required `Prompt` and `Completion` columns, ignoring case.
-   **Text Cleaning**: A `clean_markdown` function removes Markdown syntax (`#`, `*`, `_`, etc.) and extra whitespace from the prompt and completion texts to prepare them for analysis.

### 2. Data Extraction

-   The script iterates through each row of the DataFrame to extract structured data.
-   **Review Type Detection**: `detect_type_from_prompt` uses regex to determine the review category (e.g., `/HCReview`, `/DAReview`).
-   **Issue Counting**: `count_maj_min` splits the review text into sentences and searches for semantic cues to count "major" (e.g., "fatal flaw", "critical") and "minor" (e.g., "typo", "grammar") issues.
-   **Decision Extraction**: `extract_editorial_decision_and_text_from_completion` uses a series of patterns to find the final recommendation, normalizing it to "Accept," "Revise," or "Reject."
-   **Special Handling**: Logic is included to handle specific review types, like `/DBReviewSim`, where it aggregates decisions from multiple reviewers.
-   **Output**: All extracted information for each valid review is stored in a dictionary and collected into a list. This list is then saved as `extracted_cases.json`.

### 3. ASJC Classification

-   A sophisticated hybrid model, `classify_asjc_refined`, assigns each review to one of five core academic supergroups (`Life Sciences`, `Physical Sciences`, `Health Sciences`, `Social Sciences`, `Humanities`) or `Multidisciplinary`.
-   **Lexical Analysis**: The model first performs a lexical scan using `_lexical_scores`, searching for seed keywords specific to each discipline.
-   **Semantic Analysis**: It then uses a pre-trained `SentenceTransformer` model (`all-MiniLM-L6-v2`) to generate a semantic embedding of the review text and compares its cosine similarity to embeddings of the ASJC category definitions.
-   **Hybrid Scoring**: The final classification probability is a weighted combination of the lexical and semantic scores. The weighting (`alpha`) is dynamic, giving more influence to the lexical score when more seed terms are found.
-   **Uncertainty Handling**: The function also calculates confidence scores and an entropy value to flag uncertain classifications.

### 4. Analytics & Correlations

-   The script converts the list of report dictionaries back into a Pandas DataFrame for statistical analysis.
-   Categorical data types are enforced for `decision`, `review_type`, and `ASJC_supergroup` to ensure correct ordering and grouping.
-   **Statistical Tests**:
    -   **Chi-squared test (`chi2_contingency`)**: Used to check for significant associations between categorical variables (e.g., "Is there a relationship between the ASJC supergroup and the final decision?").
    -   **Kruskal-Wallis H-test (`kruskal`)**: A non-parametric test used to determine if there are statistically significant differences between two or more groups of an independent variable on a continuous or ordinal dependent variable (e.g., "Does the number of 'major issues' differ across review types?").
-   The results of these tests (chi-squared value, p-value, degrees of freedom) are stored in a dictionary.

### 5. Statistics & Final JSON Export

-   Additional summary statistics are computed, such as a Spearman correlation (`spearmanr`) between report length and the page anchor rate.
-   All data streams—metadata, individual case data, aggregate counts, and correlation results—are compiled into a single `evaluation` dictionary.
-   This comprehensive dictionary is then exported to `evaluation_results.json`, providing a complete, machine-readable summary of the entire analysis.

### 6. Visualization

-   The final stage generates high-quality plots using `matplotlib` and `seaborn` with a "Nature-grade" aesthetic.
-   **Figure 1**: A dual-pane plot showing the distribution of cases across ASJC supergroups and the confidence scores of the classifier.
-   **Figure 2**: A stacked bar chart illustrating the proportion of editorial decisions (Accept, Revise, Reject) within each ASJC supergroup.
-   **Figure 3**: A scatter plot with a regression line showing the relationship between the length of a review and its page anchor rate, annotated with the Spearman's correlation coefficient.
-   **Figure 4**: A violin plot combined with a stripplot to show both the distribution and individual data points for the total number of issues identified, grouped by review type.
-   **Figure 5**: A dual bar chart showing the compliance rate with the page anchoring rule, broken down by both ASJC supergroup and review type.

---

## Requirements

The script is designed to run in a Python environment with the following libraries installed:
-   `numpy`
-   `pandas`
-   `tqdm`
-   `scipy`
-   `sentence-transformers`
-   `matplotlib`
-   `seaborn`
-   `google.colab` (for use in Google Colaboratory)

You can install the core dependencies using pip:
```bash
pip install pandas numpy scipy sentence-transformers matplotlib seaborn tqdm

---
## Input Data Format
Your input *.csv file must contain the following columns:
Prompt: The input or prompt given to generate the peer review. This is used to detect the review type.
Completion: The full text of the peer review report.
Time (Optional): A timestamp in ISO format.
Prompt,Completion,Time
"Generate a peer review for a paper on topic X. /HCReview","This paper presents a novel method... The main weakness is in section 3...",2025-09-20T20:00:00Z
"Simulate a debate between two reviewers. /DBReviewSim","Reviewer 1: I recommend acceptance... Reviewer 2: I must disagree, there are fatal flaws...",2025-09-20T20:05:10Z
---
## Output Files
The script generates the following files in the OUT_DIR (/content/xpeerd_outputs/):
extracted_cases.json: A JSON file containing the structured data for each individual review after the extraction and ASJC classification stages.
evaluation_results.json: The final, comprehensive JSON output. It contains all metadata, a copy of the case data, aggregate statistics, and correlation results.
Figure1.png: ASJC Supergroup Classification Counts and Confidence.
Figure2.png: Distribution of Editorial Decisions by ASJC Supergroup.
Figure3.png: Report Length vs. Page Anchor Rate scatter plot.
Figure4.png: Total Issues Detected by Review Type violin plot.
Figure5.png: Compliance with Page Anchoring Rule bar charts.

