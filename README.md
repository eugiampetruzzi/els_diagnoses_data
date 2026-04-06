# els_diagnoses_data

Analysis of psychiatric diagnoses from the Stanford Neurodevelopment, Affect, and Psychopathology (SNAP) Lab's Early Life Stress (ELS) study. Data available upon request — contact eugiampe@stanford.edu.

---

## Files

- **`els_diagnoses.py`** — builds diagnostic category variables and incident diagnosis sample
- **`flowchart_els_diagnoses.png`** — participant flowchart for incident sample

### Outputs

| File | Description | N |
|------|-------------|---|
| `diagnosis_by_group_wide.csv` | Category flags (0/1/NaN) at T1–T5, one row per participant | 225 |
| `diagnosis_ever.csv` | Ever-diagnosed per category across T1–T5 | 225 |
| `incident_sample.csv` | Incident design: healthy T1-T3, classified at T4/T5 | ~87 |

---

## Methods

Structured clinical interviews were conducted at all timepoints to assess psychiatric diagnoses.

- **T1–T4 (ages ≤18):** Schedule for Affective Disorders and Schizophrenia for School-Age Children — Present and Lifetime Version (K-SADS-PL; Kaufman et al., 1997). Coded 1–4.
- **T5 (ages ≥19):** Structured Clinical Interview for DSM-5 (SCID-5; First et al., 2015). Coded 0/1.

### Coding Scheme

| Rating | T1–T4 (KSADS) | T5 (SCID) |
|--------|---------------|-----------|
| 0 | — | not present |
| 1 | not present | definite |
| 2 | probable | — |
| 3 | partial remission | — |
| 4 | definite | — |

A category flag of **1** at T1–T4 requires at least one constituent diagnosis coded **4 = definite**. T5 flags are taken directly from the pre-aggregated SCID output.

---

## Diagnostic Categories

OCD is folded into anxiety. ADHD is excluded from primary outcomes.

| Category | T1–T4 Diagnoses Included |
|----------|--------------------------|
| depression | MDE (current), dysthymia, DDNOS |
| anxiety | GAD, panic disorder, agoraphobia, social phobia, separation anxiety, specific phobia, **OCD** |
| stress | PTSD, acute stress disorder |
| bipolar | BP-I, BP-II, BP-NOS, hypomania, mania, cyclothymia |
| schizophrenia | psychosis, brief reactive psychosis |
| substance | alcohol use disorder, substance use disorder |
| eating | anorexia, bulimia |
| disruptive | conduct disorder, ODD |

---

## Incident Diagnosis Sample

The full cohort (n ≈ 224) completed K-SADS at baseline. To identify first-onset disorders in early adulthood:

1. **Healthy at T1–T3:** complete K-SADS data with all items coded 1 (not present). Participants with any rating of 2 or 3 (subthreshold/remission) were excluded.
2. **Classification at T4/T5:** incident cases received a definite diagnosis (rating = 4 at T4, or 1 at T5). Healthy controls had no diagnosis at T4 or T5. Subthreshold ratings at T4 were excluded.

Final analytic sample: **n ≈ 87** (incident cases n ≈ 40, healthy controls n ≈ 47).

See `flowchart_els_diagnoses.png` for the full selection flowchart.

### Inter-rater Reliability

Twenty interviews (5 per timepoint) were re-scored blind by a second trained rater.
- 95–100% raw agreement across all diagnoses
- Gwet's AC1 = 0.73 for absent vs. present classification
