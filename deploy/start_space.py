"""Hugging Face Space entry point: fetch the private checkpoint, then start the CarDoctor server.

The trained weights are not in git (CarDD rights review pending). Upload them once to a private
model repo and give the Space read access with an HF_TOKEN secret:
  huggingface-cli upload <user>/cardoctor-weights checkpoint_best_ema.pth --repo-type model --private
"""
import os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
target = Path(os.environ.get('CARDOCTOR_CHECKPOINT', '/data/weights/checkpoint_best_ema.pth'))
repo = os.environ.get('CARDOCTOR_WEIGHTS_REPO', '')
if not target.is_file() and repo:
    try:
        from huggingface_hub import hf_hub_download
        target.parent.mkdir(parents=True, exist_ok=True)
        path = hf_hub_download(repo_id=repo, filename=target.name, token=os.environ.get('HF_TOKEN') or None, local_dir=str(target.parent))
        print('Checkpoint downloaded:', path, flush=True)
    except Exception as exc:  # the app still starts; text checks work without the detector
        print('Checkpoint download failed:', type(exc).__name__, exc, flush=True)
space = os.environ.get('SPACE_HOST', '')  # set by Hugging Face, e.g. user-cardoctor.hf.space
hosts = ','.join(h for h in [os.environ.get('CARDOCTOR_PUBLIC_HOSTS', ''), space] if h)
os.environ['CARDOCTOR_PUBLIC_HOSTS'] = hosts
os.chdir(ROOT)
sys.exit(subprocess.call([sys.executable, '-B', 'src/app.py', '--host', '0.0.0.0', '--port', os.environ.get('PORT', '7860'), '--checkpoint', str(target)]))
