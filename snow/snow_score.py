"""Timing for 'What If It Never Stopped Snowing?' (story seconds). 120 BPM 4/4: beat 0.5 s, bar 2 s.
Two choruses of Jingle Bells (James Lord Pierpont, 1857 - public domain): the first is bright, the
second freezes up (no drums) and warms back up when the volcanoes melt the ice."""
BEAT, BAR, LOOP, FPS, K = 0.5, 2.0, 64.0, 60, 1.0
def bar(n): return n * BAR
_M = [(0, 'B', 1), (1, 'B', 1), (2, 'B', 2), (4, 'B', 1), (5, 'B', 1), (6, 'B', 2),
      (8, 'B', 1), (9, 'D', 1), (10, 'G', 1.5), (11.5, 'A', .5), (12, 'B', 4),
      (16, 'C', 1), (17, 'C', 1), (18, 'C', 1.5), (19.5, 'C', .5), (20, 'C', 1), (21, 'B', 1), (22, 'B', 1), (23, 'B', .5), (23.5, 'B', .5),
      (24, 'B', 1), (25, 'A', 1), (26, 'A', 1), (27, 'B', 1), (28, 'A', 2), (30, 'D', 2),
      (32, 'B', 1), (33, 'B', 1), (34, 'B', 2), (36, 'B', 1), (37, 'B', 1), (38, 'B', 2),
      (40, 'B', 1), (41, 'D', 1), (42, 'G', 1.5), (43.5, 'A', .5), (44, 'B', 4),
      (48, 'C', 1), (49, 'C', 1), (50, 'C', 1.5), (51.5, 'C', .5), (52, 'C', 1), (53, 'B', 1), (54, 'B', 1), (55, 'B', .5), (55.5, 'B', .5),
      (56, 'D', 1), (57, 'D', 1), (58, 'C', 1), (59, 'A', 1), (60, 'G', 4)]
PITCH = {'G': 67, 'A': 69, 'B': 71, 'C': 72, 'D': 74}
MEL = [(c * 32 + b * BEAT, n, d * BEAT) for c in range(2) for b, n, d in _M]
CHORDS = ['G', 'G', 'G', 'G', 'C', 'G', 'A', 'D', 'G', 'G', 'G', 'G', 'C', 'G', 'D', 'G'] * 2
CHORD_NOTES = {'G': [55, 59, 62, 67], 'C': [55, 60, 64, 67], 'D': [54, 57, 62, 66], 'A': [57, 61, 64, 69]}
ROOT = {'G': 43, 'C': 48, 'D': 50, 'A': 45}
def chord_at(t): return CHORDS[min(31, max(0, int(t // BAR)))]
COLD, WARM = (32.0, 52.0), 52.0                      # no drums while the planet freezes; band returns with the volcanoes
def band_on(t): return not (COLD[0] <= t < COLD[1])
KICKS = [k * BEAT for k in range(int(LOOP / BEAT)) if band_on(k * BEAT)]
SNARES = [k * BEAT for k in range(int(LOOP / BEAT)) if k % 2 == 1 and band_on(k * BEAT)]
BELLS = [k * BEAT / 2 for k in range(int(LOOP / BEAT * 2)) if band_on(k * BEAT / 2)]

# scenes (story seconds)
SCENES = [(0, 'home'), (24, 'cut'), (32, 'trap'), (40, 'globe'), (58, 'home')]
DAY_MARKS = [(0, 1), (8, 7), (16, 30), (24, 365)]
TWIST, VOLCANO = 46.0, 52.0
