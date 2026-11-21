"""Soundtrack: a lo-fi Silent Night. Jupiter's moons Io, Europa and Ganymede (1:2:4 orbits) are the
kick, clap and bass; Saturn's ring sparkles are the hi-hats. No voice."""
import numpy as np, wave, sys
from score import *

SR = 48000
N = int(LOOP * SR)
rng = np.random.default_rng(7)
mix = {k: np.zeros(N) for k in ['io', 'europa', 'ganymede', 'ring', 'melody', 'pad', 'fx']}
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




def crash(v=1.0, dur=2.5):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n); nz = nz - np.convolve(nz, np.ones(3) / 3, 'same')
    return v * nz * np.exp(-t / 0.7) * np.clip(t / 0.003, 0, 1)

M = {k: m['hits'] for k, m in MOONS.items()}
# ---- hook from frame 0: "si-lent night" with the beat already going
for t, n, d in HOOK:
    add('melody', t, glock(NOTE[n] + 12, 1.0, 1.8)); add('melody', t, pluck(NOTE[n], 0.5))
for t in (0.0, 0.75, 1.5, 2.25): add('io', t, kick(0.95))
for t in (0.75, 2.25): add('europa', t, snare(0.85))
for i in range(12): add('ring', i * 0.25, sleigh(0.45 if i % 3 else 0.75))
add('ganymede', 0.0, bass(ROOT['C']))
n_ = int(0.6 * SR); tt_ = np.arange(n_) / SR
add('fx', 2.4, rng.standard_normal(n_) * (tt_ / 0.6) ** 3 * 0.3)
# ---- the moons and the rings
for i, t in enumerate(M['io']): add('io', t, kick(1.0 if i % 2 == 0 else 0.82))
for t in M['europa']: add('europa', t, snare())
for t in M['ganymede']: add('ganymede', t, bass(ROOT[chord_at(t + 0.01)]))
for i, t in enumerate(RING_HITS): add('ring', t, sleigh(0.4 if i % 3 else 0.7))
for k, m in MOONS.items():                                        # sparkle as each moon joins
    tf = m['first'] - 0.75
    for j, mm in enumerate([86, 90, 93]): add('fx', tf + j * 0.1, glock(mm, 0.1, 0.9))
# ---- Silent Night
for t, n, d in MELODY:
    add('melody', t, glock(NOTE[n] + 12, 1.0, 2.6 if d >= 1.0 else 1.8)); add('melody', t, pluck(NOTE[n], 0.35))
# ---- the merge: a big shimmering hit on the high note
add('fx', MERGE, crash(0.9)); add('ganymede', MERGE, bass(ROOT['C'] - 12 + 12, 1.2))
for j, mm in enumerate([84, 88, 91, 96]): add('melody', MERGE + j * 0.06, glock(mm, 0.45, 3.0))
n_ = int(1.2 * SR); tt_ = np.arange(n_) / SR                      # riser into the merge
add('fx', MERGE - 1.2, rng.standard_normal(n_) * (tt_ / 1.2) ** 3 * 0.4)
# ---- outro: "2080" chimes, then a rewind whoosh back to the start
for j, mm in enumerate([79, 84, 88, 91]): add('melody', 33.0 + j * 0.375, glock(mm, 0.35, 2.5))
r0, r1 = REWIND; n_ = int((r1 - r0) * SR); tt_ = np.arange(n_) / SR
sweep = np.sin(2 * np.pi * np.cumsum(300 + 1500 * (tt_ / (r1 - r0)) ** 2) / SR)
add('fx', r0, (rng.standard_normal(n_) * 0.3 + sweep * 0.25) * (tt_ / (r1 - r0)) ** 2 * 0.6)
for j, mm in enumerate([91, 95, 98]): add('fx', r1 + j * 0.08, glock(mm, 0.2, 1.2))

# ---- warm pad that pumps with the kick
t_all = np.arange(N) / SR; pad = np.zeros(N)
for b in range(0, 25):
    t0 = bar(b); t1 = LOOP if b == 24 else bar(b + 1)
    i0, i1 = int(t0 * SR), int(t1 * SR); xf = int(0.08 * SR)
    st = np.arange(i1 - i0 + xf) / SR; seg = np.zeros_like(st)
    for m in CHORD_NOTES[CHORDS[b]]:
        for det in (-0.06, 0.06):
            for h in range(1, 6): seg += np.sin(2 * np.pi * hz(m + det) * h * st + h) / h ** 1.6
    fade = np.ones_like(st); fade[:xf] = np.linspace(0, 1, xf); fade[-xf:] = np.linspace(1, 0, xf)
    seg *= fade; end = min(N, i0 + len(seg)); pad[i0:end] += seg[:end - i0]
    if i0 + len(seg) > N: pad[:i0 + len(seg) - N] += seg[end - i0:]
duck = np.ones(N)
for t in sorted(set(M['io'] + [0.0, 0.75, 1.5, 2.25])):
    i = int(t * SR) % N; m_ = int(0.5 * SR); seg = 1 - 0.6 * np.exp(-np.arange(m_) / SR / 0.13)
    e_ = min(N, i + m_); duck[i:e_] = np.minimum(duck[i:e_], seg[:e_ - i])
mix['pad'] = pad * duck * np.interp(t_all, [0, 3, 16, 16.5, 27, 33, 37.5], [0.9, 0.7, 0.75, 0.9, 1.1, 1.0, 0.9])

def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
gains = {'io': 0.95, 'europa': 0.5, 'ganymede': 0.65, 'ring': 0.28, 'melody': 0.85, 'pad': 0.17, 'fx': 0.45}
dry = sum(norm(mix[k]) * g for k, g in gains.items())
ir_n = int(2.0 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.6)
ir = np.convolve(ir, np.ones(8) / 8, 'same'); ir /= np.sqrt(np.sum(ir ** 2))
send = dry - 0.6 * norm(mix['io']) * gains['io'] - 0.6 * norm(mix['ganymede']) * gains['ganymede']
wet = np.fft.irfft(np.fft.rfft(send) * np.fft.rfft(ir, N), N)
out = dry + 0.28 * wet
out = np.tanh(out / np.max(np.abs(out)) * 1.6) / np.tanh(1.6) * 0.93
st = np.stack([out, out], 1)
st[:, 0] += 0.06 * norm(mix['europa']) - 0.04 * norm(mix['ring'])
st[:, 1] += 0.06 * norm(mix['ring']) - 0.04 * norm(mix['europa'])
st /= np.max(np.abs(st)) / 0.93
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio ok', LOOP, 's')
