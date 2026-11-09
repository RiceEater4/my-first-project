"""Synthesises the soundtrack: every sound is a ball landing, all locked to one 120 BPM grid."""
import numpy as np, wave, sys
from score import *

SR = 48000
N = int(LOOP * SR)
rng = np.random.default_rng(7)
mix = {k: np.zeros(N) for k in ['kick', 'bell', 'snare', 'bass', 'melody', 'pad', 'fx']}

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def add(track, t, sig):
    i = int(round(t * SR)) % N
    n = len(sig)
    end = min(N, i + n)
    mix[track][i:end] += sig[:end - i]
    if i + n > N:                       # wrap tails around: seamless loop
        mix[track][:i + n - N] += sig[end - i:]

def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    if a > 0:
        e *= np.clip(t / a, 0, 1)
    return e

# --- red ball: rubbery bounce kick ---------------------------------------------------
def kick(vel=1.0):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 52 + 120 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.16)
    boing = np.sin(2 * np.pi * np.cumsum(260 + 160 * np.exp(-t / 0.02)) / SR) * env(n, 0.0005, 0.03) * 0.35
    click = rng.standard_normal(n) * env(n, 0, 0.003) * 0.25
    return vel * (body + boing + click)

# --- green ball: sleigh bells -------------------------------------------------------
BELL_PARTIALS = rng.uniform(2600, 9000, 14)
def sleigh(vel=1.0):
    n = int(0.22 * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, off in enumerate([0, 0.006, 0.013]):           # a few jingles shaken together
        o = int(off * SR)
        tt = t[:n - o]
        part = sum(np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) for f in BELL_PARTIALS[k::3])
        s[o:] += part * np.exp(-tt / 0.05) * (1 - 0.25 * k)
    hiss = rng.standard_normal(n); hiss = np.diff(hiss, prepend=0)
    s = s / 5 + hiss * env(n, 0, 0.02) * 0.15
    return vel * s

# --- gold ball: snap snare + glass ornament tink -------------------------------------
def snare(vel=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = noise - np.convolve(noise, np.ones(6) / 6, 'same')          # crude high-pass
    body = np.sin(2 * np.pi * 190 * t) * env(n, 0, 0.05) * 0.6
    tink = (np.sin(2 * np.pi * hz(98) * t) + 0.4 * np.sin(2 * np.pi * hz(98) * 2.76 * t)) * env(n, 0, 0.09) * 0.18
    return vel * (noise * env(n, 0.0005, 0.07) * 0.55 + body + tink)

# --- blue ball: deep plucked bass + soft thud ---------------------------------------
def bass(m, vel=1.0):
    n = int(1.8 * SR); t = np.arange(n) / SR
    f = hz(m)
    s = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.25)
         + 0.15 * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.12))
    thud = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t / 0.03)) / SR) * env(n, 0.001, 0.1)
    return vel * (s * env(n, 0.003, 0.55) * 0.8 + thud * 0.5)

# --- silver ball on presents: glockenspiel / music box ---------------------------------
def glock(m, vel=1.0, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    f = hz(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9)
         + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25)
         + 0.18 * np.sin(2 * np.pi * f * 5.40 * t) * np.exp(-t / 0.08)
         + 0.25 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.5))
    warm = np.sin(2 * np.pi * f / 2 * t) * np.exp(-t / 0.5) * 0.3     # octave below for body
    return vel * (s + warm) * np.clip(t / 0.001, 0, 1)

# ---------------------------------------------------------------- place every hit
for i, t in enumerate(KICK_HITS):
    add('kick', t, kick(1.0 if i % 4 == 0 else 0.85))
for i, t in enumerate(BELL_HITS):
    add('bell', t, sleigh(0.55 if i % 2 == 0 else 0.9))
for t in SNARE_HITS:
    add('snare', t, snare())
for t in BASS_HITS:
    add('bass', t, bass(ROOT[chord_at(t + 0.01)]))
for t, n, d in MELODY:
    add('melody', t, glock(PITCH[n] + 12, 1.0, 2.2 if d >= 1 else 1.6))
# landing "tap" so each present bounce is felt, not just the note
    add('melody', t, kick(0.18))
