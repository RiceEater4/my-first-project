"""Soundtrack for 'What If It Never Stopped Snowing?': Jingle Bells, bright -> frozen -> warm. No voice."""
import numpy as np, wave, sys
from snow_score import *

SR = 48000
N = int(LOOP * K * SR)
rng = np.random.default_rng(7)
mix = {k: np.zeros(N) for k in ['kick', 'stab', 'hat', 'bass', 'melody', 'pad', 'fx']}
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def add(track, t, sig):
    i = int(round(t * K * SR)) % N; n = len(sig); end = min(N, i + n)
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


def rumble(dur, v=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.convolve(rng.standard_normal(n), np.ones(60) / 60, 'same') * 6
    return v * (x + 0.6 * np.sin(2 * np.pi * 38 * t)) * np.exp(-t / (dur * 0.5)) * np.clip(t / 0.02, 0, 1)
def wind(t0, t1, v=0.3):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    x = np.convolve(rng.standard_normal(n), np.ones(30) / 30, 'same') * 3
    return v * x * (0.6 + 0.4 * np.sin(2 * np.pi * t / 2.3)) * np.clip(t / 1.0, 0, 1) * np.clip((t1 - t0 - t) / 1.0, 0, 1)
def shimmer(v=1.0):
    n = int(1.2 * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in (2900, 3700, 4400, 5200): s += np.sin(2 * np.pi * f * t + f) * np.exp(-t / 0.4)
    return v * s / 4

for i, t in enumerate(KICKS): add('kick', t, kick(0.95 if i % 4 == 0 else 0.8))
for t in SNARES: add('stab', t, snare(0.7))
for i, t in enumerate(BELLS): add('hat', t, sleigh(0.45 if i % 2 == 0 else 0.75))
for k in range(32):
    t = bar(k)
    if band_on(t): add('bass', t, bass(ROOT[CHORDS[k]], 0.8)); add('bass', t + 1.0, bass(ROOT[CHORDS[k]] + 7, 0.5))
for t, n, d in MEL:
    cold = COLD[0] <= t < COLD[1]
    add('melody', t, glock(PITCH[n] + (24 if cold else 12), 0.7 if cold else 1.0, 3.0 if cold else 2.0))
    if not cold: add('melody', t, pluck(PITCH[n], 0.35))
# story sounds
add('fx', 0.0, shimmer(0.4))
for t in (8.0, 16.0, 24.0): add('fx', t, glock(98, 0.3, 1.4)); add('fx', t + 0.08, glock(103, 0.25, 1.4))   # counter jumps
add('fx', 10.2, kick(0.5)); add('fx', 12.4, pop(0.6))                        # car buried, kid cheers
add('fx', 18.5, kick(0.4)); add('fx', 26.0, shimmer(0.5))
add('fx', 32.0, wind(32.0, 52.0, 0.45))
add('fx', 33.5, glock(91, 0.3, 2.0)); add('fx', 35.5, glock(86, 0.3, 2.0))
for t in (41.0, 42.5, 44.0): add('fx', t, shimmer(0.35))
add('fx', TWIST, rumble(1.5, 0.8)); add('fx', TWIST, sleigh(0.9))
for j, m in enumerate([79, 83, 86, 91]): add('fx', TWIST + 0.1 + j * 0.08, glock(m, 0.35, 2.0))
for t in (VOLCANO, VOLCANO + 1.0, VOLCANO + 1.8, VOLCANO + 2.6): add('fx', t, rumble(1.2, 0.9))
add('fx', 58.0, shimmer(0.4)); add('fx', 60.0, pop(0.5))
n_ = int(0.5 * SR); tt_ = np.arange(n_) / SR
add('fx', LOOP - 0.5, rng.standard_normal(n_) * (tt_ / 0.5) ** 3 * 0.25)

pad = np.zeros(N)
for k in range(32):
    t0, t1 = bar(k), min(LOOP, bar(k + 1)); i0, i1 = int(t0 * SR), int(t1 * SR); xf = int(0.06 * SR)
    st = np.arange(i1 - i0 + xf) / SR; seg = np.zeros_like(st)
    for m in CHORD_NOTES[CHORDS[k]]:
        for det in (-0.06, 0.06):
            for h in range(1, 6): seg += np.sin(2 * np.pi * hz(m + det) * h * st + h) / h ** 1.6
    fade = np.ones_like(st); fade[:xf] = np.linspace(0, 1, xf); fade[-xf:] = np.linspace(1, 0, xf)
    seg *= fade * (1.6 if COLD[0] <= t0 < COLD[1] else 1.0); end = min(N, i0 + len(seg)); pad[i0:end] += seg[:end - i0]
    if i0 + len(seg) > N: pad[:i0 + len(seg) - N] += seg[end - i0:]
duck = np.ones(N)
for t in KICKS:
    i = int(t * SR) % N; m_ = int(0.42 * SR); sg = 1 - 0.55 * np.exp(-np.arange(m_) / SR / 0.11)
    e_ = min(N, i + m_); duck[i:e_] = np.minimum(duck[i:e_], sg[:e_ - i])
mix['pad'] = pad * duck

def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
gains = {'kick': 0.9, 'stab': 0.45, 'hat': 0.25, 'bass': 0.55, 'melody': 0.85, 'pad': 0.15, 'fx': 0.55}
dry = sum(norm(mix[k]) * g for k, g in gains.items())
ir_n = int(2.2 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.7)
ir = np.convolve(ir, np.ones(8) / 8, 'same'); ir /= np.sqrt(np.sum(ir ** 2))
send = dry - 0.6 * norm(mix['kick']) * gains['kick'] - 0.6 * norm(mix['bass']) * gains['bass']
wet = np.fft.irfft(np.fft.rfft(send) * np.fft.rfft(ir, N), N)
out = dry + 0.28 * wet
out = np.tanh(out / np.max(np.abs(out)) * 1.6) / np.tanh(1.6) * 0.93
st = np.stack([out, out], 1)
st[:, 0] += 0.05 * norm(mix['stab']) - 0.03 * norm(mix['hat']); st[:, 1] += 0.05 * norm(mix['hat']) - 0.03 * norm(mix['stab'])
st /= np.max(np.abs(st)) / 0.93
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio ok', LOOP, 's')
