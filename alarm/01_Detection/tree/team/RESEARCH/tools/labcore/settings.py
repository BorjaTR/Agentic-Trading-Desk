"""labcore.settings (BUILD2, 23 Oct 2026): the settings loader with its sha check. MOVED from bucket_proof.py 2b615f53396155d0
(load_settings, verbatim behaviour: the JSON plus _sha16 and _path); want_sha16 added: a settings file whose sha16 differs from the one the
card or the ledger row names is REFUSED (LEAD SHARED_FUNCTIONS_V1: 'refuses a settings file whose sha16 differs')."""
import json
from .ids import sha16_file


def load_settings(path, want_sha16=None):
    sha = sha16_file(path)
    if want_sha16 is not None and sha != want_sha16:
        raise ValueError('settings %s is %s, not %s: refused' % (path, sha, want_sha16))
    with open(path) as f:
        s = json.load(f)
    s['_sha16'] = sha; s['_path'] = path
    return s
