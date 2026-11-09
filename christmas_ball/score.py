"""Shared timing for the video and the audio. 120 BPM, 4/4: one beat = 0.5 s, one bar = 2 s."""
BEAT = 0.5
BAR = 2.0
T0 = 2.0            # first downbeat (bar 1)
LOOP = 38.0         # total length; the video loops seamlessly
FPS = 60

def bar(n):         # start time of bar n (1-based)
    return T0 + (n - 1) * BAR

# chord per bar (bars 0..18). Bars 1-8 groove, 9-16 Jingle Bells chorus, 17-18 outro.
CHORDS = {0: 'G', 1: 'G', 2: 'G', 3: 'C', 4: 'D', 5: 'G', 6: 'G', 7: 'C', 8: 'D',
          9: 'G', 10: 'G', 11: 'G', 12: 'G', 13: 'C', 14: 'G', 15: 'D', 16: 'G', 17: 'G', 18: 'G'}
CHORD_NOTES = {'G': [55, 59, 62, 67], 'C': [55, 60, 64, 67], 'D': [54, 57, 62, 66]}
ROOT = {'G': 43, 'C': 48, 'D': 50}

def chord_at(t):
    n = int((t - T0) // BAR) + 1
    return CHORDS.get(max(0, min(18, n)), 'G')

END = 32.0          # last groove hit (bar 16 downbeat)

# Rhythm balls: (name, first landing, period, bpm label)
KICK_HITS  = [T0 + i * 0.5 for i in range(int((END - T0) / 0.5) + 1)]                 # red, from bar 1
BELL_HITS  = [bar(3) + i * 0.25 for i in range(int((END - bar(3)) / 0.25) + 1)]        # green, from bar 3
SNARE_HITS = [bar(5) + 0.5 + i * 1.0 for i in range(int((END - bar(5) - 0.5) / 1.0) + 1)]  # gold, beats 2 & 4 from bar 5
BASS_HITS  = [bar(7) + i * 2.0 for i in range(int((END - bar(7)) / 2.0) + 1)]          # blue, from bar 7

# Jingle Bells chorus (public domain, 1857), key of G. (beat offset in the 8-bar phrase, note name, beats)
_M = [(0, 'B', 1), (1, 'B', 1), (2, 'B', 2),
      (4, 'B', 1), (5, 'B', 1), (6, 'B', 2),
      (8, 'B', 1), (9, 'D', 1), (10, 'G', 1.5), (11.5, 'A', .5),
      (12, 'B', 4),
      (16, 'C', 1), (17, 'C', 1), (18, 'C', 1.5), (19.5, 'C', .5),
      (20, 'C', 1), (21, 'B', 1), (22, 'B', 1), (23, 'B', .5), (23.5, 'B', .5),
      (24, 'D', 1), (25, 'D', 1), (26, 'C', 1), (27, 'A', 1),
      (28, 'G', 4)]
PITCH = {'G': 67, 'A': 69, 'B': 71, 'C': 72, 'D': 74}
PRESENT_INDEX = {'G': 0, 'A': 1, 'B': 2, 'C': 3, 'D': 4}
MELODY = [(bar(9) + b * BEAT, n, d * BEAT) for b, n, d in _M]

# Balls hop back onto the tree on these beats (chime arpeggio G B D G + star)
RETURN = {'bell': 33.0, 'kick': 33.5, 'snare': 34.0, 'bass': 34.5, 'melody': 35.0}
RETURN_PITCH = {'bell': 79, 'kick': 83, 'snare': 86, 'bass': 91, 'melody': 95}
