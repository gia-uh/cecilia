#!/usr/bin/env python3
"""
Seed the BeaverDB RAG collection with Cuban data and embeddings.

- Loads data/cuban_data_v2.json
- Generates embeddings via LMStudio /embeddings using EMBEDDING_MODEL
- Indexes documents into the configured RAG collection
"""

import json
import os
import sys
import time
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv
from beaver import BeaverDB, Document

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

LMSTUDIO_API_URL = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-nomic-embed-text-v1.5")
RAG_BEAVER_DB_PATH = os.getenv("RAG_BEAVER_DB_PATH", "rag.db")
RAG_COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "cuban_rag")
DATA_PATH = Path(os.getenv("RAG_DATA_PATH", "data/cuban_data_v2.json"))
BATCH_SIZE = int(os.getenv("RAG_BATCH_SIZE", "32"))


def get_embeddings(texts):
    """Fetch embeddings from LMStudio /embeddings for a batch of texts."""
    if not texts:
        return []
    url = f"{LMSTUDIO_API_URL}/embeddings"
    payload = {"model": EMBEDDING_MODEL, "input": texts}
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        embeddings_raw = data.get("data", [])
        if len(embeddings_raw) != len(texts):
            logger.error(f"Embedding count mismatch: got {len(embeddings_raw)} for {len(texts)} inputs")
        embeddings = []
        for entry in embeddings_raw:
            emb = entry.get("embedding")
            if not emb:
                embeddings.append(None)
                continue
            norm = sum((x * x for x in emb)) ** 0.5
            if norm == 0:
                embeddings.append(None)
                continue
            embeddings.append([x / norm for x in emb])
        return embeddings
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return [None for _ in texts]


def main():
    if not DATA_PATH.exists():
        logger.error(f"Data file not found: {DATA_PATH}")
        sys.exit(1)

    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(dataset, list):
        logger.error("Data file should contain a JSON list of objects with a 'text' field.")
        sys.exit(1)

    db = BeaverDB(RAG_BEAVER_DB_PATH)
    collection = db.collection(RAG_COLLECTION_NAME)

    total = len(dataset)
    logger.info(f"Seeding {total} records into collection '{RAG_COLLECTION_NAME}' at {RAG_BEAVER_DB_PATH} with batch size {BATCH_SIZE}")

    seeded = 0
    for start in range(0, total, BATCH_SIZE):
        batch_items = []
        for idx in range(start, min(start + BATCH_SIZE, total)):
            item = dataset[idx]
            text = item.get("text") if isinstance(item, dict) else None
            if not text:
                continue
            batch_items.append((idx, text))

        if not batch_items:
            continue

        texts = [t for _, t in batch_items]
        embeddings = get_embeddings(texts)

        for (idx, text), emb in zip(batch_items, embeddings):
            if emb is None:
                logger.warning(f"Skipping idx={idx} due to missing embedding")
                continue

            doc_id = f"{RAG_COLLECTION_NAME}-{idx}"
            doc = Document(
                id=doc_id,
                body=text,
                embedding=emb,
            )
            collection.index(doc)
            seeded += 1

        logger.info(f"Indexed {seeded}/{total}")

    logger.info(f"Completed: indexed {seeded}/{total}")
    db.close()


if __name__ == "__main__":
    main()
