"""
ELS Diagnostic Variable Creation
=================================
Builds diagnostic category variables from T1-T4 KSADS and T5 SCID data.

Coding:
  T1-T4 (KSADS): 1=not present, 2=probable, 3=partial remission, 4=definite
  T5 (SCID):     0=not present, 1=definite

Outputs
-------
  diagnosis_by_group_wide.csv   — one row per participant, category_T1…T5 columns (0/1/NaN)
  diagnosis_ever.csv            — ever-diagnosed per category across T1–T5
  incident_sample.csv           — incident design: healthy T1-T3, outcome at T4/T5
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths (edit to match your directory) ──────────────────────────────────────
DATA_DIR = Path.home() / "Library/CloudStorage/OneDrive-Stanford/Research Projects/1 - Data/ELS/diagnoses/diagnostic data"
OUT_DIR  = Path(".")   # outputs saved alongside this script

# ── Diagnostic category mapping (T1-T4 column prefixes) ───────────────────────
# OCD folded into anxiety; ADHD excluded from primary outcomes
CATEGORY_MAP = {
    "depression":    ["mde_curr", "dys", "ddnos"],
    "anxiety":       ["gad", "panicd", "agor", "sop", "sepad", "smp", "ocd"],
    "stress":        ["ptsd", "acutesd"],
    "bipolar":       ["bp1", "bp2", "bpn", "hypo", "mania", "cyc"],
    "schizophrenia": ["psyc", "brp"],
    "substance":     ["alcho_a", "sub_a"],
    "eating":        ["anor", "bul"],
    "disruptive":    ["con", "odd"],
}

CATEGORIES  = list(CATEGORY_MAP.keys())
TIMEPOINTS  = ["T1", "T2", "T3", "T4", "T5"]

# ── Load T1-T4 ────────────────────────────────────────────────────────────────
t14 = pd.read_csv(DATA_DIR / "t1-t4 diagnostic data.csv", na_values=["NA"])
t14["ELS_ID"] = t14["els_id"].apply(lambda x: f"ELS{int(x):03d}")
print(f"T1-T4 data: {len(t14)} participants, {len(t14.columns)} columns")

# ── Build category flags for T1-T4 ───────────────────────────────────────────
# Flag = 1 if any constituent diagnosis == 4 (definite) at that timepoint
# Flag = 0 if data available and no definite diagnosis
# Flag = NaN if all constituent columns are missing at that timepoint
rows = []
for _, row in t14.iterrows():
    rec = {"ELS_ID": row["ELS_ID"]}
    for t in ["T1", "T2", "T3", "T4"]:
        for cat, prefixes in CATEGORY_MAP.items():
            cols = [c for c in t14.columns
                    if c.endswith(f"_{t}") and any(c.startswith(p + "_") for p in prefixes)]
            if not cols:
                rec[f"{cat}_{t}"] = np.nan
                continue
            vals = [row[c] for c in cols if not pd.isna(row[c])]
            if not vals:
                rec[f"{cat}_{t}"] = np.nan
            else:
                rec[f"{cat}_{t}"] = int(any(v == 4 for v in vals))
    rows.append(rec)

df14 = pd.DataFrame(rows)

# ── Load T5 ───────────────────────────────────────────────────────────────────
t5 = pd.read_excel(DATA_DIR / "t5 diagnostic data.xlsx")
t5["ELS_ID"] = t5["ELS_ID"].apply(lambda x: f"ELS{int(x):03d}")
print(f"T5 data:    {len(t5)} participants")

# Rename T5 columns to cat_T5 format; T5 coded 0/1
t5_rename = {c: f"{c}_T5" for c in t5.columns if c != "ELS_ID"}
t5 = t5.rename(columns=t5_rename)

# Add missing categories (e.g. disruptive not assessed at T5)
for cat in CATEGORIES:
    if f"{cat}_T5" not in t5.columns:
        t5[f"{cat}_T5"] = np.nan

# ── Merge T1-T4 with T5 ───────────────────────────────────────────────────────
t5_cols = ["ELS_ID"] + [f"{cat}_T5" for cat in CATEGORIES]
wide = df14.merge(t5[t5_cols], on="ELS_ID", how="outer")
wide = wide.sort_values("ELS_ID").reset_index(drop=True)
print(f"Combined:   {len(wide)} participants")

# ── Ever-diagnosed per category ───────────────────────────────────────────────
for cat in CATEGORIES:
    cols = [f"{cat}_{t}" for t in TIMEPOINTS if f"{cat}_{t}" in wide.columns]
    wide[f"{cat}_ever"] = (wide[cols] == 1).any(axis=1).astype(int)
    wide.loc[wide[cols].isna().all(axis=1), f"{cat}_ever"] = np.nan

# Any ever diagnosed
ever_cols = [f"{cat}_ever" for cat in CATEGORIES]
wide["any_ever"] = (wide[ever_cols] == 1).any(axis=1).astype(int)

# ── Save wide + ever files ─────────────────────────────────────────────────────
wide.to_csv(OUT_DIR / "diagnosis_by_group_wide.csv", index=False)

ever = wide[["ELS_ID"] + ever_cols + ["any_ever"]].copy()
ever.to_csv(OUT_DIR / "diagnosis_ever.csv", index=False)

# ── Incident Diagnosis Sample ─────────────────────────────────────────────────
# Healthy at T1, T2, T3: all category flags = 0 (no diagnosis, no subthreshold)
# Subthreshold at T1-T3: any constituent value is 2 or 3 → excluded
# Outcome at T4/T5: any category flag = 1 → incident case; all = 0 → control

def t14_subthreshold(row, timepoint):
    """True if any KSADS item is 2 or 3 (subthreshold) at given timepoint."""
    cols = [c for c in t14.columns if c.endswith(f"_{timepoint}")]
    vals = [row[c] for c in cols if not pd.isna(row.get(c))]
    return any(v in (2, 3) for v in vals)

def t14_diagnosed(row, timepoint):
    """True if any KSADS item == 4 at given timepoint."""
    cols = [c for c in t14.columns if c.endswith(f"_{timepoint}")]
    vals = [row[c] for c in cols if not pd.isna(row.get(c))]
    return any(v == 4 for v in vals)

def t14_has_data(row, timepoint):
    """True if at least one KSADS item is non-missing at given timepoint."""
    cols = [c for c in t14.columns if c.endswith(f"_{timepoint}")]
    return any(not pd.isna(row.get(c)) for c in cols)

# Step 1: healthy (not diagnosed, not subthreshold) at T1, T2, T3
t14_indexed = t14.set_index("ELS_ID")
incident_rows = []

for _, row_wide in wide.iterrows():
    eid = row_wide["ELS_ID"]
    rec = {"ELS_ID": eid}

    if eid not in t14_indexed.index:
        continue
    row_t14 = t14_indexed.loc[eid]

    # Must have data at T1-T3 and be clean (no 2,3,4)
    healthy_t123 = True
    for t in ["T1", "T2", "T3"]:
        if not t14_has_data(row_t14, t):
            healthy_t123 = False
            break
        if t14_subthreshold(row_t14, t) or t14_diagnosed(row_t14, t):
            healthy_t123 = False
            break

    rec["healthy_t123"] = healthy_t123
    if not healthy_t123:
        incident_rows.append(rec)
        continue

    # Step 2: classify at T4/T5
    # T4 subthreshold → exclude
    t4_sub  = t14_subthreshold(row_t14, "T4") if t14_has_data(row_t14, "T4") else False
    t4_diag = t14_diagnosed(row_t14, "T4")    if t14_has_data(row_t14, "T4") else False
    t4_data = t14_has_data(row_t14, "T4")

    # T5 (0/1 coded)
    t5_cat_cols = [f"{cat}_T5" for cat in CATEGORIES if f"{cat}_T5" in row_wide.index]
    t5_vals = [row_wide[c] for c in t5_cat_cols if not pd.isna(row_wide[c])]
    t5_diag = any(v == 1 for v in t5_vals) if t5_vals else None
    t5_data = bool(t5_vals)

    # Outcome: diagnosed at T4 OR T5
    if t4_sub:
        outcome = np.nan  # exclude
    elif t4_diag or t5_diag:
        outcome = 1  # incident case
    elif (t4_data and not t4_diag) or (t5_data and not t5_diag):
        outcome = 0  # healthy control at follow-up
    else:
        outcome = np.nan  # no follow-up data

    rec["incident_outcome"] = outcome

    # Per-category breakdown at T4/T5
    for cat in CATEGORIES:
        t4_flag = row_wide.get(f"{cat}_T4", np.nan)
        t5_flag = row_wide.get(f"{cat}_T5", np.nan)
        flags = [v for v in [t4_flag, t5_flag] if not pd.isna(v)]
        rec[f"{cat}_incident"] = int(any(v == 1 for v in flags)) if flags else np.nan

    incident_rows.append(rec)

incident = pd.DataFrame(incident_rows)
incident_clean = incident[incident["healthy_t123"]].copy()
incident_clean = incident_clean[incident_clean["incident_outcome"].notna()].copy()
incident_clean.to_csv(OUT_DIR / "incident_sample.csv", index=False)

# ── Summary ────────────────────────────────────────────────────────────────────
print("\n── Diagnosis prevalence by category and timepoint (n definite) ──")
header = f"{'Category':14s}" + "".join(f"  {t:>4s}" for t in TIMEPOINTS) + "  EVER"
print(header)
print("-" * len(header))
for cat in CATEGORIES:
    row_str = f"{cat:14s}"
    for t in TIMEPOINTS:
        col = f"{cat}_{t}"
        if col in wide.columns:
            n = int((wide[col] == 1).sum())
            row_str += f"  {n:>3d}"
        else:
            row_str += "   --"
    n_ever = int((wide[f"{cat}_ever"] == 1).sum())
    row_str += f"  {n_ever:>3d}"
    print(row_str)

print("\n── Incident sample ──")
n_healthy_t123 = incident["healthy_t123"].sum()
n_valid = incident_clean["incident_outcome"].notna().sum()
n_cases = int((incident_clean["incident_outcome"] == 1).sum())
n_controls = int((incident_clean["incident_outcome"] == 0).sum())
print(f"  Healthy at T1-T3:           {n_healthy_t123}")
print(f"  Valid follow-up (T4 or T5): {n_valid}")
print(f"  Incident cases:             {n_cases}")
print(f"  Healthy controls:           {n_controls}")
print(f"\nOutputs saved to: {OUT_DIR.resolve()}")
