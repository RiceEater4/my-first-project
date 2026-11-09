# What If You Dropped a Ball? (Christmas pixel short)

1080x1920, 60 fps, 38 s seamless loop, no voice: just the balls and the music.

Ornaments fall off a pixel Christmas tree. Every landing is a sound on one 120 BPM grid,
and each new ball adds a layer to the beat:

| Ball | Bounces | Sound |
|---|---|---|
| Red | 120 BPM (every beat) | kick |
| Green | 240 BPM (every 8th) | sleigh bells |
| Gold | 60 BPM (beats 2 & 4) | snare + glass tink |
| Blue | 30 BPM (once a bar) | bass note following the chords |
| Silver | on the presents | Jingle Bells chorus (public domain, 1857) on glockenspiel |

At the end every ball hops back onto the tree, so the last frame is the first frame.

```
python3 audio.py audio.wav
python3 video.py what_if_you_dropped_a_ball.mp4 audio.wav
python3 video.py --stills out_dir 3.0 19.0      # preview frames
```
`score.py` holds all timing, so picture and sound always stay in sync.
