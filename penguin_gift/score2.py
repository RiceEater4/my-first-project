"""Timing for the blueprint remake of 'What If Penguins Gave Christmas Gifts?' (story time, seconds).
Waltz 3/4: quarter = 0.5 s, bar = 1.5 s, bars start at 0.5 s; t = 0 is the pickup note.
Seven 8-bar verses of We Wish You a Merry Christmas (public domain) = 84 s of story."""
Q, BAR, B0, LOOP, FPS, K = 0.5, 1.5, 0.5, 84.0, 60, 1.0
def bar(k): return B0 + k * BAR

P = {'D4': 62, 'E4': 64, 'F#4': 66, 'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72, 'D5': 74}
PHRASE = [[('G4', 1), ('G4', .5), ('A4', .5), ('G4', .5), ('F#4', .5)], [('E4', 1), ('E4', 1), ('E4', 1)],
          [('A4', 1), ('A4', .5), ('B4', .5), ('A4', .5), ('G4', .5)], [('F#4', 1), ('D4', 1), ('D4', 1)],
          [('B4', 1), ('B4', .5), ('C5', .5), ('B4', .5), ('A4', .5)], [('G4', 1), ('E4', 1), ('D4', .5), ('D4', .5)],
          [('E4', 1), ('A4', 1), ('F#4', 1)], [('G4', 2)]]
BAR_CHORD = ['G', 'C', 'A7', 'D', 'B7', 'Em', 'D', 'G']
CHORD_NOTES = {'G': [55, 59, 62, 67], 'C': [55, 60, 64, 67], 'A7': [55, 61, 64, 69], 'D': [54, 57, 62, 66],
               'B7': [54, 59, 63, 69], 'Em': [55, 59, 64, 67]}
ROOT = {'G': 43, 'C': 48, 'A7': 45, 'D': 50, 'B7': 47, 'Em': 40}
NBARS = 56
def verse(v):
    out = [(round(12.0 * v, 4), 'D4', Q)]
    for j in range(8):
        t = bar(8 * v + j)
        for n, d in PHRASE[j]:
            out.append((round(t, 4), n, d * Q)); t += d * Q
    return out
VERSES = [verse(v) for v in range(7)]
MEL = [n for v in VERSES for n in v]
NEST = [n for n in VERSES[5] if 60.0 <= n[0] < 72.0]              # one pebble per note in verse 6
def chord_at(t):
    k = int((t - B0) // BAR)
    return BAR_CHORD[min(NBARS - 1, max(0, k)) % 8] if t >= B0 else 'D'
KICKS = [bar(k) for k in range(NBARS)]
STABS = [round(bar(k) + q * Q, 4) for k in range(NBARS) for q in (1, 2) if bar(k) + q * Q < LOOP]
HATS = [round(12.0 + i * Q / 2, 4) for i in range(int((LOOP - 12.0) / (Q / 2)))]

# ---------------- the story (story seconds) ----------------
PIP0, PENNY_X, CRUSH_X = 70, 470, 650
WALKS = [(17.0, 18.0, 70, 82), (20.4, 21.4, 82, 104), (23.8, 24.8, 104, 126), (39.0, 41.0, 126, 150), (48.6, 53.6, 225, 398)]
PEBBLE_X = {'dull1': 105, 'dull2': 127, 'shiny': 149, 'best': 317}
PICKS = {'dull1': 18.3, 'dull2': 21.7, 'shiny': 25.1, 'best': 46.4}
TOSSES = {'dull1': 20.0, 'dull2': 23.4}
PLACE_SHINY, SHINY_GROUND_X = 27.0, 162
PEEK = (26.0, 28.6)
THIEF_FALL, SNATCH, THIEF_GONE = 28.6, 29.5, 31.2
THIEF_X0, THIEF_XS, THIEF_X1 = 34, 76, 360
SAD, SIGH, DETERMINED = 31.0, 33.2, 33.8
REVEAL = 36.0
SLIP, FALL, SLIDE, GETUP = 41.5, 42.8, (43.3, 46.3, 150, 225), 47.0
OFFER, PONDER, GIVE = 54.0, (54.5, 56.2), 56.3
NEST_T = 60.0
THIEF_SCENE, THIEF_GIVE = 72.0, 74.6
FLURRY, EGG_IN, CRACKS, HATCH = 76.6, 77.2, (79.4, 80.4), 81.5
NEST_CX = 434
