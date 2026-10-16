#!/usr/bin/env python3
"""Execute notebooks in separate project kernels and preserve outputs for review."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
for name,subdir in [('IPYTHONDIR','ipython'),('JUPYTER_RUNTIME_DIR','jupyter-runtime'),('MPLCONFIGDIR','matplotlib')]:
    path=ROOT/'.cache'/subdir
    path.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault(name,str(path))

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start',type=int,default=1)
    parser.add_argument('--end',type=int,default=10)
    args=parser.parse_args()
    report=ROOT/'reports/preprocessing/notebook_execution.json'
    results=json.loads(report.read_text()) if report.exists() else {}
    for path in sorted((ROOT/'dnn-hmm').glob('*.ipynb')):
        stage=int(path.name[:2])
        if not args.start<=stage<=args.end:
            continue
        print('Executing',path.name,flush=True)
        nb=nbformat.read(path,as_version=4)
        nbformat.validate(nb)
        for index, cell in enumerate(nb.cells):
            if cell.cell_type == 'code':
                compile(cell.source, f'{path.name}:cell-{index}', 'exec')
        km=KernelManager(kernel_name='python3')
        km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
        client=NotebookClient(nb,km=km,timeout=600,resources={'metadata':{'path':str(path.parent)}})
        start=time.monotonic()
        try:
            # An externally supplied manager must be explicitly cleaned up by the client context.
            with client.setup_kernel(cleanup_kc=True):
                client.execute()
            results[path.name]={'status':'passed','code_cells':sum(c.cell_type=='code' for c in nb.cells),
                                'seconds':round(time.monotonic()-start,2)}
        except Exception as error:
            results[path.name]={'status':'failed','error':str(error)}
            raise
        finally:
            nbformat.write(nb,path)
            report.parent.mkdir(parents=True,exist_ok=True)
            report.write_text(json.dumps(results,indent=2)+'\n')
    print('Notebook execution complete.',flush=True)


if __name__=='__main__':
    main()
