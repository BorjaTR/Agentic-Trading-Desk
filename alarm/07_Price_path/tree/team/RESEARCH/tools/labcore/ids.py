"""labcore.ids (BUILD2, 23 Oct 2026): the one sha16. MOVED from team/RESEARCH/tools/bucket_proof/bucket_proof.py 2b615f53396155d0
(sha16_file, verbatim); sha16_text added beside it (the same rule on a text). sha16 = the first 16 hex of sha256."""
import hashlib


def sha16_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def sha16_text(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]
