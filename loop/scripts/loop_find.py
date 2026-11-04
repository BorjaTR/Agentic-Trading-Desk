"""loop_find: was this tried, learned or built already? Prints every row that holds ALL the words. Read only.

Usage: python3 loop_find.py <PROCESS folder> <PLAYGROUND folder> [--any] word [word ...]
Searches each process's TRIED, SEED, LESSONS and GAPS files, the prompt registry, the playground indexes and every path in PROCESS/SEARCH_ALSO.txt.
--any: rows holding at least one word, most words first, top 30. Use it when a word search finds nothing: an old idea may be worded differently.
"""
import glob, os, sys


def main():
    any_mode = '--any' in sys.argv
    args = [x for x in sys.argv[1:] if x != '--any']
    proc, play, words = args[0], args[1], [w.lower() for w in args[2:]]
    if not words:
        sys.exit('give at least one word')
    files = []
    for pat in ('*/TRIED_*.tsv', '*/SEED_*.tsv', '*/LESSONS_*.tsv', '*/GAPS_*.tsv', 'PROMPTS/PROMPTS_*.tsv'):
        files += glob.glob(os.path.join(proc, pat))
    files += [os.path.join(play, 'INDEX.tsv'), os.path.join(play, 'tool_tests', 'INDEX.tsv')]
    also = os.path.join(proc, 'SEARCH_ALSO.txt')
    if os.path.exists(also):
        with open(also) as h:
            files += [os.path.join(os.path.dirname(proc), os.path.expanduser(x.strip())) for x in h if x.strip() and not x.startswith('#')]
    hits, ranked = 0, []
    for f in sorted(x for x in files if '.pre_' not in x and os.path.exists(x)):
        with open(f, errors='replace') as h:
            for n, line in enumerate(h, 1):
                low = line.lower()
                got = sum(w in low for w in words)
                if n > 1 and (got if any_mode else got == len(words)):
                    hits += 1
                    ranked.append((-got, f'{os.path.relpath(f, os.path.dirname(proc))}:{n}\t{line.rstrip()[:400]}'))
    ranked.sort(key=lambda x: x[0])
    for _, text in ranked[:30] if any_mode else ranked:
        print(text)
    print(f'HITS\t{hits}')


if __name__ == '__main__':
    main()
