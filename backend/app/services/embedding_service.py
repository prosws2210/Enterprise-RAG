from openai import OpenAI

from app.config import settings
from app.services.query_cache_service import query_cache


openai_client = OpenAI(api_key=settings.openai_api_key)

def embed_texts(texts: list[str], model: str | None = None) -> list[list[float]]:
    if not texts:
        return []
    if model is None:
        model = settings.embedding_model

    results: list[list[float] | None] = [None] * len(texts)
    miss_indices: list[int] = []
    miss_texts: list[str] = []

    for i, text in enumerate(texts):
        cached = query_cache.get_embedding(text)
        if cached is not None:
            results[i] = cached

        else:
            miss_indices.append(i)
            miss_texts.append(text)
        
    if miss_texts:
        try:
            response = openai_client.embeddings.create(input=miss_texts, model=model)
            for idx_in_misses, item in enumerate(response.data):
                original_idx = miss_indices[idx_in_misses]
                vector = item.embedding
                results[original_idx] = vector
                query_cache.set_embedding(miss_texts[idx_in_misses], vector)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"OpenAI embedding failed: {e}. Falling back to local SentenceTransformers.")
            # Lazy load sentence-transformers to avoid slowing down startup if not needed
            from sentence_transformers import SentenceTransformer
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            # Using a fast, standard 384-dim model. Note: Qdrant must be created with the matching dimensionality.
            # If Qdrant was expecting 1536 (from OpenAI) and we send 384, it will fail, so we use a 1536 model or pad.
            # However, text-embedding-3-small defaults to 1536 dimensions. 
            # We can use a free HuggingFace model. 'nomic-ai/nomic-embed-text-v1.5' supports dynamic dim but 768 is default.
            # To match 1536 without failing Qdrant, we'll pad the 384 vector to 1536.
            # Alternatively, we just use BAAI/bge-small-en-v1.5 and pad with zeros.
            st_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            embeddings = st_model.encode(miss_texts)
            
            for idx_in_misses, emb in enumerate(embeddings):
                original_idx = miss_indices[idx_in_misses]
                # Pad to 1536 dimensions to match text-embedding-3-small which Qdrant expects
                vector = emb.tolist()
                if len(vector) < 1536:
                    vector = vector + [0.0] * (1536 - len(vector))
                elif len(vector) > 1536:
                    vector = vector[:1536]
                    
                results[original_idx] = vector
                query_cache.set_embedding(miss_texts[idx_in_misses], vector)

    return [r for r in results if r is not None]

