"""Set up the isolated environment and launch the local Streamlit app."""
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def run(args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)

def main():
    os.chdir(ROOT)
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Use Python 3.14 for the supplied model and pinned dependencies.")
    if sys.prefix == sys.base_prefix:
        raise RuntimeError("Run start_windows.bat or use the project's .venv314 Python.")
    requirements = ROOT / 'requirements.txt'
    fingerprint = hashlib.sha256(requirements.read_bytes()).hexdigest()
    marker = Path(sys.prefix) / 'instaclay-requirements.sha256'
    installed = marker.exists() and marker.read_text() == fingerprint
    if installed:
        for line in requirements.read_text().splitlines():
            name, separator, version = line.partition('==')
            if not separator:
                name = line.split('>=')[0]
            try:
                actual = metadata.version(name)
                if separator and actual != version:
                    installed = False
            except metadata.PackageNotFoundError:
                installed = False
    if not installed:
        print('Installing project dependencies. First setup requires internet.', flush=True)
        run(['-m', 'pip', 'install', '--only-binary=:all:', '-r', str(requirements)])
        marker.write_text(fingerprint)
    from core import FEATURES, post_features, predict
    import joblib
    import pandas as pd
    artifacts = ROOT / 'artifacts'
    required = ['model.joblib', 'report.json', 'cleaned_posts.csv', 'test_metrics.csv',
                'cross_validation.csv', 'hypothesis_tests.csv', 'correlations.csv',
                'descriptive_statistics.csv', 'feature_importance.csv', 'test_predictions.csv', 'splits.csv']
    retrain = '--retrain' in sys.argv or any(not (artifacts / f).exists() for f in required)
    if not retrain:
        try:
            report = json.loads((artifacts / 'report.json').read_text(encoding='utf-8'))
            raw_hash = hashlib.sha256((ROOT / 'data/instagram_posts.csv').read_bytes()).hexdigest()
            retrain = raw_hash != report['raw_sha256'] or report['versions']['sklearn'] != metadata.version('scikit-learn') or report['versions']['pandas'] != metadata.version('pandas') or report['versions']['numpy'] != metadata.version('numpy') or not report['versions']['python'].startswith('3.14.')
            bundle = joblib.load(artifacts / 'model.joblib')
            sample = pd.DataFrame([post_features('Test #art', '', bundle['types'][0], '2025-01-01T12:00:00Z')])
            predict(bundle['model'], sample[FEATURES])
        except Exception as exc:
            print(f'Model validation failed: {exc}', flush=True)
            retrain = True
    if retrain:
        print('Building models and analysis from the bundled CSV. This may take several minutes.', flush=True)
        run(['train.py'])
    print('Opening InstaClay at http://localhost:8501. Keep this window open. Ctrl+C stops the app.', flush=True)
    run(['-m', 'streamlit', 'run', 'app.py', '--server.address=localhost',
         '--server.port=8501', '--server.headless=false', '--browser.gatherUsageStats=false'])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f'\nStartup failed: {exc}', file=sys.stderr)
        sys.exit(1)
