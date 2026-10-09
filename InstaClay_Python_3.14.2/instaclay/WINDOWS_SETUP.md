# Run InstaClay with Python 3.14.2 on Windows / VS Code

1. Use your installed **64-bit Python 3.14.2**. The launcher detects either `py -3.14` or `python`.
Extract this rebuilt ZIP into a new folder. Do not copy a previous virtual environment. The launcher uses `.venv314`, leaving an older `.venv` alone.

2. Right-click the downloaded ZIP → **Extract All**. Open the extracted `instaclay` folder in VS Code (File → Open Folder).
3. In the VS Code terminal, run:

```powershell
.\start_windows.bat
```

You can also double-click the same file in File Explorer. The launcher creates `.venv314`, installs the pinned packages on first use, checks the model and opens Streamlit. Internet is needed for initial package installation. Subsequent launches reuse the environment. No PowerShell activation or execution-policy changes are needed.

Open **http://localhost:8501** if the browser does not open. Keep the terminal open. Press Ctrl+C to stop (answer Y if Windows asks to terminate the batch job).

## VS Code debugging

After the first successful setup, install VS Code's Python extension. Use **Python: Select Interpreter** → `.venv314\Scripts\python.exe`. Open Run and Debug, select **InstaClay: Streamlit**, and press F5. Do not use Run Python File on `app.py`; Streamlit must launch it.

## Rebuild models

Stop the running app first, then run `.\retrain_windows.bat`. This retrains all candidates, updates statistics and starts the dashboard. A changed source CSV or missing model files also triggers training on startup. Keep the supplied column schema.

## Troubleshooting

- **Python not found:** install Python 3.14, then restart VS Code.
- **Broken/copied environment:** close the app, rename `.venv314` to `.venv314_old`, and rerun the launcher. Virtual environments must be created on your own computer.
- **Package installation failure:** check internet/proxy settings and read the first pip error in the terminal.
- **Port 8501 already in use:** stop the earlier Streamlit process, or run `.\.venv314\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.headless false`.
- **Model files absent or incompatible:** run `.\retrain_windows.bat`.

## Data and results

The bundled CSV contains 1,000 rows and 40 columns. 112 rows have missing likes; 888 are used. The project estimates likes + comments from pre-publication post features. Random Forest is selected by training cross-validation, but its test R² is negative. This is an academic analysis app, and its estimates are not precise predictions of future engagement.
