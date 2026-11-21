"""Soundtrack: every sound is a candy cane landing on a world, all on one 120 BPM grid,
plus the Jingle Bells chorus as the Christmas lights come on. No voice."""
import numpy as np, wave, sys
from score import *

SR = 48000
N = int(LOOP * SR)
rng = np.random.default_rng(7)
mix = {k: np.zeros(N) for k in ['earth', 'moon', 'mars', 'jupiter', 'melody', 'pad', 'fx']}
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



def tap(v=1.0):
    """little candy 'tock' layered on every landing so you hear the cane itself"""
    n = int(0.12 * SR); t = np.arange(n) / SR
    return v * (np.sin(2 * np.pi * 1850 * t) * np.exp(-t / 0.018) + 0.5 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.008))

# ---------------------------------------------------------------- hook from frame 0
for t, nm in HOOK:
    add('melody', t, glock(PITCH[nm] + 12, 0.95, 1.2)); add('melody', t, pluck(PITCH[nm], 0.55))
for t in (0.0, 0.5, 1.0, 1.5): add('earth', t, kick(0.95))
for t in (0.5, 1.5): add('mars', t, snare(0.9))
for i in range(8): add('jupiter', i * 0.25, sleigh(0.5 if i % 2 == 0 else 0.8))
n_ = int(0.5 * SR); tt_ = np.arange(n_) / SR
add('fx', 1.5, rng.standard_normal(n_) * (tt_ / 0.5) ** 3 * 0.35)

# ---------------------------------------------------------------- every landing
Hh = {k: w['hits'] for k, w in WORLDS.items()}
for i, t in enumerate(Hh['earth']): add('earth', t, kick(1.0 if i % 4 == 0 else 0.85)); add('fx', t, tap(0.18))
for t in Hh['moon']: add('moon', t, bass(ROOT[chord_at(t + 0.01)])); add('fx', t, tap(0.22))
for t in Hh['mars']: add('mars', t, snare()); add('fx', t, tap(0.15))
for i, t in enumerate(Hh['jupiter']): add('jupiter', t, sleigh(0.55 if i % 2 == 0 else 0.9))
for t, n, d in MELODY: add('melody', t, glock(PITCH[n] + 12, 1.0, 2.2 if d >= 0.5 else 1.6)); add('melody', t, pluck(PITCH[n], 0.3))
for k, t in POP.items(): add('melody', t, glock(POP_PITCH[k], 0.75, 2.4)); add('fx', t, sleigh(0.3))
for j, m in enumerate([91, 95, 98, 103, 98, 95, 91]): add('fx', LIGHTS_FLASH + j * 0.0833, glock(m, 0.2, 1.2))
for k, w in WORLDS.items():                                   # sparkle as each cane appears
    tf = (REFORM if k == 'earth' else w['first'] - w['period'] / 2 - FORM)
    for j, m in enumerate([86, 90, 93]): add('fx', tf + j * 0.12, glock(m, 0.11, 1.0))
for t_land, dur in [(w['first'], w['period'] / 2) for k, w in WORLDS.items() if k != 'earth']:
    m = int(dur * SR); tt = np.arange(m) / SR                 # falling whistle into each first landing
    add('fx', t_land - dur, np.sin(2 * np.pi * np.cumsum(1500 - 800 * tt / dur) / SR) * (tt / dur) ** 2 * 0.08)

# ---------------------------------------------------------------- warm pad with kick pump
t_all = np.arange(N) / SR; pad = np.zeros(N)
for b in range(0, 19):
    t0 = 0.0 if b == 0 else bar(b); t1 = LOOP if b == 18 else bar(b + 1)
    i0, i1 = int(t0 * SR), int(t1 * SR); xf = int(0.08 * SR)
    st = np.arange(i1 - i0 + xf) / SR; seg = np.zeros_like(st)
    for m in CHORD_NOTES[CHORDS[b]]:
        for det in (-0.06, 0.06):
            for h in range(1, 6): seg += np.sin(2 * np.pi * hz(m + det) * h * st + h) / h ** 1.6
    fade = np.ones_like(st); fade[:xf] = np.linspace(0, 1, xf); fade[-xf:] = np.linspace(1, 0, xf)
    seg *= fade; end = min(N, i0 + len(seg)); pad[i0:end] += seg[:end - i0]
    if i0 + len(seg) > N: pad[:i0 + len(seg) - N] += seg[end - i0:]
duck = np.ones(N)
for t in sorted(set([round(x, 4) for x in Hh['earth'] + [0.0, 0.5, 1.0, 1.5]])):
    i = int(t * SR) % N; m_ = int(0.42 * SR); seg = 1 - 0.65 * np.exp(-np.arange(m_) / SR / 0.11)
    e_ = min(N, i + m_); duck[i:e_] = np.minimum(duck[i:e_], seg[:e_ - i])
mix['pad'] = pad * duck * np.interp(t_all, [0, 2, 17.5, 18, 34, 37, 38], [1.0, 0.75, 0.8, 1.0, 1.0, 0.8, 1.0])

def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
gains = {'earth': 0.95, 'moon': 0.65, 'mars': 0.5, 'jupiter': 0.32, 'melody': 0.8, 'pad': 0.16, 'fx': 0.45}
dry = sum(norm(mix[k]) * g for k, g in gains.items())
ir_n = int(1.6 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.5)
ir = np.convolve(ir, np.ones(8) / 8, 'same'); ir /= np.sqrt(np.sum(ir ** 2))
send = dry - 0.6 * norm(mix['earth']) * gains['earth'] - 0.6 * norm(mix['moon']) * gains['moon']
wet = np.fft.irfft(np.fft.rfft(send) * np.fft.rfft(ir, N), N)
out = dry + 0.24 * wet
out = np.tanh(out / np.max(np.abs(out)) * 1.6) / np.tanh(1.6) * 0.93
st = np.stack([out, out], 1)
st[:, 0] += 0.06 * norm(mix['mars']) - 0.04 * norm(mix['jupiter'])
st[:, 1] += 0.06 * norm(mix['jupiter']) - 0.04 * norm(mix['mars'])
st /= np.max(np.abs(st)) / 0.93
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio ok', LOOP, 's')
