"""Soundtrack: a bouncy waltz of We Wish You a Merry Christmas, with pebble clicks, a slide whoosh,
and one pebble landing on every note of the last phrase. No voice."""
import numpy as np, wave, sys
from score import *

SR = 48000
N = int(LOOP * SR)
rng = np.random.default_rng(7)
mix = {k: np.zeros(N) for k in ['kick', 'stab', 'hat', 'bass', 'melody', 'pad', 'fx']}
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def add(track, t, sig):
    i = int(round(t * SR)) % N; n = len(sig); end = min(N, i + n)
    mix[track][i:end] += sig[:end - i]
    if i + n > N: mix[track][:i + n - N] += sig[end - i:]       # wrap tails: seamless loop

def env(n, a, d):
    t = np.arange(n) / SR; e = np.exp(-t / d)
    return e * np.clip(t / a, 0, 1) if a > 0 else e

def kick(v=1.0):
    n = int(0.45 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(48 + 190 * np.exp(-t / 0.028)) / SR) * env(n, 0.001, 0.2)
    body = np.tanh(body * 2.2) / np.tanh(2.2)
    bell = np.sin(2 * np.pi * hz(91) * t) * env(n, 0, 0.05) * 0.10          # tiny bell on top
    return v * (body + bell + rng.standard_normal(n) * env(n, 0, 0.003) * 0.25)

PARTS = rng.uniform(2600, 9000, 14)
def sleigh(v=1.0):
    n = int(0.22 * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for k, off in enumerate([0, 0.006, 0.013]):
        o = int(off * SR); tt = t[:n - o]
        s[o:] += sum(np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) for f in PARTS[k::3]) * np.exp(-tt / 0.05) * (1 - 0.25 * k)
    return v * (s / 5 + np.diff(rng.standard_normal(n), prepend=0) * env(n, 0, 0.02) * 0.15)

def snare(v=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    clap = np.zeros(n)
    for off in (0, 0.009, 0.018, 0.027):
        o = int(off * SR); e = np.exp(-np.arange(n - o) / SR / (0.012 if off < 0.027 else 0.09))
        nz = rng.standard_normal(n - o); nz = nz - np.convolve(nz, np.ones(4) / 4, 'same')
        clap[o:] += nz * e
    return v * (clap * 0.5 + _snare_body(n, t))

def _snare_body(n, t):
    no = rng.standard_normal(n); no = no - np.convolve(no, np.ones(6) / 6, 'same')
    tink = (np.sin(2 * np.pi * hz(98) * t) + 0.4 * np.sin(2 * np.pi * hz(98) * 2.76 * t)) * env(n, 0, 0.09) * 0.18
    return no * env(n, 0.0005, 0.06) * 0.3 + np.sin(2 * np.pi * 200 * t) * env(n, 0, 0.04) * 0.45 + tink

def bass(m, v=1.0):
    n = int(1.8 * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.25) + 0.15 * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.12)
    thud = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t / 0.03)) / SR) * env(n, 0.001, 0.1)
    return v * (s * env(n, 0.003, 0.55) * 0.8 + thud * 0.5)

def glock(m, v=1.0, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25)
         + 0.18 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.08) + 0.25 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.5))
    return v * (s + np.sin(np.pi * f * t) * np.exp(-t / 0.5) * 0.3) * np.clip(t / 0.001, 0, 1)

def handbell(ms, v=1.0):
    """soft two-note hand-bell chord for Venus' off-beats"""
    n = int(0.6 * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        f = hz(m); s += np.sin(2 * np.pi * f * t) * np.exp(-t / 0.22) + 0.3 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t / 0.06)
    return v * s * np.clip(t / 0.002, 0, 1)

def pluck(m, v=1.0):
    n = int(0.7 * SR); t = np.arange(n) / SR; f = hz(m); s = np.zeros(n)
    for h in range(1, 9): s += np.sin(2 * np.pi * f * h * t) / h * np.exp(-t * (6 + h * 4))
    return v * s * np.clip(t / 0.002, 0, 1)




def tap(v=1.0, f=1850):
    n = int(0.12 * SR); t = np.arange(n) / SR
    return v * (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.018) + 0.5 * np.sin(2 * np.pi * f * 1.7 * t) * np.exp(-t / 0.008))
def whoosh(dur, v=1.0, up=True):
    n = int(dur * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n)
    nz = np.convolve(nz, np.ones(6) / 6, 'same'); e = np.sin(np.pi * t / dur) ** 2
    return v * nz * e
def pop(v=1.0):
    n = int(0.15 * SR); t = np.arange(n) / SR
    return v * np.sin(2 * np.pi * np.cumsum(500 + 900 * t / 0.15) / SR) * np.exp(-t / 0.05)

