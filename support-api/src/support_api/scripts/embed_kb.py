"""Backfill embeddings for chunks where embedding IS NULL

After embeddings are filled, subsequent runs should not RECREATE embeddings. (idempotent)

Cost: very cheap, pennies on the dollar. text-embedding-3-small $0.02/1M tokens, 
total cost for 37 chunks would be less than a penny.
"""

import sys

from support_api.embeddings import embed_batch
from support_api.storage import connect
from support_api.storage.queries import update_kb_chunk_embedding

BATCH_SIZE = 16 # Azure Open AI accepts up to ~16-2048 inputs per request, 16 a conservative batch size

def main() -> int:
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT article_id, chunk_index, chunk_text
                    FROM kb_chunks
                WHERE embedding IS NULL
                ORDER BY article_id, chunk_index
                """
            )
            pending = cur.fetchall() # all the rows in the kb_chunks table where there isnt an embedding

            if not pending:
                print("No chunks to embed - all chunks already have embeddings.")
                return 0
            
            total = len(pending)
            print(f"Embedding {total} chunks in batches of {BATCH_SIZE}...")

            for batch_start in range(0, total, BATCH_SIZE): # starting from 0 to (# of rows w/ NULL embeddings), incrementing by 16 (BATCH_SIZE)
                batch = pending[batch_start : batch_start + BATCH_SIZE]
                vectors = embed_batch([row["chunk_text"] for row in batch]) # list comprehension of the chunk_text of each row in the batch
                for row, vector in zip(batch, vectors): # (row from db, assosicated vector), (row from db, assosicated vector), (row from db, assosicated vector)
                    update_kb_chunk_embedding(
                        conn,
                        article_id=row["article_id"],
                        chunk_index=row["chunk_index"],
                        embedding=vector
                    )
                conn.commit()
                done = min(batch_start + BATCH_SIZE, total)
                print(f"    embedded {done}/{total}")

            print("Embeddings Done.")
            return 0
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())