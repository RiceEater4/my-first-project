"""Shared timing for 'What If the Planets Played Christmas Music?'
120 BPM, 4/4: one beat = 0.5 s, one bar = 2 s. Video loops every 42 s."""
BEAT, BAR, T0, LOOP, FPS = 0.5, 2.0, 2.0, 42.0, 60

def bar(n): return T0 + (n - 1) * BAR

# chords per bar: 1-10 groove, 11-18 Deck the Halls, 19-20 outro
CHORDS = {0: 'G', 1: 'G', 2: 'G', 3: 'C', 4: 'D', 5: 'G', 6: 'G', 7: 'C', 8: 'D', 9: 'Em', 10: 'D',
          11: 'G', 12: 'G', 13: 'D', 14: 'G', 15: 'G', 16: 'G', 17: 'D', 18: 'G', 19: 'G', 20: 'G'}
CHORD_NOTES = {'G': [55, 59, 62, 67], 'C': [55, 60, 64, 67], 'D': [54, 57, 62, 66], 'Em': [55, 59, 64, 67]}
ROOT = {'G': 43, 'C': 48, 'D': 50, 'Em': 40}
def chord_at(t):
    n = int((t - T0) // BAR) + 1
    return CHORDS.get(max(0, min(20, n)), 'G')

# Each planet rings the bells hung evenly around its orbit. Closer to the Sun = faster orbit.
# step = period / bells, so every bell lands exactly on the beat grid.
PLANETS = {
    #           orbit period (s), bells, first hit, last hit
    'earth':   dict(period=6.0,  bells=12, first=2.0,   last=38.0),   # kick, every beat
    'mercury': dict(period=2.0,  bells=8,  first=6.0,   last=38.0),   # sleigh bells, 8th notes
    'venus':   dict(period=4.0,  bells=8,  first=10.25, last=37.75),  # bell chords on the off-beats
    'mars':    dict(period=8.0,  bells=8,  first=14.5,  last=37.5),   # snare on beats 2 and 4
    'jupiter': dict(period=16.0, bells=8,  first=18.0,  last=38.0),   # bass, once a bar
}
for p in PLANETS.values():
    p['step'] = p['period'] / p['bells']
    n = int(round((p['last'] - p['first']) / p['step']))
    p['hits'] = [p['first'] + i * p['step'] for i in range(n + 1)]
FORM = 0.8                       # a planet sparkles into being this long before its first bell

# Deck the Halls (traditional Welsh, public domain), key of G. Each note lights one star.
_PHRASE = [('D', 1.5), ('C', .5), ('B', 1), ('A', 1),
           ('G', 1), ('A', 1), ('B', 1), ('G', 1),
           ('A', .5), ('B', .5), ('C', .5), ('A', .5), ('B', 1.5), ('A', .5),
           ('G', 1), ('F#', 1), ('G', 2)]
PITCH = {'F#': 66, 'G': 67, 'A': 69, 'B': 71, 'C': 72, 'D': 74}
MELODY = []
_t = bar(11)
for rep in range(2):
    for n, d in _PHRASE:
        MELODY.append((_t, n, d * BEAT)); _t += d * BEAT
MELODY[-1] = (MELODY[-1][0], 'G', 1.0)          # last note at 37.0 = the top star

# finale: planets burst into sparkles on a rising chime (Earth stays to start the loop)
BURST = {'mercury': 38.5, 'venus': 39.0, 'mars': 39.5, 'jupiter': 40.0}
BURST_PITCH = {'mercury': 79, 'venus': 83, 'mars': 86, 'jupiter': 91}
TREE_GLOW = 40.5
