"""Timing for 'The Christmas Star Is Coming Back... in 2080'.
6/8 lilt: dotted-quarter beat = 0.75 s (80 BPM), eighth = 0.25 s, bar = 1.5 s. 37.5 s seamless loop."""
BEAT, EIGHTH, BAR, LOOP, FPS = 0.75, 0.25, 1.5, 37.5, 60
def bar(n): return n * BAR

CHORDS = {0: 'C', 1: 'C', 2: 'C', 3: 'F', 4: 'C', 5: 'C', 6: 'G', 7: 'C', 8: 'F', 9: 'C', 10: 'G',
          11: 'F', 12: 'F', 13: 'C', 14: 'C', 15: 'G', 16: 'G', 17: 'C', 18: 'C', 19: 'C', 20: 'G', 21: 'C',
          22: 'C', 23: 'C', 24: 'C'}
CHORD_NOTES = {'C': [55, 60, 64, 67], 'F': [57, 60, 65, 69], 'G': [55, 59, 62, 67]}
ROOT = {'C': 36, 'F': 41, 'G': 43}
def chord_at(t): return CHORDS.get(max(0, min(24, int(t // BAR))), 'C')

# Jupiter's moons Io, Europa and Ganymede really orbit in a 1:2:4 rhythm (the Laplace resonance).
# Each one "hits" when it passes in front of Jupiter.
END = 33.0
def grid(start, step, stop=END): return [round(start + i * step, 4) for i in range(int((stop - start) / step + 1e-6) + 1)]
MOONS = {
    'io':       dict(period=0.75, first=3.0),     # kick, every beat
    'europa':   dict(period=1.5,  first=6.75),    # clap, the 2nd beat of every bar
    'ganymede': dict(period=3.0,  first=9.0),     # bass, every two bars
}
for m in MOONS.values(): m['hits'] = grid(m['first'], m['period'])
RING_HITS = grid(13.5, 0.25, END - 0.25)          # Saturn's ring sparkles on the hi-hats

# Silent Night (Franz Gruber, 1818 - public domain), key of C, durations in eighths
NOTE = {'C4': 60, 'D4': 62, 'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72, 'D5': 74, 'E5': 76, 'F5': 77}
HOOK_BARS = [[('G4', 3), ('A4', 1), ('G4', 2)], [('E4', 6)]]                 # "si-lent night" from frame 0
SONG_BARS = [[('A4', 4), ('A4', 2)], [('C5', 3), ('B4', 1), ('A4', 2)], [('G4', 3), ('A4', 1), ('G4', 2)], [('E4', 6)],
             [('D5', 4), ('D5', 2)], [('F5', 3), ('D5', 1), ('B4', 2)], [('C5', 6)], [('E5', 6)],
             [('C5', 3), ('G4', 1), ('E4', 2)], [('G4', 3), ('F4', 1), ('D4', 2)], [('C4', 6)]]
def notes(bars, t0):
    out = []
    for b, notes_ in enumerate(bars):
        t = t0 + b * BAR
        for n, d in notes_:
            out.append((t, n, d * EIGHTH)); t += d * EIGHTH
    return out
HOOK = notes(HOOK_BARS, 0.0)
MELODY = notes(SONG_BARS, bar(11))                 # 16.5 s -> 33.0 s
MERGE = 27.0                                        # the high "peace" note: the two planets become one star
REWIND = (35.5, 36.5)
SCENES = [(0.0, 'wide'), (3.0, 'jupiter'), (13.2, 'saturn'), (16.2, 'wide')]
FADE = 0.5
