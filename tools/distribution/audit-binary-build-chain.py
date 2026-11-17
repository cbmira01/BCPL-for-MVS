#!/usr/bin/env python3
"""Read-only TA.0 binary build-chain audit; never asserts MVS acceptance."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = Path(__file__).with_name('validate-manifest.py')
MANIFEST = ROOT / 'packaging/distribution/manifest/ta0-inventory.yaml'
DSPAL = ROOT / 'config/dspal.yaml'
VERIFY = ROOT / 'tools/reconstruction/verify.py'
BUILDER_KEYS = {'IC19BLD': 'MR10_JCL', 'BLIBBLD': 'BOOT_JCL',
                'BLDBMAIN': 'BOOT_JCL', 'BLDCORCO': 'BOOT_JCL',
                'BLDCORLB': 'BOOT_JCL', 'BCPLDEMO': 'BOOT_JCL',
                'BCPLTIME': 'BOOT_JCL', 'BCPLQSAM': 'BOOT_JCL'}
CORE = ('BCPLMAIN', 'BCPLMEM', 'BCPLBYTE', 'BCPLAPT',
        'BCPLIO', 'BCPLRGS', 'BCPLREG')
EXT = ('BCPLDEMO', 'BCPLTIME', 'BCPLQSAM')
BINARY_KEYS = ('MR10_OBJ', 'MR10_LOAD', 'BOOT_OBJ', 'EXT_OBJ')
STEP = re.compile(r'^//([A-Z0-9@$#]{1,8})\s+EXEC\b', re.M)
MEMBER = re.compile(r'    ([A-Z@$#][A-Z0-9@$#]{0,7})\s*')

_spec = importlib.util.spec_from_file_location('ta0_manifest_validation', VALIDATOR)
assert _spec and _spec.loader
validation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validation)


class ChainError(ValueError):
    pass


def checked(condition: bool, message: str) -> None:
    if not condition:
        raise ChainError(message)


def verification_contract(path: Path) -> tuple[dict[str, tuple[str, ...]], set[str], set[str]]:
    """Parse only AST constants; do not import or execute reconstruction code."""
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except (OSError, SyntaxError, UnicodeError) as exc:
        raise ChainError(f'cannot read verification contract: {exc}') from exc
    names: dict[str, tuple[str, ...]] = {}
    steps: dict[str, tuple[str, ...]] = {}
    inventories: dict[str, set[str]] = {}
    for item in tree.body:
        if not isinstance(item, ast.Assign) or len(item.targets) != 1:
            continue
        target = item.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id in ('ASM_CORE', 'PUT_CORE'):
            names[target.id] = tuple(ast.literal_eval(item.value))
        if target.id in ('RUNTIME_MEMBERS', 'EXTENSION_MEMBERS'):
            checked(isinstance(item.value, ast.Call) and len(item.value.args) == 1,
                    f'unsupported {target.id} contract')
            inventories[target.id] = set(ast.literal_eval(item.value.args[0]))
        if target.id == 'EXPECTED_STEPS':
            checked(isinstance(item.value, ast.Dict), 'invalid EXPECTED_STEPS mapping')
            for key, expr in zip(item.value.keys, item.value.values):
                job = ast.literal_eval(key)
                if job not in BUILDER_KEYS:
                    continue
                checked(isinstance(expr, ast.Tuple), f'{job}: unsupported step contract')
                expanded: list[str] = []
                for val in expr.elts:
                    if isinstance(val, ast.Starred) and isinstance(val.value, ast.Name):
                        checked(val.value.id in names, f'{job}: unknown named steps')
                        expanded.extend(names[val.value.id])
                    else:
                        expanded.append(ast.literal_eval(val))
                steps[job] = tuple(expanded)
    checked(set(steps) == set(BUILDER_KEYS), 'expected build-job contracts missing')
    checked(set(inventories) == {'RUNTIME_MEMBERS', 'EXTENSION_MEMBERS'},
            'verified runtime/extension inventory constants absent')
    return steps, inventories['RUNTIME_MEMBERS'], inventories['EXTENSION_MEMBERS']


def source_chain(key: str, member: str) -> tuple[str, ...]:
    if key in ('MR10_OBJ', 'MR10_LOAD'):
        return ('MR10_ASM(ICINT19)',)
    if key == 'EXT_OBJ':
        return (f'EXT_ASM({member})',)
    if member == 'BLIB':
        return ('BOOT_SOURCE(BLIB)',)
    if member == 'COROUTIN':
        return ('BOOT_SOURCE(COROUTIN)', 'BOOT_ASM(COROUTIN)')
    return (f'BOOT_ASM({member})',)


def builder(key: str, member: str) -> str:
    if key in ('MR10_OBJ', 'MR10_LOAD'):
        return 'IC19BLD'
    if key == 'EXT_OBJ':
        return member
    if member == 'BLIB':
        return 'BLIBBLD'
    if member == 'BCPLCO':
        return 'BLDCORCO'
    if member == 'COROUTIN':
        return 'BLDCORLB'
    return 'BLDBMAIN'


def build_plan(manifest: dict[str, Any], dspal: dict[str, Any], root: Path,
               *, verification_path: Path | None = None) -> dict[str, Any]:
    verification_path = verification_path or root / 'tools/reconstruction/verify.py'
    steps, runtime, extensions = verification_contract(verification_path)
    rows = {row['dspal_key']: row for row in manifest['datasets'][2:]}
    checked(set(rows['BOOT_OBJ']['members']) == runtime, 'BOOT_OBJ differs from reconstruction verification contract')
    checked(set(rows['EXT_OBJ']['members']) == extensions, 'EXT_OBJ differs from reconstruction verification contract')
    for key in ('MR10_OBJ', 'MR10_LOAD'):
        checked(rows[key]['members'] == ['ICINT19'], f'{key} unexpected interpreter member')
    records: list[dict[str, Any]] = []
    for key in BINARY_KEYS:
        row = rows[key]
        for member in row['members']:
            job = builder(key, member)
            job_key = BUILDER_KEYS[job]
            mapping = dspal['datasets'][job_key]['members']
            source_path = mapping.get(job)
            checked(validation.safe_git_source(root, source_path), f'{job}: missing/unsafe Git-backed build JCL')
            text = (root / source_path).read_text(encoding='utf-8')
            actual = tuple(STEP.findall(text))
            checked(actual == steps[job], f'{job}: JCL steps differ from reconstruction verification contract')
            refs = source_chain(key, member)
            for ref in refs:
                src_key, src_member = ref.split('(', 1)
                src_member = src_member[:-1]
                checked(src_key in rows and src_member in rows[src_key]['members'],
                        f'{key}({member}): missing selected source {ref}')
            job_on_tape = job in rows[job_key]['members']
            checked(job_on_tape or job == 'BLIBBLD', f'{job}: unselected build JCL without qualification')
            production_steps = steps[job]
            state = 'GIT_BUILD_CONTRACT_ONLY; MVS_AND_RIGHTS_UNVERIFIED'
            records.append({
                'target': f'{key}({member})',
                'selected_source_members': list(refs),
                'build_job': f'{job_key}({job})',
                'build_jcl_path': source_path,
                'build_jcl_on_tape': job_on_tape,
                'reconstruction_step_contract': list(production_steps),
                'requires_generated_assembler': key == 'BOOT_OBJ' and member == 'COROUTIN',
                'requires_absent_compiler_for_bcpl_source_rebuild': key == 'BOOT_OBJ' and member in {'BLIB', 'COROUTIN'},
                'mvs_build_receipt': None,
                'mvs_input_inventory_receipt': None,
                'mvs_binary_readback_receipt': None,
                'candidate_source_sha_verified': False,
                'redistribution_approved': False,
                'status': state,
            })
    checked(len(records) == 15, f'expected 15 selected MVS binary members, found {len(records)}')
    return {'status': 'TA.0 RECONSTRUCTION BUILD PLAN ONLY; NO CANDIDATE OR BINARY ACCEPTANCE',
            'summary': {'binary_members': len(records),
                        'git_build_contracts_traced': len(records),
                        'mvs_receipts_verified': 0,
                        'rights_approvals': 0,
                        'unshipped_build_jobs': sorted({r['build_job'] for r in records if not r['build_jcl_on_tape']}),
                        'bcpl_source_rebuilds_unavailable_without_native_compiler': sum(
                            r['requires_absent_compiler_for_bcpl_source_rebuild'] for r in records)},
            'members': records}


def check_inventory_listing(path: Path, dsn: str, expected: set[str]) -> None:
    """Review only an operator-supplied saved dspal ls listing. Not object readback."""
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeError) as exc:
        raise ChainError(f'{path.name}: cannot read inventory listing: {exc}') from exc
    checked(bool(lines) and lines[0] == f'{dsn}:', f'{path.name}: wrong MVS dataset heading')
    found: set[str] = set()
    for line in lines[1:]:
        match = MEMBER.fullmatch(line)
        checked(match is not None, f'{path.name}: invalid inventory row')
        name = match.group(1)
        checked(name not in found, f'{path.name}: duplicate member {name}')
        found.add(name)
    checked(found == expected,
            f'{path.name}: missing {sorted(expected - found)}, extra {sorted(found - expected)}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--dspal', type=Path, default=DSPAL)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--json', action='store_true', help='show unresolved, per-member MVS build proof plan')
    parser.add_argument('--inventory-dir', type=Path, help='check four saved read-only dspal ls reports')
    parser.add_argument('--strict', action='store_true', help='fail unless binary MVS evidence complete (not yet possible)')
    args = parser.parse_args(argv)
    try:
        manifest, dspal = validation.load(args.manifest), validation.load(args.dspal)
        validation.check(manifest, dspal, args.root)
        plan = build_plan(manifest, dspal, args.root)
        if args.inventory_dir is not None:
            for key in BINARY_KEYS:
                row = next(x for x in manifest['datasets'] if x.get('dspal_key') == key)
                dsn = f"{dspal['mvs']['hlq']}.{dspal['datasets'][key]['dsn']}"
                check_inventory_listing(args.inventory_dir / f'{key}.txt', dsn, set(row['members']))
    except (ChainError, validation.ManifestError, KeyError, OSError) as exc:
        print(f'TA.0 BINARY PROVENANCE FAIL: {exc}', file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        s = plan['summary']
        print(f"TA.0 BUILD-CHAIN MAP: {s['binary_members']} members, "
              f"{s['git_build_contracts_traced']} Git build contracts, "
              f"{s['mvs_receipts_verified']} candidate MVS receipts; "
              f"unshipped: {', '.join(s['unshipped_build_jobs'])}")
        if args.inventory_dir:
            print('4 saved MVS inventory listings matched; binary readback still unverified')
    if args.strict:
        print('TA.0 BINARY PROVENANCE NOT ACCEPTED: no candidate MVS readback/rights evidence', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
