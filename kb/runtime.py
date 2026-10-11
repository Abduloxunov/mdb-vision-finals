"""All mutable vector/model state and caches are explicitly on D:."""
from pathlib import Path
import os
BASE = Path(__file__).resolve().parent
MODEL_ID = 'intfloat/multilingual-e5-small'
MODEL_REVISION = '614241f622f53c4eeff9890bdc4f31cfecc418b3'
COLLECTION = 'cardoctor_text_e5_small_v1'
DIMENSION = 384


def configure(runtime=None):
    path = Path(runtime or os.environ.get('CARDOCTOR_KB_RUNTIME', BASE / '.runtime')).resolve()
    if os.name == 'nt' and path.drive.upper() != 'D:':
        raise ValueError('KB caches and runtime must be on D:.')
    path.mkdir(parents=True, exist_ok=True)
    paths = {'HF_HOME':'cache/huggingface', 'HF_HUB_CACHE':'cache/huggingface/hub',
             'HUGGINGFACE_HUB_CACHE':'cache/huggingface/hub', 'HF_ASSETS_CACHE':'cache/huggingface/assets', 'HF_XET_CACHE':'cache/huggingface/xet',
             'SENTENCE_TRANSFORMERS_HOME':'cache/sentence-transformers', 'TORCH_HOME':'cache/torch',
             'XDG_CACHE_HOME':'cache', 'PIP_CACHE_DIR':'cache/pip', 'TMP':'tmp', 'TEMP':'tmp', 'TMPDIR':'tmp'}
    for key, sub in paths.items():
        target = path / sub
        target.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(target)
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['DO_NOT_TRACK'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    return path
