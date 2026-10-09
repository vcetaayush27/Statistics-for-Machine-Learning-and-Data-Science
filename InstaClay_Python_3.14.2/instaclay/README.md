# InstaClay — Python 3.14.2 Edition

A complete Statistics for Machine Learning and Data Science project with a light claymorphism Streamlit interface. The target is **likes + comments**, using only post details that can be supplied before publication.

See **WINDOWS_SETUP.md** for VS Code setup and troubleshooting. Run `start_windows.bat` to set up and launch; `retrain_windows.bat` rebuilds models.

## Start on Windows

1. Use **Python 3.14.2** from https://www.python.org/downloads/ (include the Python launcher).
2. Extract the ZIP completely. Do not launch from inside the ZIP preview.
3. Open the `instaclay` folder and double-click **start_windows.bat**.
4. Open http://localhost:8501 if your browser does not open automatically.

The first launch installs dependencies and requires internet access. The app itself works offline. Leave the terminal open; Ctrl+C stops the server. The supplied trained model is ready to use, so retraining is optional.

### Manual PowerShell commands

```powershell
cd "C:\path\to\instaclay"
py -3.14 -m venv .venv314
.\.venv314\Scripts\python.exe -m pip install -r requirements.txt
.\.venv314\Scripts\python.exe -m streamlit run app.py
```

No activation command or PowerShell execution-policy change is required.

### macOS / Linux

Install Python 3.14, then run `bash start_unix.sh` from this folder.

### Docker

```bash
docker build -t instaclay .
docker run --rm -p 8501:8501 instaclay
```

### Optional hosted deployment

Use Python 3.14 and `app.py` as the entrypoint. Include `core.py`, `artifacts/`, `requirements.txt`, and `.streamlit/config.toml`. Raw CSV and training code are needed only for retraining. The interface exposes cleaned-data downloads; remove those buttons and identifying columns before publishing a public demo if that data should not be distributed. No hosting account or deployment is created by this package.

## Features

- Overview: dataset metrics, engagement distribution, content mix.
- Predict a post: caption, hashtags, format, date, time and timezone; point estimate and 80% prediction interval.
- Compare two posts: model preference, absolute difference and an uncertainty-overlap notice; CSV export.
- Statistics: distributions, posting-hour patterns, rank correlations, corrected hypothesis tests and descriptive statistics.
- Model performance: cross-validation, separate test metrics, observed versus predicted chart and permutation importance.
- Data & methods: cleaning audit, excluded inputs, split sizes, limitations and downloads.

## Dataset actually used

The uploaded `instagram_posts.csv` has **1,000 rows and 40 columns**, with one post per account. This package uses this exact uploaded file, not the previously discussed 178,922-row file or merged dataset. A SHA-256 fingerprint is in `artifacts/report.json`.

112 posts have missing likes and are excluded from supervised training; **888 labeled posts** remain. Missing likes are not zero. Genuine large counts are preserved; there is no arbitrary removal of viral posts. Captions are normalized using Unicode NFKC and whitespace cleanup. Missing captions become empty strings, acknowledging that absence cannot be distinguished from collection failure. Hashtags are parsed from caption and serialized list, case-folded and deduplicated. Times are parsed with UTC awareness; planner timezones are converted to UTC using the same feature function. Invalid targets, IDs and timestamps are excluded and audited.

## Model design and honesty

Predictors: caption length, word count, hashtag count, mentions, exclamation/question counts, cyclic hour and weekday, and content type. Caption semantics, sentiment and image content are not modeled. Changing words without changing these structural features can give identical predictions.

Excluded inputs: likes, comments, views, engagement scores, post/user IDs, followers, account post count and account flags. The last three are collection-time values without evidence they were known at publication. This exclusion limits predictive power but respects the requested pre-publication scope.

Comparison: median baseline, Linear Regression, Random Forest and histogram Gradient Boosting. All are trained on log(1 + engagement) because counts are strongly skewed. Estimates are obtained with expm1 and constrained to nonnegative values. This emphasizes multiplicative error and typical engagement rather than estimating an unbiased arithmetic mean for viral posts.

A fixed seeded account-disjoint 60/20/20 split separates training (532), calibration (178) and test (178). Five-fold grouped cross-validation on training data selects hyperparameters and model using log-scale RMSE (RMSLE); learned preprocessing stays inside each fold. No test-driven model selection occurs. Random Forest wins CV; Linear Regression is slightly better on test RMSLE. The test set is deliberately not used to switch winners. The shipped model is the exact evaluated model, not a refit on test data.

The model's **raw test R² is negative**, and its log-scale R² is only about 0.063. This means the file supports a working academic pipeline but **does not support precise engagement predictions**. More algorithm tuning cannot manufacture missing audience information or a consistent measurement window. The interface reports the actual measured performance; it never converts regression error into a fabricated accuracy percentage.

Split-conformal prediction ranges use the absolute log residual on the separate calibration set and the finite-sample 80% quantile. They are individual outcome ranges, not confidence intervals for the mean and not statistical tests of a comparison. Coverage relies on exchangeability and can fail for future distribution shifts. The sample has no fixed observation horizon, so estimates cannot be labeled “seven-day engagement.” Dates spanning 2013–2025 describe historical material, not a representative current Instagram population.

## Statistical analysis

Descriptive statistics and a 2,000-resample bootstrap median interval are exported. Kruskal–Wallis tests compare engagement distributions across content formats, UTC time blocks and weekdays. Holm correction covers these three tests; epsilon-squared gives an effect-size estimate. Spearman correlations across six structural features have a separate Holm correction. Tests describe associations, not causal gains or guaranteed best posting times. No pairwise post-hoc claim is made. Exploratory charts use the full cleaned sample; model tuning uses the designated training split only.

## Reproduce

```powershell
.\.venv314\Scripts\python.exe train.py
.\.venv314\Scripts\python.exe -m unittest discover -s tests -v
```

Retraining overwrites `artifacts/`. Restart Streamlit after retraining to clear cached models. Do not tune repeatedly against the exported test results; a new tuning cycle needs a fresh holdout for an unbiased final assessment. The script expects the same input schema; replacing the data with unrelated CSV columns requires deliberate adaptation.

## Files

- `app.py`: complete light-mode dashboard.
- `core.py`: shared cleaning, feature construction and inference.
- `train.py`: statistical analysis, cross-validation, calibration, evaluation and export.
- `data/instagram_posts.csv`: exact uploaded input.
- `artifacts/model.joblib`: trained pipelines and calibration information.
- `artifacts/*.csv`: cleaned data, split manifest, statistics, scores and predictions.
- `artifacts/report.json`: machine-readable audit, metrics and limitations.
- `RESULTS.md`: readable measured results.
- `tests/test_project.py`: parser, target, leakage, split, prediction and interface tests.
- launchers, Dockerfile and pinned dependencies for deployment.

Only load the supplied model or models you trained yourself: joblib is a Python serialization format and arbitrary third-party files can execute code.

## References

- Scikit-learn leakage and pipelines: https://scikit-learn.org/stable/common_pitfalls.html
- Streamlit testing: https://docs.streamlit.io/develop/concepts/app-testing
- Dataset provenance is supplied by the user's uploaded file. Its exact checksum is recorded; public-source authenticity was not independently certified in this build.
