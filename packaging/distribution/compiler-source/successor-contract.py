#!/usr/bin/env python3
"""TA.2 supplemental source-family contract for the approved rc2 layout.

This is not a replacement for the canonical manifest validator or TA.2
producer gate. The frozen rc1 inventory is the baseline for rc2 extension.
No MVS or tape I/O, and no issuance of legal redistribution rights.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[3]
DIR = Path(__file__).resolve().parent
RC1 = ROOT / 'packaging/distribution/manifest/releases/BCPL-0.1.0-rc1.yaml'
RC2 = ROOT / 'packaging/distribution/manifest/releases/BCPL-0.1.0-rc2.yaml'
DSPAL = ROOT / 'config/dspal.yaml'
REGISTRY = ROOT / 'packaging/distribution/registry/releases.yaml'
SELECTION = DIR / 'source-selection.json'
GROUP = 'cambridge-source'

class ContractError(ValueError):
    pass

def need(check: bool, why: str) -> None:
    if not check:
        raise ContractError(why)

def read_yaml(path: Path) -> dict:
    doc = yaml.safe_load(path.read_text(encoding='utf8'))
    need(isinstance(doc, dict), f'{path.name}: malformed YAML document')
    return doc

def expected_members(selection: dict) -> tuple[dict, dict, dict]:
    groups = {g['role']: g['members'] for g in selection['source_sets']}
    need(set(groups) == {'historical','derived','support'}, 'source family mismatch')
    need(len(groups['historical']) == 15 and len(groups['derived']) == 11
         and len(groups['support']) == 3, 'source family count mismatch')
    return groups['historical'], groups['derived'], groups['support']

def verify(rc1: dict, rc2: dict, dspal: dict, registry: dict,
           selection: dict, rc2_bytes: bytes) -> dict:
    need(rc2.get('schema_version') == 1 and rc2.get('phase') == 'candidate',
         'rc2 must be a candidate under schema v1')
    rel = rc2['release']; prior = rc1['release']
    need(rel.get('candidate_id') == 'BCPL-0.1.0-rc2' and
         rel.get('version') == '0.1.0-rc2', 'successor release identity drift')
    need(rel.get('cambridge_source') == 'included' and
         rel.get('native_compiler') == 'absent',
         'Cambridge source is not a native executable')
    need(isinstance(rel.get('source_commit'), str) and
         len(rel['source_commit']) == 40 and
         all(c in '0123456789abcdef' for c in rel['source_commit']),
         'source freeze must be full Git SHA')
    need(prior.get('candidate_id') == 'BCPL-0.1.0-rc1' and
         rc1['volume']['volser'] == 'BC0001', 'rc1 baseline identity drift')
    vol = rc2['volume']
    need(vol.get('volser') == 'BC0002' and
         vol.get('registry_reservation') == 'BCPL-0.1.0-rc2',
         'successor VOLSER/reservation drift')
    need(rel['source_commit'] != prior['source_commit'],
         'new source-inclusive candidate must use new Git freeze')
    entries = rc2['datasets']; base = rc1['datasets']
    need(len(base) == 20 and len(entries) == 22, 'two additional datasets required')
    need(entries[:20] == base, 'accepted rc1 dataset selection changed')
    need(entries[0]['generator'] == 'bootstrap_fb80' and
         entries[1]['generator'] == 'installer_pds',
         'reserved bootstrap/installer changed')
    need(all(r['sequence'] == i for i,r in enumerate(entries,1)),
         'noncontiguous release tape dataset sequence')
    need(rc2['profiles'] == {
        'mr10-only': ['common','mr10'],
        'native-only': ['common','native',GROUP],
        'combined': ['common','mr10','native',GROUP],
    }, 'source profile closure mismatch')
    names = ('CAMB_SOURCE','CAMB_DEMOTED')
    hist, derived, support = expected_members(selection)
    expected = (hist, {**support, 'SNOTICE':
                      'packaging/distribution/compiler-source/SNOTICE.txt'})
    generated = derived
    for i, key in enumerate(names, 20):
        row = entries[i]
        managed = dspal['datasets'][key]
        need(row['sequence'] == i+1 and row['dspal_key'] == key and
             row['group'] == GROUP and row['kind'] == 'pds_unload' and
             row['owner'] == 'cambridge-compiler-source' and
             row['transfer'] == 'iebcopy_unload',
             f'BT{i+1:04d}: Cambridge source metadata mismatch')
        need(row['target_dsn_template'] == '{HLQ}.' + managed['dsn'],
             f'BT{i+1:04d}: recipient DSN differs from dspal')
        need(managed['populate'] is True and managed['type'] == 'pds',
             f'{key}: release source is not populated PDS')
        dcb = {'dsorg': 'PO','recfm': 'FB','lrecl': 80,'blksize': 800}
        need(row['target_dcb'] == dcb and all(managed[k] == v for k,v in dcb.items()),
             f'{key}: FB80 target DCB mismatch')
        need(managed['members'] == expected[i-20] and
             set(row['members']) == set(expected[i-20]) | (set(generated) if i==21 else set()),
             f'{key}: selected source lineage mismatch')
        need(managed.get('generated_members',{}) == (generated if i==21 else {}),
             f'{key}: generator member mapping mismatch')
        need(row.get('source_family') == ('historical' if i == 20 else 'demoted-and-support'),
             f'{key}: source family disclosure missing')
        need(row.get('rights_status') == 'preservation-policy-approved-rights-unresolved',
             f'{key}: historical/derivative rights claims changed')
    need(len(set(r.get('dspal_key') for r in entries[2:])) == 20,
         'duplicate selected PDS alias')
    candidates = registry['candidates']
    need(len(candidates)==2 and
         {r['candidate_id'] for r in candidates} ==
         {'BCPL-0.1.0-rc1','BCPL-0.1.0-rc2'},
         'registry candidate selection mismatch')
    old = next(x for x in candidates if x['candidate_id'].endswith('rc1'))
    new = next(x for x in candidates if x['candidate_id'].endswith('rc2'))
    need(old['volser']=='BC0001' and old['state']=='reserved' and
         old['source_commit']==prior['source_commit'],
         'prior reservation disturbed')
    need(new['state']=='reserved' and new['volser']=='BC0002' and
         new['source_commit']==rel['source_commit'] and
         new['version']==rel['version'] and
         new['manifest_sha256']==hashlib.sha256(rc2_bytes).hexdigest(),
         'successor registry/hash mismatch')
    need(len({x['volser'] for x in candidates}) == len(candidates),
         'duplicate reserved VOLSER')
    return {'candidate_id':rel['candidate_id'], 'volser':vol['volser'],
            'tape_datasets':len(entries), 'added_pds':2, 'new_source_members':30,
            'historical_sources':15,'derived_sources':11,'support_sources':3,
            'notice_members':1,'native_compiler':'absent',
            'mvs_stage_verified':False,'rights_verified':False}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args(argv)
    try:
        result=verify(read_yaml(RC1),read_yaml(RC2),read_yaml(DSPAL),
                      read_yaml(REGISTRY),json.loads(SELECTION.read_text()),
                      RC2.read_bytes())
    except (OSError,ValueError,KeyError,TypeError) as ex:
        print(f'TA.2 RC2 SOURCE CONTRACT HALTED: {ex}',file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result,sort_keys=True,indent=2))
    else:
        print('TA.2 RC2 SOURCE LAYOUT: 22 logical datasets; 2 new PDSes; 30 source/notice members PASS')
        print('RELEASE GATES OPEN: MVS staging, provenance receipts, native compiler absent; no tape created')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
