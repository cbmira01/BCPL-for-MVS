"""TA.0: exact historical IEBPTPCH decoded-member receipt compatibility.

The pre-pagination decoder did not emit ``repeated_page_headings``.  The
page-aware decoder adds that *one* field.  Old receipts may be accepted only
when fresh decoding demonstrates zero repeated headings and every other
saved metadata field agrees exactly.  Source/JES/hash/FB80 evidence checks
remain the responsibility of the calling reconciler.
"""
from __future__ import annotations


def metadata_schema(saved: object, current: object) -> str | None:
    """Return the exact accepted schema variant; None for all other mismatches.

    No saved data is modified or upgraded. In particular, a legacy receipt
    cannot obscure any observed page continuation, altered record metadata,
    newly absent field, or extra field.
    """
    if type(saved) is not dict or type(current) is not dict:
        return None
    repeats = current.get('repeated_page_headings')
    if type(repeats) is not int or repeats < 0:
        return None
    if saved == current:
        return 'PAGE_AWARE_V2'
    if 'repeated_page_headings' not in saved and repeats == 0:
        before_pagination = {key: value for key, value in current.items()
                             if key != 'repeated_page_headings'}
        if saved == before_pagination:
            return 'PRE_PAGE_V1'
    return None
