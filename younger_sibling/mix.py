"""Final soundtrack (bad-wrapping short): Jett's narration on top, a calm music-box Jingle Bells bed (public domain) about 13 dB
under the voice, and soft sound effects on the story beats. usage: python3 mix.py out.wav"""
import sys, os, json, wave, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
T = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T['lines'], T['total']
N = int(END * SR); rng = np.random.default_rng(5)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'narration.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
voice = np.zeros(N); v = np.frombuffer(raw, np.float32); voice[:min(N, len(v))] = v[:N]
voice /= np.max(np.abs(voice)) + 1e-9
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(buf, t, sig):
    i = int(t * SR); e = min(N, i + len(sig))
    if 0 <= i < N: buf[i:e] += sig[:e - i]
def env(n, d): return np.exp(-np.arange(n) / SR / d)
def glock(m, v=1.0, dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    return v * (np.sin(2 * np.pi * f * t) * env(n, 0.8) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * env(n, 0.2)) * np.clip(t / 0.002, 0, 1)
def bells(v=1.0):
    n = int(0.2 * SR); t = np.arange(n) / SR
    return v * sum(np.sin(2 * np.pi * f * t + f) for f in (3100, 4300, 5600, 7200)) / 4 * env(n, 0.05)
def whoosh(dur=0.35, v=1.0):
    n = int(dur * SR); x = np.convolve(rng.standard_normal(n), np.ones(8) / 8, 'same')
    return v * x * np.sin(np.pi * np.arange(n) / n) ** 2
def boom(v=1.0):
    n = int(0.9 * SR); t = np.arange(n) / SR
    return v * (np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t / 0.05)) / SR) * env(n, 0.35) + rng.standard_normal(n) * env(n, 0.04) * 0.3)
def shutter(v=1.0):
    n = int(0.12 * SR); x = rng.standard_normal(n) * env(n, 0.015); y = np.zeros(n); k = int(0.06 * SR); y[k:] = x[:n - k] * 0.7
    return v * (x + y)
def beep(m, v=1.0, d=0.12):
    n = int(d * SR); t = np.arange(n) / SR; return v * np.sign(np.sin(2 * np.pi * hz(m) * t)) * 0.3 * np.clip((d - t) / 0.02, 0, 1)
def wind(dur, v=1.0):
    n = int(dur * SR); x = np.convolve(rng.standard_normal(n), np.ones(60) / 60, 'same') * 6
    return v * x * np.sin(np.pi * np.arange(n) / n) * (0.7 + 0.3 * np.sin(np.arange(n) / SR * 3))
def step(v=1.0):
    n = int(0.09 * SR); return v * np.convolve(rng.standard_normal(n), np.ones(20) / 20, 'same') * env(n, 0.02) * 4
def growl(v=1.0):
    n = int(0.8 * SR); t = np.arange(n) / SR
    return v * np.tanh(3 * np.sin(2 * np.pi * 70 * t) * (1 + 0.5 * np.sin(2 * np.pi * 13 * t))) * np.sin(np.pi * t / 0.8) * 0.5
# ---- calm music bed
music = np.zeros(N)
M = [(0, 71, 1), (1, 71, 1), (2, 71, 2), (4, 71, 1), (5, 71, 1), (6, 71, 2), (8, 71, 1), (9, 74, 1), (10, 67, 1.5), (11.5, 69, .5), (12, 71, 4),
     (16, 72, 1), (17, 72, 1), (18, 72, 1.5), (19.5, 72, .5), (20, 72, 1), (21, 71, 1), (22, 71, 1), (23, 71, .5), (23.5, 71, .5),
     (24, 74, 1), (25, 74, 1), (26, 72, 1), (27, 69, 1), (28, 67, 4)]
CH = [(55, 59, 62), (55, 59, 62), (55, 60, 64), (55, 59, 62), (55, 60, 64), (55, 59, 62), (54, 57, 62), (55, 59, 62)]
for rep in range(int(END / 16) + 1):
    t0 = rep * 16.0
    for b, m, d in M: add(music, t0 + b * 0.5, glock(m, 0.35, 2.2))
    for bar in range(8):
        n = int(2 * SR); t = np.arange(n) / SR
        pad = sum(np.sin(2 * np.pi * hz(m) * t) + 0.15 * np.sin(4 * np.pi * hz(m) * t) for m in CH[bar]) * 0.10
        pad *= np.clip(t / 0.3, 0, 1) * np.clip((2 - t) / 0.3, 0, 1); add(music, t0 + bar * 2, pad)
music /= np.max(np.abs(music)) + 1e-9
venv = np.convolve(np.abs(voice), np.ones(int(0.05 * SR)) / (0.05 * SR), 'same')
venv = np.convolve((venv > 0.02).astype(float), np.ones(int(0.25 * SR)) / (0.25 * SR), 'same')
music *= 0.11 - 0.075 * np.clip(venv, 0, 1)
music[int((END - 1.0) * SR):] *= np.linspace(1, 0, N - int((END - 1.0) * SR))
# ---- effects
import importlib.util
spec = importlib.util.spec_from_file_location('ysv', os.path.join(HERE, 'video.py')); v_ = importlib.util.module_from_spec(spec); spec.loader.exec_module(v_)
cs = v_.cs
def click(v=1.0):
    n = int(0.03 * SR); return v * rng.standard_normal(n) * env(n, 0.004)
