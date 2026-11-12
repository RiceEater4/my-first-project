"""Timing for 'What If Penguins Gave Christmas Gifts?'
Waltz (3/4): quarter = 0.4 s, bar = 1.2 s. Bars start at 0.4 s, so t = 0 is the pickup note
("we") and the loop (26.4 s) ends right before the next pickup."""
Q, BAR, B0, LOOP, FPS = 0.4, 1.2, 0.4, 26.4, 60
def bar(k): return B0 + k * BAR

# We Wish You a Merry Christmas (traditional English carol - public domain), key of G, durations in quarters
P = {'D4': 62, 'E4': 64, 'F#4': 66, 'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72, 'D5': 74}
PHRASE = [[('G4', 1), ('G4', .5), ('A4', .5), ('G4', .5), ('F#4', .5)], [('E4', 1), ('E4', 1), ('E4', 1)],
          [('A4', 1), ('A4', .5), ('B4', .5), ('A4', .5), ('G4', .5)], [('F#4', 1), ('D4', 1), ('D4', 1)],
          [('B4', 1), ('B4', .5), ('C5', .5), ('B4', .5), ('A4', .5)], [('G4', 1), ('E4', 1), ('D4', .5), ('D4', .5)],
          [('E4', 1), ('A4', 1), ('F#4', 1)], [('G4', 2)]]
BAR_CHORD = ['G', 'C', 'A7', 'D', 'B7', 'Em', 'D', 'G']
CHORD_NOTES = {'G': [55, 59, 62, 67], 'C': [55, 60, 64, 67], 'A7': [55, 61, 64, 69], 'D': [54, 57, 62, 66],
               'B7': [54, 59, 63, 69], 'Em': [55, 59, 64, 67]}
ROOT = {'G': 43, 'C': 48, 'A7': 45, 'D': 50, 'B7': 47, 'Em': 40}

def phrase_notes(pickup_t, bars_idx, first_bar_k):
    out = [(pickup_t, 'D4', Q)]
    for j, bi in enumerate(bars_idx):
        t = bar(first_bar_k + j)
        for n, d in PHRASE[bi]:
            out.append((round(t, 4), n, d * Q)); t += d * Q
    return out
MEL1 = phrase_notes(0.0, range(8), 0)                     # 0.0 - 9.6   hook + the search
MEL2 = phrase_notes(bar(7) + 2 * Q, range(8), 8)          # 9.6 - 19.2  the thief, the gift
NEST = phrase_notes(bar(15) + 2 * Q, [0, 1, 2, 3, 6, 7], 16)   # 19.2 - 26.4 one pebble per note
CHORDS = {}
for k in range(22):
    if k < 16: CHORDS[k] = BAR_CHORD[k % 8]
    else: CHORDS[k] = BAR_CHORD[[0, 1, 2, 3, 6, 7][k - 16]]
def chord_at(t):
    k = int((t - B0) // BAR)
    return CHORDS.get(min(21, max(0, k)), 'D')          # t < 0.4 is the pickup over the last bar's D

KICKS = [bar(k) for k in range(22)]
STABS = [round(bar(k) + q * Q, 4) for k in range(22) for q in (1, 2) if bar(k) + q * Q < LOOP]
HATS = [round(bar(8) + i * Q / 2, 4) for i in range(int((LOOP - bar(8)) / (Q / 2)))]

# story beats (seconds)
WALKS = [(2.4, 3.6, 50, 76), (4.4, 5.4, 76, 101), (6.2, 7.2, 101, 126), (12.2, 13.0, 126, 150), (13.4, 15.6, 150, 226)]
PICKS = {'dull1': 3.6, 'dull2': 5.4, 'shiny': 7.2, 'best': 13.2}
TOSSES = {'dull1': 4.2, 'dull2': 6.0}
SNATCH, GIVE, PLACE = 10.4, 16.8, 19.2
THIEF = (9.6, 11.6)
