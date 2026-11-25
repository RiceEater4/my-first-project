"""Timing for 'What If You Dropped a Candy Cane on Every World?'
120 BPM, 4/4 (beat 0.5 s, bar 2 s), 38 s seamless loop."""
BEAT, BAR, T0, LOOP, FPS = 0.5, 2.0, 2.0, 38.0, 60
def bar(n): return T0 + (n - 1) * BAR

CHORDS = {0: 'G', 1: 'G', 2: 'G', 3: 'C', 4: 'D', 5: 'G', 6: 'G', 7: 'C', 8: 'D',
          9: 'G', 10: 'G', 11: 'G', 12: 'G', 13: 'C', 14: 'G', 15: 'D', 16: 'G', 17: 'G', 18: 'G'}
CHORD_NOTES = {'G': [55, 59, 62, 67], 'C': [55, 60, 64, 67], 'D': [54, 57, 62, 66]}
ROOT = {'G': 43, 'C': 48, 'D': 50}
def chord_at(t):
    n = int((t - T0) // BAR) + 1
    return CHORDS.get(max(0, min(18, n)), 'G')

# A bouncing cane returns every T = 2*sqrt(2h/g). Each world's drop height is chosen so its
# bounce lands on the beat grid; the motion on screen uses that world's real gravity.
G_EARTH = 9.81
END = 34.0
WORLDS = {
    #          gravity m/s^2, bounce period s, first landing
    'earth':   dict(g=9.81, period=0.5,  first=2.0),    # kick, every beat
    'moon':    dict(g=1.62, period=2.0,  first=6.0),    # bass, once a bar (weak gravity: slow, floaty)
    'mars':    dict(g=3.71, period=1.0,  first=10.5),   # clap on 2 and 4
    'jupiter': dict(g=24.79, period=0.25, first=14.0),  # sleigh bells, 8th notes (if it had a floor)
}
for wd in WORLDS.values():
    wd['h'] = wd['g'] * wd['period'] ** 2 / 8                     # metres
    n = int(round((END - wd['first']) / wd['period']))
    wd['hits'] = [wd['first'] + i * wd['period'] for i in range(n + 1) if wd['first'] + i * wd['period'] <= END]
FORM = 0.6

# Jingle Bells chorus (James Lord Pierpont, 1857 - public domain), key of G
_M = [(0, 'B', 1), (1, 'B', 1), (2, 'B', 2), (4, 'B', 1), (5, 'B', 1), (6, 'B', 2),
      (8, 'B', 1), (9, 'D', 1), (10, 'G', 1.5), (11.5, 'A', .5), (12, 'B', 4),
      (16, 'C', 1), (17, 'C', 1), (18, 'C', 1.5), (19.5, 'C', .5),
      (20, 'C', 1), (21, 'B', 1), (22, 'B', 1), (23, 'B', .5), (23.5, 'B', .5),
      (24, 'D', 1), (25, 'D', 1), (26, 'C', 1), (27, 'A', 1), (28, 'G', 4)]
PITCH = {'G': 67, 'A': 69, 'B': 71, 'C': 72, 'D': 74}
MELODY = [(bar(9) + b * BEAT, n, d * BEAT) for b, n, d in _M]
# hook from frame 0: "jingle bells, jingle bells" in quick 8ths
HOOK = [(0.0, 'B'), (0.25, 'B'), (0.5, 'B'), (1.0, 'B'), (1.25, 'B'), (1.5, 'B')]

POP = {'jupiter': 34.5, 'mars': 35.0, 'moon': 35.5, 'earth': 36.0}     # canes burst into sparkles
POP_PITCH = {'jupiter': 79, 'mars': 83, 'moon': 86, 'earth': 91}
LIGHTS_FLASH = 36.5
REFORM = 37.0                                                           # Earth's cane re-forms -> loop