MEL = MEL1 + MEL2 + NEST
for i, t in enumerate(KICKS): add('kick', t, kick(1.0 if i % 2 == 0 else 0.85))
add('kick', 0.0, kick(0.7))
for t in STABS:                                                    # oom-pah-PAH chord stabs
    c = CHORD_NOTES[chord_at(t + 0.01)]
    for m in c[1:]: add('stab', t, pluck(m, 0.35))
for i, t in enumerate(HATS): add('hat', t, sleigh(0.45 if i % 2 else 0.75))
for t in KICKS: add('bass', t, bass(ROOT[chord_at(t + 0.01)], 0.8))
for i, (t, n, d) in enumerate(MEL):
    loud = 1.0 if t < 9.6 or t >= 19.2 else 0.9
    add('melody', t, glock(P[n] + 12, loud, 2.0 if d >= 0.8 else 1.4)); add('melody', t, pluck(P[n], 0.4))
for t, n, d in NEST: add('fx', t + 0.0, tap(0.5, 1500 + (P[n] - 60) * 40))   # each nest pebble clacks on its note
# story sounds
for k, t in PICKS.items(): add('fx', t, tap(0.45, 2100))
for k, t in TOSSES.items(): add('fx', t, whoosh(0.25, 0.25)); add('fx', t + 0.55, tap(0.35, 1300))
add('fx', PICKS['shiny'], glock(91, 0.35, 1.4)); add('fx', PICKS['shiny'] + 0.08, glock(95, 0.3, 1.4))
add('fx', THIEF[0], whoosh(THIEF[1] - THIEF[0], 0.45))                     # belly-slide
add('fx', SNATCH, pop(0.6)); add('fx', SNATCH + 0.05, tap(0.5, 2400))
add('fx', 12.0, glock(98, 0.25, 1.0)); add('fx', PICKS['best'], glock(91, 0.35, 1.6)); add('fx', PICKS['best'] + 0.1, glock(98, 0.3, 1.6))
add('fx', GIVE, glock(86, 0.4, 2.0)); add('fx', GIVE + 0.2, pop(0.5))
for j, m in enumerate([86, 90, 93, 98]): add('fx', GIVE + 0.25 + j * 0.07, glock(m, 0.2, 1.4))
add('fx', 2.4, pop(0.5))                                                     # thought bubble pops
n_ = int(0.4 * SR); tt_ = np.arange(n_) / SR
add('fx', LOOP - 0.4, rng.standard_normal(n_) * (tt_ / 0.4) ** 3 * 0.25)  # tiny riser into the loop

# pad (pumps with the kick)
t_all = np.arange(N) / SR; pad = np.zeros(N)
for k in range(-1, 22):
    t0 = max(0.0, bar(k)); t1 = min(LOOP, bar(k + 1))
    i0, i1 = int(t0 * SR), int(t1 * SR); xf = int(0.06 * SR)
    st = np.arange(i1 - i0 + xf) / SR; seg = np.zeros_like(st)
    for m in CHORD_NOTES[CHORDS.get(k, 'D')]:
        for det in (-0.06, 0.06):
            for h in range(1, 6): seg += np.sin(2 * np.pi * hz(m + det) * h * st + h) / h ** 1.6
    fade = np.ones_like(st); fade[:xf] = np.linspace(0, 1, xf); fade[-xf:] = np.linspace(1, 0, xf)
    seg *= fade; end = min(N, i0 + len(seg)); pad[i0:end] += seg[:end - i0]
    if i0 + len(seg) > N: pad[:i0 + len(seg) - N] += seg[end - i0:]
duck = np.ones(N)
for t in KICKS:
    i = int(t * SR) % N; m_ = int(0.45 * SR); seg = 1 - 0.6 * np.exp(-np.arange(m_) / SR / 0.11)
    e_ = min(N, i + m_); duck[i:e_] = np.minimum(duck[i:e_], seg[:e_ - i])
mix['pad'] = pad * duck

def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
gains = {'kick': 0.95, 'stab': 0.4, 'hat': 0.25, 'bass': 0.55, 'melody': 0.85, 'pad': 0.13, 'fx': 0.5}
dry = sum(norm(mix[k]) * g for k, g in gains.items())
ir_n = int(1.5 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.45)
ir = np.convolve(ir, np.ones(8) / 8, 'same'); ir /= np.sqrt(np.sum(ir ** 2))
send = dry - 0.6 * norm(mix['kick']) * gains['kick'] - 0.6 * norm(mix['bass']) * gains['bass']
wet = np.fft.irfft(np.fft.rfft(send) * np.fft.rfft(ir, N), N)
out = dry + 0.22 * wet
out = np.tanh(out / np.max(np.abs(out)) * 1.6) / np.tanh(1.6) * 0.93
st = np.stack([out, out], 1)
st[:, 0] += 0.05 * norm(mix['stab']) - 0.03 * norm(mix['hat'])
st[:, 1] += 0.05 * norm(mix['hat']) - 0.03 * norm(mix['stab'])
st /= np.max(np.abs(st)) / 0.93
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio ok', LOOP, 's')
