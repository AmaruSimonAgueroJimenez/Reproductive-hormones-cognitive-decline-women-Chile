# Neurodegeneration and reproductive health in Chile

The [research website](https://amarusimonaguerojimenez.github.io/Reproductive-hormones-cognitive-decline-women-Chile/) provides an English index linking three full reports and both presentations.

## Full methods, results and extended analyses

- [Part I: descriptive evidence](docs/descriptive_methods_results.html): recorded dementia and neurodegenerative disease across mortality, hospital and primary-care sources, with the extended figure and table bank and the new functional and dementia instrument analyses.
- [Part II: connected analyses](docs/reproductive_life_course.html): reproductive history, ovarian surgery and menopause-care context, including the survey, surgery and care extensions and the new REM instrument context.
- [Administrative extension](docs/access_diagnostic_recording_extension.html): REM, DEIS and GRD care and diagnostic recording, with source-completeness checks, geographic analyses, association sensitivities and the new dementia reassessment and caregiver measures.

All three reports were extended on 30 October 2026 with a shared REM instrument account covering functional status, fall risk, dementia programme reassessment and caregiver measures. The original analyses retain their reviewed 28 and 29 October definitions and observation windows. The new instrument sections document annual field harmonisation, reporting eligibility, missing values, duplicate handling and the unresolved 2021 reassessment anomaly. They do not establish individual cognitive trajectories or individual hormonal effects. The adjacent comorbidity prevalence bars added on 30 October preserve the original network analyses. Administrative facility associations remain exploratory and sensitive to denominators and programme intensity.

The shared instrument extension adds six panel figures and 16 tables to each report. These are the same new results reproduced in the three scientific contexts, rather than three independent sets of observations.

## Presentations

- [Combined presentation of both parts: 46 slides](docs/combined_project_key_results_slides.html).
- [Part II key results: 18 slides](docs/reproductive_key_results_slides.html).

Arrow keys navigate between slides. **F** opens fullscreen and **O** opens the overview. Complete original figures and institutional source references remain linked from the slides. PowerPoint files stay outside this public repository through case-insensitive `.gitignore` rules.

## Figures, tables and documents

Each full report links its reviewed line-numbered Word document and its original vector figures. The descriptive report includes its complete Word figure/table bank and figure/table asset archive. The administrative extension retains its existing reconstruction archive and 26 original source tables. The three reports also share the new instrument tables, panel figures and [instrument reconstruction package](outputs/rem_neuro_instruments_2026-10-30/REM_Instrument_Assets_EN.zip). All previously published scientific PNGs preserve their exact bytes; the new instrument figures are separately identified.

The public HTML copies use relative links to the original PNG files, so a figure is downloaded once and reused. Report navigation has been added, and the unavailable PowerPoint download anchor has been removed from the public Part II HTML. The delivery preparation step preserves the reviewed analytical values, scientific prose, tables, figure scales, crops, folded code and report runtime. Quarto sources are retained exactly; the downloadable `*_source.txt` copies are byte-identical to the QMD files.

## Reproducibility and verification

From a downloaded copy of the repository, verify the delivered pages, every local link, the original figures, numerical table structure and complete file manifest with Python 3.10 or newer:

```sh
python3 scripts/prepare_site.py --check
```

`python3 scripts/prepare_site.py` prepares the online delivery of the recorded HTML snapshots and refreshes the delivery manifest. It is idempotent and permits only the documented publishing changes. The script uses the Python standard library.

The QMD and folded report code make the analysis specifications inspectable. Rebuilding the complete original reports requires the parent analytical project, software and the inputs specified for each component; the website files alone do not reconstruct every earlier analysis. The new [REM instrument package](outputs/rem_neuro_instruments_2026-10-30/REM_Instrument_Assets_EN.zip) documents aggregate-only reproduction of the new instrument tables and figures, not standalone reconstruction of all three complete reports. The administrative report retains its separately documented [public reconstruction package](outputs/access_diagnostic_extension_2026-10-29/Access_Diagnostic_Recording_Assets_EN.zip), including public aggregate inputs, analysis sources, environment pins and rebuild instructions. Original-record refresh requires the authorised external releases and upstream preparation. Public metadata uses relative project paths and `EXTERNAL_DATA_ROOT` labels.

`publication_manifest.json` and `site_provenance.json` record file integrity and the relationship to the reviewed snapshots. They are technical provenance records; scientific references point to [DEIS](https://deis.minsal.cl/#datosabiertos), [FONASA](https://datosabiertos.fonasa.cl/dimensiones-financiamientos/), [INE](https://www.ine.gob.cl/estadisticas-por-tema/demografia-y-poblacion/estimaciones-y-proyecciones-de-poblacion) and the other original institutions cited in the reports.

No individual-level records are included in this repository. The public site retains the distinct observation units, measurement limits and analysis populations described in each report.
