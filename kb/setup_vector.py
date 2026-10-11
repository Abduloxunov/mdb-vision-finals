"""Download only the pinned public embedding model into D: storage.
This command is the only model-download step; querying remains offline.
"""
import argparse
import json
import time
from pathlib import Path
from runtime import configure, MODEL_ID, MODEL_REVISION, DIMENSION


def setup(runtime=None):
    root = configure(runtime)
    from huggingface_hub import snapshot_download
    start = time.perf_counter()
    model_path = Path(snapshot_download(repo_id=MODEL_ID, revision=MODEL_REVISION,
        cache_dir=str(root / 'cache/huggingface/hub'), token=False,
        allow_patterns=['README.md','config.json','model.safetensors','modules.json',
                        'sentence_bert_config.json','sentencepiece.bpe.model','tokenizer.json',
                        'tokenizer_config.json','special_tokens_map.json','1_Pooling/config.json'],
        max_workers=2)).resolve()
    if __import__('os').name == 'nt' and model_path.drive.upper() != 'D:':
        raise ValueError('Downloaded model was not stored on D:.')
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(str(model_path), device='cpu', local_files_only=True, trust_remote_code=False)
    model.max_seq_length = 512
    if model.get_embedding_dimension() != DIMENSION:
        raise ValueError('Unexpected embedding dimension.')
    vector = model.encode(['query: tyre damage'], normalize_embeddings=True, show_progress_bar=False)
    if vector.shape != (1, DIMENSION):
        raise ValueError('Embedding smoke check failed.')
    marker = {'model_id':MODEL_ID, 'revision':MODEL_REVISION,'path':str(model_path),'dimension':DIMENSION,
              'device':'cpu','license':'MIT','download_seconds':round(time.perf_counter()-start,3),
              'model_file_bytes':sum(p.stat().st_size for p in model_path.rglob('*') if p.is_file())}
    (root/'model.json').write_text(json.dumps(marker,indent=2),encoding='utf-8')
    return {key:value for key,value in marker.items() if key!='path'}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime')
    print(json.dumps(setup(parser.parse_args().runtime),indent=2))
