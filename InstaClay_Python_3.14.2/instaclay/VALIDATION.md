# Python 3.14.2 rebuild validation

- Installed dependencies in an isolated CPython 3.14.2 Linux environment.
- Upgraded pandas to 2.3.3 for Python 3.14 support.
- Resolved and downloaded the full dependency set as binary wheels for Windows x64 / CPython 3.14. No source compiler is required for this verified set.
- Retrained all four model candidates and regenerated analysis, model serialization, calibration and metrics using Python 3.14.2.
- Four automated tests passed, covering six dashboard pages, prediction/comparison submissions, empty filters, cleaning, splits, timezone features and predictions.
- Streamlit health endpoint returned HTTP 200 / ok under Python 3.14.2.
- Updated Windows and Unix launchers, bootstrap, Docker image, VS Code configuration and setup documentation.
- Windows startup uses .venv314 and accepts the installed Python 3.14 interpreter through either py or python.
- Dataset bytes and measured Random Forest results are unchanged. This compatibility rebuild does not improve predictive accuracy.
- Native Windows batch execution was not available; runtime tests ran on Linux. Windows package availability was verified separately.

Pandas compatibility reference: https://pandas.pydata.org/pandas-docs/version/2.3.3/whatsnew/v2.3.3.html
