from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import pandas as pd

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument('results',type=Path); args=p.parse_args()
    root=Path(__file__).parent; expected=json.loads((root/'reference/expected_counts.json').read_text())
    report=json.loads((args.results/'TRACE_R_COMPLETION_REPORT.json').read_text())
    checks={
      'included_manuscripts':report.get('included_manuscripts')==expected['included_manuscripts'],
      'excluded_records':report.get('excluded_records')==expected['excluded_records'],
      'report_rows':report.get('report_rows')==expected['report_rows'],
      'concern_units':report.get('concern_units')==expected['concern_units'],
      'quality_gates':report.get('quality_checks_passed')==report.get('quality_checks_total')==expected['quality_checks_total'],
      'figures':report.get('figure_files_passed')==expected['figure_files'],
    }
    hashes=pd.read_csv(root/'reference/reference_table_hashes.csv')
    for row in hashes.itertuples(index=False):
        path=args.results/row.relative_path
        checks['hash:'+row.relative_path]=path.exists() and sha(path)==row.sha256
    failed=[k for k,v in checks.items() if not v]
    result={'status':'PASS' if not failed else 'FAIL','checks':len(checks),'failed':failed}
    print(json.dumps(result,indent=2)); raise SystemExit(1 if failed else 0)
if __name__=='__main__': main()
