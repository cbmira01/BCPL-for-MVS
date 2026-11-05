"""Frozen test fixture: the 29 managed names at Git 96657fd (5 November 2026)."""
# Snapshot used only by offline tests as the 5 November 2026 baseline.
# Production inventory authority comes from tracked config/dspal.yaml.
REQUIRED_LOGICAL = frozenset((
    'MR10_SOURCE', 'MR10_ASM', 'MR10_JCL', 'MR10_LIBRARY',
    'MR10_BCPLDEMO', 'MR10_LANGDEMO', 'MR10_TESTS', 'MR10_OBJ', 'MR10_LOAD',
    'CAMB_SOURCE', 'CAMB_ASM', 'CAMB_JCL', 'CAMB_LIBRARY', 'CAMB_BCPLDEMO',
    'CAMB_LANGDEMO', 'CAMB_TESTS', 'CAMB_OBJ', 'CAMB_LOAD',
    'BOOT_SOURCE', 'BOOT_INTCODE', 'BOOT_ASM', 'BOOT_JCL', 'BOOT_OBJ',
    'BOOT_DEVOBJ', 'EXT_OBJ', 'EXT_MAC', 'EXT_ASM', 'EXT_SOURCE', 'DIST_DOCS',
))
