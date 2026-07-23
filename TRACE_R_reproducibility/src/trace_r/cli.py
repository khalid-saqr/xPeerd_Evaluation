from __future__ import annotations
import argparse, json
from pathlib import Path
from .acquisition import download, verify, FILENAME
from .pipeline import run_analysis

def main(argv=None):
    p=argparse.ArgumentParser(description='Reproduce the locked TRACE-R xPeerd analysis.')
    p.add_argument('--input-zip',type=Path,help='Use a local source ZIP instead of downloading Zenodo.')
    p.add_argument('--output',type=Path,default=Path('results'))
    p.add_argument('--download-dir',type=Path,default=Path('.cache/trace-r'))
    args=p.parse_args(argv)
    source=args.input_zip if args.input_zip else download(args.download_dir/FILENAME)
    verify(source)
    report=run_analysis(source,args.output)
    print(json.dumps(report,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
