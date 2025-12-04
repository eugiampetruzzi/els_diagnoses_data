# els_diagnoses_data

## project overview
This repository contains data and analysis scripts regarding the onset of psychiatric disorders in early adulthood. The study tracks a longitudinal cohort to identify "incident diagnoses"—participants who were healthy through mid-adolescence but developed a psychiatric disorder in early adulthood.

## files

### data files
* **t1-t4 diagnostic data.csv**: current diagnosis at timepoints 1 through 4. coded as `1` (diagnosis) or `0` (no diagnosis). these represent actual KSADS variables (ungrouped).
* **t5 diagnostic data.xlsx**: current diagnosis at timepoint 5. coded as `1` (diagnosis) or `0` (no diagnosis). these are grouped according to the major disorder categories described below.
* **incidence_subsample.csv**: demographic and ED data for the final analytic sample (healthy T1-T3 who received a diagnosis at T4 or T5). note: diagnosis labels must be merged from the T1-T5 files.

### analysis
* **analysis.Rmd**: r markdown file containing the data cleaning, merging, and statistical analysis code.

## methodology

### clinical interviews
Structured clinical interviews were conducted at four timepoints. Interviews were conducted by trained assessors under the supervision of a clinician.

* **ages $\le 18$**: Schedule for Affective Disorders and Schizophrenia for School-Age Children: Present and Lifetime Version (K-SADS-PL; Kaufman et al., 1997). Evaluates current/lifetime DSM-IV and DSM-5 disorders.
* **ages $\ge 19$**: Structured Clinical Interview for DSM-5 (SCID-5; First et al., 2015). Assesses current/lifetime psychiatric disorders.

### diagnostic coding scheme
Both interviews utilized a standardized coding scheme:

| code | definition | note |
| :--- | :--- | :--- |
| **0** | no information | |
| **1** | not present | |
| **2** | probable | excluded from analysis |
| **3** | partial remission | excluded from analysis |
| **4** | definite | classified as case |

### inter-rater reliability
Five audio-recorded interviews were randomly selected from each timepoint (20 total) for blind scoring.
* **raw agreement**: 95-100%
* **gwet’s ac1**: 0.73 (for dichotomous classification of absent [1] vs present [4])

## study sample definition

The study focuses on diagnoses assessed consistently across all timepoints: depressive disorders, anxiety disorders (OCD, trauma-related), bipolar/related, schizophrenia spectrum, substance use, eating disorders, and disruptive disorders.

### incident diagnosis logic
The full cohort (N=224) was filtered to create the final analytic sample (N=87) based on the following criteria:

1.  **healthy baseline (t1-t3)**:
    * participants with complete K-SADS data at T1, T2, and T3.
    * all current diagnoses coded as **1 = not present**.
    * *exclusion*: any rating of 2 (probable) or 3 (partial remission).
    * *result*: N=106 (47.3% of full sample).

2.  **diagnostic classification (t4-t5)**:
    * of the 106 healthy baseline participants, 88 had valid data at the final assessment.
    * **incident cases (N=40)**: received a rating of **4 = definite** for any psychiatric diagnosis. this indicates first onset between mid-adolescence and early adulthood.
    * **healthy controls (N=47)**: maintained ratings of **1 = not present** across all timepoints.
    * *exclusion*: one participant with subthreshold symptoms (2 = probable).

This classification isolates pre-morbid variability and avoids confounding with concurrent psychiatric diagnoses, distinguishing between early-onset (neurodevelopmental/familial) and later-onset (regulatory system maturation) etiologies.
