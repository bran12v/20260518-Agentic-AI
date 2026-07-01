"""Cluster bootstrap: idempotent init -> seed -> embed"""

from support_api.storage import connect, init_db, seed_from_json

_EMBED_LOCK_KEY = 728301 # arbitrary, creates a namespace for our lock.

def main() -> int:
    init_db() # create all our tables

    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM tickets")
        tickets_n = cur.fetchone()["n"] # number of tickets in the db
        cur.execute("SELECT count(*) AS n FROM kb_articles")
        kb_n = cur.fetchone()["n"] # number of kb_articles in the db

    if tickets_n == 0:
        seed_from_json()
        print("seeded core + KB")
    elif kb_n == 0:
        seed_from_json(seed_core=False)
        print("seeded KB only")
    else:
        print(f"skipped seed; {tickets_n} tickets, {kb_n} articles present")
        
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) as n FROM kb_chunks WHERE embedding IS NULL")
        pending = cur.fetchone()["n"]

    if pending == 0:
        print("skipped embed; all chunks already embedded")
        return 0
    
    # AKS deployments usually have more than 1 replica (need to implement a lock)
    from support_api.scripts.embed_kb import main as embed_main
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (_EMBED_LOCK_KEY,))
        try:
            cur.execute("SELECT count(*) as n FROM kb_chunks WHERE embedding IS NULL")
            if cur.fetchone()["n"] == 0:
                print("another pod already embedded; skipping")
            else:
                embed_main()
        finally:
            cur.execute("SELECT pg_advisory_unlock(%s)", (_EMBED_LOCK_KEY,))
    return 0

if __name__ == "__main__":
    raise SystemExit(main()) # only raised as error if not SystemExit(0)