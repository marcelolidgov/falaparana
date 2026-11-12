"""Trilha de efeitos sintetizada (sem direitos autorais): aplausos/torcida, whoosh, pop, boom.

Uso: python3 video/sfx.py edl.json saida.wav [--hook FIM] [--final INI] [--pops t1,t2]
- torcida forte no gancho (0..hook) e no final (final..fim); ambiente baixo no meio
- whoosh na entrada de cada gráfico da EDL
"""
import argparse, json, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(20000)


def bandpass(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.clip((f - lo * 0.7) / (lo * 0.3 + 1e-9), 0, 1) * np.clip((hi * 1.3 - f) / (hi * 0.3), 0, 1)
    return np.fft.irfft(X * m, len(x))


def norm(x):
    return x / (np.abs(x).max() + 1e-9)


def aplausos(n, taxa=55):
    out = np.zeros(n)
    k = int(n / SR * taxa)
    L = int(0.03 * SR)
    env = np.exp(-np.arange(L) / (0.006 * SR))
    for p in rng.integers(0, n - L, k):
        g = rng.uniform(0.2, 1.0)
        out[p:p + L] += rng.standard_normal(L) * env * g
    out = bandpass(out, 700, 6000)
    roar = bandpass(rng.standard_normal(n), 250, 1800)
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * np.arange(n) / SR + rng.uniform(0, 6))
    return norm(norm(out) * 0.8 + norm(roar) * 0.45 * mod)


def whoosh(d=0.4):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n); seg = 1024
    for i in range(0, n, seg):
        c = 400 + 5000 * (i / n) ** 1.5
        out[i:i + seg] = bandpass(x[i:i + seg], c * 0.6, c * 1.4)[:len(out[i:i + seg])]
    env = np.sin(np.pi * t / d) ** 2
    return norm(out * env)


def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 25) + 250
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)


def boom():
    n = int(0.8 * SR); t = np.arange(n) / SR
    f = 90 * np.exp(-t * 6) + 42
    return np.tanh(2 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5))


def db(v):
    return 10 ** (v / 20)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl"); ap.add_argument("saida")
    ap.add_argument("--hook", type=float, default=4.0)
    ap.add_argument("--final", type=float, default=None)
    ap.add_argument("--pops", default="")
    ap.add_argument("--booms", default="0")
    a = ap.parse_args()
    edl = json.load(open(a.edl))
    dur = edl["duracao"]; n = int(dur * SR) + SR // 2
    t = np.arange(n) / SR
    fin = a.final if a.final is not None else edl["planos"][-1]["ini"]
    # envelope da torcida
    env = np.full(n, db(-34))
    env = np.where(t < a.hook, db(-14), env)
    rel = (t >= a.hook) & (t < a.hook + 0.8)
    env[rel] = db(-14) + (db(-34) - db(-14)) * ((t[rel] - a.hook) / 0.8)
    att = (t >= fin - 0.3) & (t < fin + 0.4)
    env[att] = db(-34) + (db(-15) - db(-34)) * ((t[att] - fin + 0.3) / 0.7)
    env[t >= fin + 0.4] = db(-15)
    env *= np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.6, 0, 1)
    mix = aplausos(n) * env
    w = whoosh()
    for g in edl.get("graficos", []):
        i = int(max(0, g["ini"] - 0.18) * SR)
        mix[i:i + len(w)] += w[:n - i] * db(-20)
    p = pop()
    for s in [x for x in a.pops.split(",") if x]:
        i = int(float(s) * SR); mix[i:i + len(p)] += p[:n - i] * db(-14)
    b = boom()
    for s in [x for x in a.booms.split(",") if x]:
        i = int(float(s) * SR); mix[i:i + len(b)] += b[:n - i] * db(-12)
    mix = np.clip(mix, -1, 1)
    st = np.stack([mix, np.roll(mix, 240)], 1)  # leve abertura estéreo
    with wave.open(a.saida, "w") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((st * 32767).astype(np.int16).tobytes())
    print("ok ->", a.saida)


if __name__ == "__main__":
    main()
