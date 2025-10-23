# els diagnostic data processing (t1-t5)

## repository description

this repository contains an r markdown script (`dx_eu_master_replication.rmd`) created to wrangle, score, and standardize diagnostic data collected by the stanford neurodevelopment, affect, and psychopathology (snap) lab for the longitudinal study of early life stress (els).

this script processes data from five timepoints (t1-t5) to create composite diagnostic variables based on reports from both adolescent participants and their parents. the primary goal is to generate analysis-ready datasets in both long and wide formats, saved to a specified output directory.

## data collection procedures

across the first four timepoints, diagnostic information was collected using semi-structured interviews with both adolescents and their parents. at the fifth timepoint, participants completed a self-report structured interview.

* **t1, t2, t3, & t4:** diagnostic information was collected using the kiddie schedule for affective disorders and schizophrenia (ksads) administered to both parent and child informants. *(citation: kaufman, j., birmaher, b., brent, d., rao, u., flynn, c., moreci, p., ... & ryan, n. (1997). schedule for affective disorders and schizophrenia for school-age children-present and lifetime version (k-sads-pl): initial reliability and validity data. journal of the american academy of child & adolescent psychiatry, 36(7), 980-988.)*. data were provided in excel (`.xlsx`) format for t1-t3 and csv (`.csv`) format for t4.
* **t5:** diagnostic information was collected from participants using the structured clinical interview for dsm-5 (scid). *(citation: first, m. b., williams, j. b., karg, r. s., & spitzer, r. l. (2015). structured clinical interview for dsm-5—research version (scid-5-rv). american psychiatric association.)*. data were provided in a pre-processed excel (`.xlsx`) format summarizing diagnoses.

## data processing and variable creation

the `dx_eu_master_replication.rmd` script implements a pipeline that creates composite diagnostic variables based on specific coding rules:

1.  **scoring individual reports (t1-t4 ksads):**
    * first, for the raw ksads data, an individual diagnosis was only considered **'present' (coded as 1)** if the raw interview score was `4` ("definite").
    * all other scores (e.g., `0`="no info", `1`="not present", `2`="probable", `3`="partial remission") were coded as **'absent' (coded as 0)**. missing raw scores (`na`) remained `na`.

2.  **creating participant-level diagnoses (t1-t4 ksads):**
    * next, a participant was assigned a final binary (`1`/`0`) diagnosis for a specific disorder (e.g., `dx_gad`) based on a composite "parent or child" rule.
    * a participant was coded as `1` (present) if *either* the parent informant **or** the child informant reported a 'definite' (`4`) score for that disorder.
    * if neither reported a `4`, the participant was coded as `0` (absent). this step generates intermediate files (`ksads_t[1-4]_eu_master.csv`) saved to the specified output directory.

3.  **creating diagnostic groups (t1-t5):**
    * the individual binary diagnoses (e.g., `dx_gad`, `dx_sepad`, `dx_smp`) were grouped into broader diagnostic categories (e.g., `anxiety`, `depression`, `adhd`, `substance`) based on a predefined list (`dx_group_list`).
    * a participant was assigned a `1` for a category if they met criteria for *any* of the individual disorders within that group (i.e., a `max(..., na.rm = true)` function was used across the relevant individual diagnoses, handling potential `-inf` results for rows with only `na`s by converting them back to `0`).
    * this logic was applied to the t1-t4 ksads master data and the processed t5 scid data. this step generates intermediate files (`ksads_t[1-4]_dx_groups.csv`) saved to the specified output directory.

4.  **compiling and formatting:**
    * the timepoint-specific group files (t1-t4) and the t5 scid data were combined into a single **long-format** dataset (`dx_master_eu_long_format.csv`), saved to the output directory.
    * this long file was then pivoted into a **wide-format** dataset (`dx_master_eu.csv`), handling potential duplicate participant-timepoint entries by taking the maximum value and ensuring `na` propagation. this file is saved to the output directory.

5.  **creating summary flags:**
    * finally, the wide-format file was processed to add "any diagnosis" flags (`any_dx_t1` through `any_dx_t5`, `any_dx_lifetime`, `dx_any_t1t4`).
    * these flags correctly handle `na` values using a custom `max_or_na` function: a flag is `1` if any constituent diagnosis at that timepoint is 1, `0` if all constituent diagnoses are 0, and `na` if all constituent diagnoses for that timepoint are `na`.
    * this generates the final analysis-ready wide file (`dx_master_eu_with_flags.csv`), saved to the output directory.

## code overview

the `dx_eu_master_replication.rmd` script is structured as follows:

* **setup:** loads required packages (`tidyverse`, `readxl`, `knitr`, `purrr`) and sets chunk options.
* **paths:** defines input file paths and the primary output directory path.
* **groups:** defines the `dx_group_list` for categorizing diagnoses.
* **functions:** defines `process_ksads_timepoint()` and `create_diagnostic_groups()`.
* **processing:** executes the functions for t1-t4, including specific id cleaning for t4. intermediate files are saved to the output directory.
* **compiling:** reads intermediate files and the t5 file, creating the long-format dataset (`dx_master_eu_long_format.csv`) in the output directory.
* **formatting:** pivots the long data to create the initial wide-format dataset (`dx_master_eu.csv`) in the output directory.
* **flags:** adds the `any_dx` summary flags to the wide data, creating the final wide dataset (`dx_master_eu_with_flags.csv`) in the output directory.
* **appendix:** includes summary chunks that load the final output files to verify counts and calculate conversion rates directly within the r markdown output visual.

## final output files

this pipeline generates three primary, analysis-ready master files saved to the specified `output_path` directory:

1.  **`dx_master_eu_long_format.csv`**
    * **format:** **long** (one row per participant per timepoint).
    * **content:** includes `els_id`, `timepoint`, and all final binary (`0`/`1`) diagnostic group columns (e.g., `anxiety`, `depression`, `stress`). `na` indicates missing data for that participant at that timepoint.

2.  **`dx_master_eu.csv`**
    * **format:** **wide** (one row per participant).
    * **content:** includes `els_id` and all diagnostic groups with a timepoint suffix (e.g., `anxiety_t1`, `depression_t2`). `na` indicates missing data for that participant at that timepoint.

3.  **`dx_master_eu_with_flags.csv`**
    * **format:** **wide** (one row per participant).
    * **content:** includes all columns from `dx_master_eu.csv` plus the calculated summary flags (`any_dx_t1`, `any_dx_t2`, `any_dx_t3`, `any_dx_t4`, `any_dx_t5`, `any_dx_lifetime`, `dx_any_t1t4`). `na` indicates missing data.

## appendix: data summaries

the script concludes with an appendix section that loads the final output files and generates summary tables directly in the r markdown output visual:

* **ns per t:** provides counts of available data per timepoint and counts of 'present' (1) and 'absent' (0) diagnoses for each group at each timepoint, correctly handling `na` values.
* **strict conversion counts:** calculates the number of participants considered "healthy" (no diagnosis = 0) through specific baseline periods (t1, t1-t2, t1-t3, t1-t4) who subsequently developed a diagnosis (= 1) at a later timepoint (t4 or t5). calculations correctly propagate `na` values (i.e., conversion status is `na` if baseline or outcome status is `na`).
* **sample: incidence (t1-t3 healthy, t4 or t5 diagnosis):** defines a specific analytic sample comprising participants who were healthy (no diagnosis) through t3 and had follow-up data available at either t4 or t5. within this sample, it calculates the incidence rate (proportion developing a diagnosis at t4 or t5) and provides descriptive statistics (sex, race) comparing the "incidence group" (converters) to the "stable healthy group" (non-converters).