# final big hit + chimes as the balls hop back onto the tree
add('fx', END, sleigh(1.0) * 0.8)
for k, t in RETURN.items():
    add('melody', t, glock(RETURN_PITCH[k], 0.7 if k != 'melody' else 0.9, 2.5))
# star sparkle at the end: quick shimmering arpeggio
for j, m in enumerate([91, 95, 98, 103, 98, 95]):
    add('fx', 35.0 + j * 0.0833, glock(m, 0.18, 1.2))

# falling whistles for the long drops (kid 0.5 s, Santa 1 s, robin 0.4 s) - each ends exactly on its first landing
for t_land, dur, f0 in [(bar(5) + 0.5, 0.5, 1300), (bar(7), 1.0, 1500), (bar(9), 0.4, 1700)]:
    m = int(dur * SR); tt = np.arange(m) / SR
    add('fx', t_land - dur, np.sin(2 * np.pi * np.cumsum(f0 - 800 * tt / dur) / SR) * (tt / dur) ** 2 * 0.1)
# a soft shimmer as each ball gathers itself out of the snow
for t_form, root in [(1.25, 91), (5.375, 98), (9.5, 86), (12.5, 79), (17.1, 95)]:
    for j, m in enumerate([root, root + 4, root + 7]):
        add('fx', t_form + j * 0.12, glock(m, 0.12, 1.0))
    add('fx', t_form, sleigh(0.22))

# ---------------------------------------------------------------- warm pad (quiet bed)
t_all = np.arange(N) / SR
pad = np.zeros(N)
for b in range(0, 19):
    t0, t1 = (0.0 if b == 0 else bar(b)), min(LOOP, bar(b + 1))
    if b == 18: t1 = LOOP
    i0, i1 = int(t0 * SR), int(t1 * SR)
    xf = int(0.08 * SR)
    seg_t = np.arange(i1 - i0 + xf) / SR
    seg = np.zeros_like(seg_t)
    for m in CHORD_NOTES[CHORDS[b]]:
        for det in (-0.06, 0.06):
            f = hz(m + det)
            for h in range(1, 6):
                seg += np.sin(2 * np.pi * f * h * seg_t + h) / h ** 1.6
    fade = np.ones_like(seg_t)
    fade[:xf] = np.linspace(0, 1, xf); fade[-xf:] = np.linspace(1, 0, xf)
    seg *= fade
    end = min(N, i0 + len(seg))
    pad[i0:end] += seg[:end - i0]
    if i0 + len(seg) > N:
        pad[:i0 + len(seg) - N] += seg[end - i0:]
pad *= 0.9 + 0.1 * np.sin(2 * np.pi * t_all / (LOOP / 19))
# swell in the chorus, gentler in the groove
level = np.interp(t_all, [0, 2, 17.5, 18, 32, 36, 38], [0.6, 0.6, 0.7, 1.0, 1.0, 0.75, 0.6])
mix['pad'] = pad * level

# ---------------------------------------------------------------- mix
def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
gains = {'kick': 0.95, 'bell': 0.30, 'snare': 0.50, 'bass': 0.65, 'melody': 0.80, 'pad': 0.09, 'fx': 0.45}
dry = sum(norm(mix[k]) * g for k, g in gains.items())

# circular convolution reverb (tail wraps around => loop is seamless)
ir_n = int(1.6 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.45)
ir = np.convolve(ir, np.ones(8) / 8, 'same')
ir /= np.sqrt(np.sum(ir ** 2))
send = dry - 0.6 * norm(mix['kick']) * gains['kick'] - 0.6 * norm(mix['bass']) * gains['bass']
wet = np.fft.irfft(np.fft.rfft(send) * np.fft.rfft(ir, N), N)
out = dry + 0.22 * wet
out = np.tanh(out / np.max(np.abs(out)) * 1.6) / np.tanh(1.6) * 0.93

stereo = np.stack([out, out], 1)
# a touch of width: sleigh bells slightly right, snare slightly left
stereo[:, 0] += 0.06 * norm(mix['snare']) - 0.04 * norm(mix['bell'])
stereo[:, 1] += 0.06 * norm(mix['bell']) - 0.04 * norm(mix['snare'])
stereo /= np.max(np.abs(stereo)) / 0.93
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((stereo * 32767).astype('<i2').tobytes())
print('audio ok', LOOP, 's')
