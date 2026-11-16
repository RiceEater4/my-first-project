"""Final soundtrack: Jett's narration on top, a calm music-box Jingle Bells bed (public domain) about 13 dB
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
spec = importlib.util.spec_from_file_location('ssv', os.path.join(HERE, 'video.py')); v_ = importlib.util.module_from_spec(spec); spec.loader.exec_module(v_)
cs = v_.cs
def crash(v=1.0):
    n = int(0.6 * SR); x = rng.standard_normal(n) * env(n, 0.12); t = np.arange(n) / SR
    return v * (x * 0.6 + sum(np.sin(2 * np.pi * f * t) for f in (2900, 4100, 5300, 6900)) / 4 * env(n, 0.08))
def click(v=1.0):
    n = int(0.03 * SR); return v * rng.standard_normal(n) * env(n, 0.004)
def splat(v=1.0):
    n = int(0.5 * SR); t = np.arange(n) / SR
    return v * (np.sin(2 * np.pi * np.cumsum(260 * np.exp(-t / 0.08) + 60) / SR) * env(n, 0.12) + np.convolve(rng.standard_normal(n), np.ones(30) / 30, 'same') * env(n, 0.05) * 3)
def fire(dur, v=1.0):
    n = int(dur * SR); x = np.convolve(rng.standard_normal(n), np.ones(25) / 25, 'same') * 4
    cr = (rng.random(n) < 0.0015) * rng.standard_normal(n) * 3
    return v * (x * (0.6 + 0.4 * np.sin(np.arange(n) / SR * 7)) + np.convolve(cr, np.ones(40) / 40, 'same') * 4) * np.clip(np.arange(n) / (0.2 * SR), 0, 1) * np.clip((n - np.arange(n)) / (0.3 * SR), 0, 1)
fx = np.zeros(N)
add(fx, 0.0, bells(0.6)); add(fx, 0.3, whoosh(1.0, 0.5))
add(fx, cs(v_.L_HOOK, 3), boom(1.0)); add(fx, cs(v_.L_HOOK, 3), crash(0.5))
add(fx, SEG[v_.L_WHAT][0], boom(0.8)); add(fx, SEG[v_.L_WHAT][0], whoosh(0.3, 0.5))
for i_ in range(2, 16): add(fx, SEG[i_][0], whoosh(0.3, 0.22))
for k in range(10): add(fx, cs(v_.L_HOMES, 1) + k * 0.22, glock(84 + (k % 5) * 2, 0.12, 0.6))
for k in range(12): add(fx, SEG[v_.L_HOURS][0] + k * 0.25, click(0.5))
for k in range(int(2.0 / 0.16)): add(fx, cs(v_.L_PERSEC, 1) + k * 0.16, whoosh(0.12, 0.35))
for k in range(10): add(fx, cs(v_.L_SPEED, 2) - 0.6 + k * 0.14, glock(70 + k * 2, 0.15, 0.4))
add(fx, cs(v_.L_SOUND, 0) + 0.4, boom(0.6))
add(fx, SEG[v_.L_METEOR][0], whoosh(1.2, 0.5)); add(fx, cs(v_.L_METEOR, 3), whoosh(0.8, 0.6))
add(fx, cs(v_.L_FIRE, 1) - 0.1, fire(SEG[v_.L_FIRE][1] - cs(v_.L_FIRE, 1) + 0.6, 0.5))
add(fx, cs(v_.L_FLAT, 1), splat(0.8)); add(fx, cs(v_.L_FLAT, 2), glock(79, 0.3))
add(fx, cs(v_.L_BOOM, 1), boom(1.0)); add(fx, cs(v_.L_BOOM, 2), crash(0.7))
add(fx, cs(v_.L_TWIST, 0) + 0.2, glock(79, 0.4, 2.0)); add(fx, cs(v_.L_TWIST, 2), glock(91, 0.3)); add(fx, cs(v_.L_TWIST, 2) + 0.1, glock(96, 0.3))
add(fx, cs(v_.L_TIME, 1), glock(86, 0.3, 2.5)); add(fx, cs(v_.L_TIME, 1) + 0.15, glock(93, 0.25, 2.5))
for k in range(8): add(fx, cs(v_.L_TIME, 5) + k * 0.2, click(0.4))
add(fx, cs(v_.L_SMART, 2), bells(0.6)); add(fx, cs(v_.L_SMART, 2) + 0.05, glock(91, 0.3))
add(fx, SEG[v_.L_CTA][0] + 0.1, glock(88, 0.3))
add(fx, cs(v_.L_CTA, 2) + 0.35, click(1.0)); add(fx, cs(v_.L_CTA, 2) + 0.38, glock(96, 0.35))
add(fx, cs(v_.L_CTA, 3), whoosh(0.3, 0.4)); add(fx, cs(v_.L_CTA, 4), bells(0.7))
mix = voice * 1.0 + music + fx * 0.30
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.95
st = np.stack([mix, mix], 1)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('mix ok', END)