def crinkle(dur, v=1.0):
    n = int(dur * SR); x = rng.standard_normal(n) * (rng.random(n) < 0.08)
    x = np.convolve(x, np.ones(6) / 6, 'same') * 3; return v * x * np.clip(np.arange(n) / (0.03 * SR), 0, 1) * np.clip((n - np.arange(n)) / (0.05 * SR), 0, 1)
def tape(v=1.0):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return v * rng.standard_normal(n) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 70 * t))) * env(n, 0.09) * 0.8
def sad_trombone(v=1.0):
    out = np.zeros(int(1.6 * SR))
    for k, m in enumerate((55, 54, 53, 52)):
        n = int(0.4 * SR if k < 3 else 0.8 * SR); t = np.arange(n) / SR; f = hz(m)
        s_ = sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, 6)) * np.clip(t / 0.02, 0, 1) * env(n, 0.5)
        i = int(k * 0.4 * SR); out[i:i + n] += s_[:len(out) - i]
    return v * out
def pop(v=1.0):
    n = int(0.08 * SR); t = np.arange(n) / SR; return v * np.sin(2 * np.pi * np.cumsum(900 - 6000 * t) / SR) * env(n, 0.02)
fx = np.zeros(N)
def hiss(dur, v=1.0):
    n = int(dur * SR); x = rng.standard_normal(n); x = x - np.convolve(x, np.ones(6) / 6, 'same')
    return v * x * np.clip(np.arange(n) / (0.05 * SR), 0, 1) * np.clip((n - np.arange(n)) / (0.2 * SR), 0, 1)
def meow(v=1.0):
    n = int(0.5 * SR); t = np.arange(n) / SR; f = 700 + 300 * np.sin(np.pi * t / 0.5)
    return v * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.5) * 0.6
def thud(v=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    return v * (np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t / 0.06) + 45) / SR) * env(n, 0.09))
def munch(v=1.0):
    n = int(0.12 * SR); return v * np.convolve(rng.standard_normal(n), np.ones(8) / 8, 'same') * env(n, 0.03) * 3
def stamp(v=1.0):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return v * (np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t / 0.03) + 60) / SR) * env(n, 0.06) + rng.standard_normal(n) * env(n, 0.01) * 0.5)
add(fx, 0.1, glock(84, 0.25))
D = SEG[v_.L_DUMB][0]; add(fx, D, boom(1.0)); add(fx, D + 0.1, glock(55, 0.35, 1.2))
for i_ in range(2, len(SEG)): add(fx, SEG[i_][0], whoosh(0.3, 0.2))
for k in range(8): add(fx, SEG[v_.L_CHECKED][0] + 0.3 + k * 0.12, glock(72 + k * 2, 0.13, 0.5))
add(fx, cs(v_.L_CHECKED, 2), bells(0.5)); add(fx, cs(v_.L_CHECKED, 3), glock(91, 0.3)); add(fx, SEG[v_.L_TWO][0], boom(0.5)); add(fx, cs(v_.L_TWO, 2), sad_trombone(0.3))
P = cs(v_.L_SUB, 2); add(fx, P, boom(0.9)); add(fx, P, bells(0.8)); add(fx, P + 0.35, click(1.0)); [add(fx, P + 0.38 + k * 0.08, glock(86 + k * 3, 0.25, 1.0)) for k in range(5)]
for k in range(10): add(fx, cs(v_.L_STUDY, 1) - 0.2 + k * 0.12, click(0.35))
add(fx, cs(v_.L_STUDY, 2), glock(88, 0.3))
add(fx, cs(v_.L_THEORY, 4), bells(0.6)); [add(fx, cs(v_.L_THEORY, 4) + k * 0.08, glock(84 + k * 3, 0.2, 1.0)) for k in range(4)]
add(fx, cs(v_.L_SMARTER, 2), glock(91, 0.3))
add(fx, SEG[v_.L_NOBODY][0], boom(0.8)); add(fx, SEG[v_.L_NOBODY][0] + 0.1, glock(55, 0.4, 2.0))
add(fx, cs(v_.L_STRICT, 3), stamp(0.9)); add(fx, cs(v_.L_STRICT, 4), pop(0.4)); add(fx, cs(v_.L_STRICT, 5), bells(0.5))
for k in range(4): add(fx, cs(v_.L_FOUR, 2) + k * 0.15, glock(86 + k * 2, 0.25, 0.8))
add(fx, cs(v_.L_FOUR, 3), boom(0.5))
add(fx, cs(v_.L_NICE, 2), bells(0.8)); [add(fx, cs(v_.L_NICE, 2) + k * 0.08, glock(84 + k * 3, 0.22, 1.2)) for k in range(5)]
add(fx, SEG[v_.L_CTA][0] + 0.1, pop(0.4)); add(fx, cs(v_.L_CTA, 2), whoosh(0.4, 0.4)); add(fx, cs(v_.L_CTA, 3), bells(0.7))
mix = voice * 1.0 + music + fx * 0.30
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.95
st = np.stack([mix, mix], 1)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('mix ok', END)
