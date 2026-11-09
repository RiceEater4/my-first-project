"""Soundtrack: every sound is a planet ringing a bell on its orbit, all on one 120 BPM grid,
plus Deck the Halls on glockenspiel as a comet lights the stars. No voice."""
import numpy as np, wave, sys
from score import *

SR = 48000
N = int(LOOP * SR)
rng = np.random.default_rng(7)
mix = {k: np.zeros(N) for k in ['earth', 'mercury', 'venus', 'mars', 'jupiter', 'melody', 'pad', 'fx']}
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
    body = np.sin(2 * np.pi * np.cumsum(52 + 120 * np.exp(-t / 0.035)) / SR) * env(n, 0.001, 0.16)
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
    no = rng.standard_normal(n); no = no - np.convolve(no, np.ones(6) / 6, 'same')
    tink = (np.sin(2 * np.pi * hz(98) * t) + 0.4 * np.sin(2 * np.pi * hz(98) * 2.76 * t)) * env(n, 0, 0.09) * 0.18
    return v * (no * env(n, 0.0005, 0.07) * 0.55 + np.sin(2 * np.pi * 190 * t) * env(n, 0, 0.05) * 0.6 + tink)

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

# ---------------------------------------------------------------- every bell the planets ring
H = {k: p['hits'] for k, p in PLANETS.items()}
for i, t in enumerate(H['earth']): add('earth', t, kick(1.0 if i % 4 == 0 else 0.85))
for i, t in enumerate(H['mercury']): add('mercury', t, sleigh(0.55 if i % 2 == 0 else 0.9))
for t in H['venus']:
    c = CHORD_NOTES[chord_at(t + 0.01)]; add('venus', t, handbell([c[1] + 12, c[2] + 12], 0.8))
for t in H['mars']: add('mars', t, snare())
for t in H['jupiter']: add('jupiter', t, bass(ROOT[chord_at(t + 0.01)]))
for t, n, d in MELODY: add('melody', t, glock(PITCH[n] + 12, 1.0, 2.2 if d >= 0.75 else 1.6))
add('fx', 38.0, sleigh(1.0) * 0.8)                                  # final shimmer
for k, t in BURST.items(): add('melody', t, glock(BURST_PITCH[k], 0.75, 2.5))
for j, m in enumerate([91, 95, 98, 103, 98, 95, 91]):                 # the tree glows
    add('fx', TREE_GLOW + j * 0.0833, glock(m, 0.2, 1.2))
for k, p in PLANETS.items():                                        # sparkle as each planet forms
    if k == 'earth': continue
    tf = p['first'] - FORM
    for j, m in enumerate([86, 90, 93]): add('fx', tf + j * 0.12, glock(m, 0.11, 1.0))
    add('fx', tf, sleigh(0.2))
n = int(0.9 * SR); tt = np.arange(n) / SR                           # the comet streaking in
add('fx', bar(11) - 0.9, rng.standard_normal(n) * np.convolve(np.ones(1), [1], 'same')[0] * (tt / 0.9) ** 2 * 0.05)
add('fx', bar(11) - 0.9, np.sin(2 * np.pi * np.cumsum(900 + 900 * tt / 0.9) / SR) * (tt / 0.9) ** 2 * 0.06)

# ---------------------------------------------------------------- warm pad
t_all = np.arange(N) / SR; pad = np.zeros(N)
for b in range(0, 21):
    t0 = 0.0 if b == 0 else bar(b); t1 = LOOP if b == 20 else bar(b + 1)
    i0, i1 = int(t0 * SR), int(t1 * SR); xf = int(0.08 * SR)
    st = np.arange(i1 - i0 + xf) / SR; seg = np.zeros_like(st)
    for m in CHORD_NOTES[CHORDS[b]]:
        for det in (-0.06, 0.06):
            for h in range(1, 6): seg += np.sin(2 * np.pi * hz(m + det) * h * st + h) / h ** 1.6
    fade = np.ones_like(st); fade[:xf] = np.linspace(0, 1, xf); fade[-xf:] = np.linspace(1, 0, xf)
    seg *= fade; end = min(N, i0 + len(seg)); pad[i0:end] += seg[:end - i0]
    if i0 + len(seg) > N: pad[:i0 + len(seg) - N] += seg[end - i0:]
mix['pad'] = pad * np.interp(t_all, [0, 2, 21.5, 22, 38, 41, 42], [0.6, 0.6, 0.7, 1.0, 1.0, 0.7, 0.6])

def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
gains = {'earth': 0.95, 'mercury': 0.30, 'venus': 0.30, 'mars': 0.50, 'jupiter': 0.65, 'melody': 0.80, 'pad': 0.09, 'fx': 0.45}
dry = sum(norm(mix[k]) * g for k, g in gains.items())
ir_n = int(1.8 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.55)
ir = np.convolve(ir, np.ones(8) / 8, 'same'); ir /= np.sqrt(np.sum(ir ** 2))
send = dry - 0.6 * norm(mix['earth']) * gains['earth'] - 0.6 * norm(mix['jupiter']) * gains['jupiter']
wet = np.fft.irfft(np.fft.rfft(send) * np.fft.rfft(ir, N), N)
out = dry + 0.26 * wet
out = np.tanh(out / np.max(np.abs(out)) * 1.6) / np.tanh(1.6) * 0.93
st = np.stack([out, out], 1)
st[:, 0] += 0.06 * norm(mix['mars']) - 0.04 * norm(mix['mercury']) + 0.04 * norm(mix['venus'])
st[:, 1] += 0.06 * norm(mix['mercury']) - 0.04 * norm(mix['mars']) - 0.02 * norm(mix['venus'])
st /= np.max(np.abs(st)) / 0.93
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio ok', LOOP, 's')
