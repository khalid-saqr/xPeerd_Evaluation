from __future__ import annotations
import hashlib
from pathlib import Path
import requests

DOI='10.5281/zenodo.21479700'
RECORD_ID='21479700'
FILENAME='xpeerd_benchmark_study_2026_v1.0.0.zip'
SHA256='0ab7cb88d2b2db687b586ad303e017a9db0a8104e10f1b8e18c30b8f6a75129c'
MD5='95bb05a1d2164d66db24a5176749aa77'

def digest(path, algorithm):
    h=hashlib.new(algorithm)
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def verify(path):
    path=Path(path)
    if not path.is_file(): raise FileNotFoundError(path)
    observed={'sha256':digest(path,'sha256'),'md5':digest(path,'md5'),'bytes':path.stat().st_size}
    if observed['sha256']!=SHA256: raise RuntimeError(f"SHA-256 mismatch: {observed['sha256']} != {SHA256}")
    if observed['md5']!=MD5: raise RuntimeError(f"MD5 mismatch: {observed['md5']} != {MD5}")
    return observed

def _entries(record):
    files=record.get('files',[])
    if isinstance(files,list): return files
    if isinstance(files,dict):
        entries=files.get('entries',files)
        if isinstance(entries,dict): return list(entries.values())
        if isinstance(entries,list): return entries
    return []

def download(destination, force=False):
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists() and not force:
        verify(destination); return destination
    destination.unlink(missing_ok=True)
    session=requests.Session(); session.headers['User-Agent']='TRACE-R-reproducibility/1.0.0'
    urls=[]; api=f'https://zenodo.org/api/records/{RECORD_ID}'
    try:
        r=session.get(api,timeout=60); r.raise_for_status(); record=r.json()
        for e in _entries(record):
            name=e.get('key') or e.get('filename') or e.get('name')
            if name==FILENAME:
                links=e.get('links') or {}; url=links.get('content') or links.get('download') or links.get('self')
                if url: urls.append(url)
    except Exception: pass
    urls += [f'https://zenodo.org/records/{RECORD_ID}/files/{FILENAME}?download=1',
             f'https://zenodo.org/api/records/{RECORD_ID}/files/{FILENAME}/content']
    errors=[]
    for url in dict.fromkeys(urls):
        part=destination.with_suffix(destination.suffix+'.part')
        try:
            with session.get(url,stream=True,timeout=300) as r:
                r.raise_for_status()
                with part.open('wb') as f:
                    for chunk in r.iter_content(1024*1024):
                        if chunk: f.write(chunk)
            verify(part); part.replace(destination); return destination
        except Exception as exc:
            part.unlink(missing_ok=True); errors.append(f'{url}: {exc}')
    raise RuntimeError('Zenodo download failed:\n'+'\n'.join(errors))
