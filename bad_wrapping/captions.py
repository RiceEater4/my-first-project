"""Builds captions.json: the narration's exact words (from script.py), timed with the word timestamps
the speech recogniser measured on narration.mp3 (words.json). Chunks of up to 3 words, breaking at
punctuation, each shown from its first word until the next chunk starts."""
import json, re, difflib, os
HERE = os.path.dirname(os.path.abspath(__file__))
from script import LINES
heard = json.load(open(os.path.join(HERE, 'words.json'))) if os.path.exists(os.path.join(HERE, 'words.json')) else []
_n = sum(len(t.split()) for t, _, _ in LINES)
if len(heard) < _n * 0.8:                                   # no recording yet: estimate 2.3 words/s with pauses
    heard, t = [], 0.2
    for txt, _, _ in LINES:
        for w in txt.split():
            d = 0.42 + (0.25 if w[-1] in '.,?!' else 0); heard.append([t, t + d - 0.05, w]); t += d
        t += 0.35
NUM = {'forty': '40', 'two': '2', 'eighteen': '18', 'nine': '9', 'twenty': '20', 'fifty': '50'}
def norm(w):
    w = re.sub(r"[^a-z0-9']", '', w.lower()); w = NUM.get(w, w)
    return re.sub(r'(.)\1+', r'\1', w)            # 'whaaaat' -> 'what'
script_words, line_of, hl_of = [], [], []
for li, (txt, _tts, hl) in enumerate(LINES):
    for w in txt.split():
        script_words.append(w); line_of.append(li); hl_of.append(set(hl))
sm = difflib.SequenceMatcher(a=[norm(w) for w in script_words], b=[norm(w[2]) for w in heard], autojunk=False)
times = [None] * len(script_words)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): times[a + k] = heard[b + k][:2]
for i in range(len(times)):                      # fill any unmatched word between its neighbours
    if times[i] is None:
        prev = next((times[j] for j in range(i - 1, -1, -1) if times[j]), [0, 0])
        nxt = next((times[j] for j in range(i + 1, len(times)) if times[j]), [prev[1] + 0.3] * 2)
        times[i] = [prev[1], nxt[0]]
missing = sum(1 for a, b, n in [(0, 0, 0)] for _ in [])
from script import CAPTION_BREAKS
chunks, idx = [], 0
for li, brk in enumerate(CAPTION_BREAKS):
    assert brk.replace('|', ' ').split() == LINES[li][0].split(), f'caption breaks differ from the narration on line {li}'
    for part in brk.split('|'):
        n = len(part.split()); chunks.append(list(range(idx, idx + n))); idx += n
assert idx == len(script_words)
caps = []
for ci, ch in enumerate(chunks):
    t0 = times[ch[0]][0]
    t_end = times[ch[-1]][1]
    t1 = min((times[chunks[ci + 1][0]][0] - 0.03) if ci + 1 < len(chunks) else t_end + 0.6, t_end + 0.6)
    words = [script_words[i] for i in ch]
    hl = sorted({re.sub(r"[^A-Z0-9']", '', script_words[i].upper()).replace("'S", '') for i in ch} & set().union(*[hl_of[i] for i in ch]))
    caps.append({'t0': round(t0 - 0.03, 3), 't1': round(t1, 3), 'text': ' '.join(words).upper(), 'hl': hl, 'line': line_of[ch[0]]})
lines = []
for li in range(len(LINES)):
    ws = [times[i] for i in range(len(script_words)) if line_of[i] == li]
    lines.append([round(ws[0][0], 3), round(ws[-1][1], 3)])
json.dump(caps, open(os.path.join(HERE, 'captions.json'), 'w'), indent=1)
T = json.load(open(os.path.join(HERE, 'timing.json'))); T['lines'] = lines; json.dump(T, open(os.path.join(HERE, 'timing.json'), 'w'), indent=1)
unmatched = len(script_words) - sum(n for _, _, n in sm.get_matching_blocks())
print('words', len(script_words), 'unmatched', unmatched)
for c in caps: print(f"{c['t0']:6.2f}-{c['t1']:6.2f}  {c['text']}")
