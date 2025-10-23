# els diagnostic data processing (t1-t5)

## repository description

this repository contains an r markdown script (`dx_eu_master_replication.rmd`) created to wrangle, score, and standardize diagnostic data collected by the stanford neurodevelopment, affect, and psychopathology (snap) lab for the longitudinal study of early life stress (els).

these scripts process data from five timepoints (t1-t5) to create composite diagnostic variables based on reports from both adolescent participants and their parents. the primary goal is to generate analysis-ready datasets in both long and wide formats.

## data collection procedures

across the first four timepoints, diagnostic information was collected from both adolescents and their parents.

* **t1, t2, t3, & t4:** diagnostic information was collected using the kiddie schedule for affective disorders and schizophrenia (ksads). *(citation for ksads, e.g., kaufman et al., 1997)*. data were provided in excel (`.xlsx`) format for t1-t3 and csv (`.csv`) format for t4.
* **t5:** diagnostic information was collected from participants using the structured clinical interview for dsm-5 (scid). *(citation for scid, e.g., first et al., 2015)*. data were provided in a pre-processed excel (`.xlsx`) format.

## data processing and variable creation

the `dx_eu_master_replication.rmd` script implements a pipeline that creates composite diagnostic variables based on specific coding rules:

1.  **scoring individual reports (t1-t4 ksads):**
    * first, for the raw ksads data, an individual diagnosis was only considered **'present' (coded as 1)** if the raw score was `4` ("definite").
    * all other scores (e.g., `0`="no info", `1`="not present", `2`="probable", `3`="partial remission", or `na`) were coded as **'absent' (coded as 0)**. `na` values remained `na`.

2.  **creating participant-level diagnoses (t1-t4 ksads):**
    * next, a participant was assigned a final binary (`1`/`0`) diagnosis for a specific disorder (e.g., `dx_gad`) based on a composite "parent or child" rule.
    * a participant was coded as `1` (present) if *either* the parent informant **or** the child informant reported a 'definite' (`4`) score for that disorder.
    * if neither reported a `4`, the participant was coded as `0` (absent). this step generates intermediate files (`ksads_t[1-4]_eu_master.csv`).

3.  **creating diagnostic groups (t1-t5):**
    * the individual binary diagnoses (e.g., `dx_gad`, `dx_sepad`, `dx_smp`) were grouped into broader diagnostic categories (e.g., `anxiety`, `depression`, `adhd`, `substance`) based on a predefined list (`dx_group_list`).
    * a participant was assigned a `1` for a category if they met criteria for *any* of the individual disorders within that group (i.e., a `max()` function was used across the relevant individual diagnoses, handling potential `-inf` results).
    * this logic was applied to the t1-t4 ksads master data and the processed t5 scid data. this step generates intermediate files (`ksads_t[1-4]_dx_groups.csv`).

4.  **compiling and formatting:**
    * the timepoint-specific group files (t1-t4) and the t5 scid data were combined into a single **long-format** dataset (`dx_master_eu_long_format.csv`).
    * this long file was then pivoted into a **wide-format** dataset (`dx_master_eu.csv`).

5.  **creating summary flags:**
    * finally, the wide-format file was processed to add "any diagnosis" flags (`any_dx_t1` through `any_dx_t5`, `any_dx_lifetime`, `dx_any_t1t4`).
    * these flags correctly handle `na` values: a flag is `1` if any diagnosis at that timepoint is 1, `0` if all diagnoses are 0, and `na` if all diagnoses for that timepoint are `na`.
    * this generates the final analysis-ready wide file (`dx_master_eu_with_flags.csv`).

## code overview

the `dx_eu_master_replication.rmd` script is structured as follows:

* **setup:** loads required packages (`tidyverse`, `readxl`, `knitr`, `purrr`).
* **paths:** defines input file paths.
* **groups:** defines the `dx_group_list` for categorizing diagnoses.
* **functions:** defines `process_ksads_timepoint()` and `create_diagnostic_groups()`.
* **processing:** executes the functions for t1-t4, including specific id cleaning for t4.
* **compiling:** reads intermediate files and the t5 file, creating the long-format dataset.
* **formatting:** pivots the long data to create the initial wide-format dataset.
* **flags:** adds the `any_dx` summary flags to the wide data, creating the final wide dataset.
* **appendix:** includes summary chunks to verify counts and calculate conversion rates.

## final output files

this pipeline generates three primary, analysis-ready master files saved in the same directory as the `.rmd` script:

1.  **`dx_master_eu_long_format.csv`**
    * **format:** **long** (one row per participant per timepoint).
    * **content:** includes `els_id`, `timepoint`, and all final binary (`0`/`1`) diagnostic group columns (e.g., `anxiety`, `depression`, `stress`). `na` indicates missing data for that timepoint.

2.  **`dx_master_eu.csv`**
    * **format:** **wide** (one row per participant).
    * **content:** includes `els_id` and all diagnostic groups with a timepoint suffix (e.g., `anxiety_t1`, `depression_t2`). `na` indicates missing data for that timepoint.

3.  **`dx_master_eu_with_flags.csv`**
    * **format:** **wide** (one row per participant).
    * **content:** includes all columns from `dx_master_eu.csv` plus the calculated summary flags (`any_dx_t1`, `any_dx_t2`, `any_dx_t3`, `any_dx_t4`, `any_dx_t5`, `any_dx_lifetime`, `dx_any_t1t4`). `na` indicates missing data.

## appendix: data summaries

the script concludes with an appendix section that generates summary tables directly in the r markdown output:

* **ns per t:** provides counts of available data per timepoint and counts of 'present' (1) and 'absent' (0) diagnoses for each group at each timepoint, correctly handling `na` values.
* **strict conversion counts:** calculates the number of participants considered "healthy" (no diagnosis) through specific baseline periods (t1, t1-t2, t1-t3, t1-t4) who subsequently developed a diagnosis at a later timepoint (t4 or t5).
