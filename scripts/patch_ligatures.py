#!/usr/bin/env python3
"""Disable the 'www' ligature in Smile Nerd Font Mono."""

import argparse
import logging
from pathlib import Path

from fontTools.ttLib import TTFont

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def find_www_single_subst_lookups(gsub):
    """Find SingleSubst lookup indices that map 'w' to www-related glyphs."""
    www_lookup_indices = {}  # index -> target glyph name
    for i, lookup in enumerate(gsub.LookupList.Lookup):
        if lookup.LookupType != 1:
            continue
        for sub in lookup.SubTable:
            if not hasattr(sub, "mapping"):
                continue
            if "w" in sub.mapping:
                target = sub.mapping["w"]
                if target in ("w_w_w.liga", "w.spacer"):
                    www_lookup_indices[i] = target
    return www_lookup_indices


def find_www_chain_rules(gsub, www_lookup_indices):
    """Find ChainContextSubst rules that reference www-related lookups."""
    results = []  # (lookup_idx, sub_idx, ruleset_idx, rule_idx)
    for i, lookup in enumerate(gsub.LookupList.Lookup):
        if lookup.LookupType != 6:
            continue
        for j, sub in enumerate(lookup.SubTable):
            if sub.Format != 1:
                continue
            if not hasattr(sub, "ChainSubRuleSet") or not sub.ChainSubRuleSet:
                continue
            for rsi, rs in enumerate(sub.ChainSubRuleSet):
                if not rs:
                    continue
                for ri, rule in enumerate(rs.ChainSubRule):
                    if not rule.SubstLookupRecord:
                        continue
                    for rec in rule.SubstLookupRecord:
                        if rec.LookupListIndex in www_lookup_indices:
                            results.append((i, j, rsi, ri, rec.LookupListIndex))
    return results


def patch_www_ligature(font_path: str):
    """Disable www ligature in the given font file (in-place)."""
    log.info("Loading font: %s", font_path)
    font = TTFont(font_path)
    gsub = font["GSUB"].table

    # Step 1: Find the SingleSubst lookups for www
    www_lookups = find_www_single_subst_lookups(gsub)
    if not www_lookups:
        log.warning("No www-related SingleSubst lookups found, nothing to patch")
        return

    log.info("Found www SingleSubst lookups: %s", {k: v for k, v in www_lookups.items()})

    # Step 2: Find chain rules referencing these lookups
    chain_rules = find_www_chain_rules(gsub, www_lookups)
    log.info("Found %d chain rules referencing www lookups", len(chain_rules))

    # Step 3: Remove SubstLookupRecords from chain rules
    patched_chains = set()
    for lookup_idx, sub_idx, rsi, ri, ref_lookup in chain_rules:
        rule = gsub.LookupList.Lookup[lookup_idx].SubTable[sub_idx].ChainSubRuleSet[rsi].ChainSubRule[ri]
        # Remove records that reference www lookups
        rule.SubstLookupRecord = [
            rec for rec in rule.SubstLookupRecord
            if rec.LookupListIndex not in www_lookups
        ]
        rule.SubstCount = len(rule.SubstLookupRecord)
        patched_chains.add((lookup_idx, sub_idx, rsi, ri))

    log.info("Patched %d chain rules (removed SubstLookupRecords)", len(patched_chains))

    # Step 4: Change SingleSubst mappings to self-map (w -> w)
    for idx in www_lookups:
        lookup = gsub.LookupList.Lookup[idx]
        for sub in lookup.SubTable:
            if hasattr(sub, "mapping") and "w" in sub.mapping:
                old_target = sub.mapping["w"]
                sub.mapping["w"] = "w"
                log.info("Lookup %d: changed w -> %s to w -> w", idx, old_target)

    log.info("Saving patched font: %s", font_path)
    font.save(font_path)
    log.info("Done")


def main():
    parser = argparse.ArgumentParser(description="Disable www ligature in font")
    parser.add_argument("font", help="Path to TTF font file to patch (modified in-place)")
    args = parser.parse_args()

    if not Path(args.font).exists():
        log.error("Font file not found: %s", args.font)
        raise SystemExit(1)

    patch_www_ligature(args.font)


if __name__ == "__main__":
    main()
