# What If You Drop a Ball 4x Higher? (Christmas pixel short)

1080x1920, 60 fps, 38 s seamless loop, no voice: just bounces and music.

**The fact:** a perfectly bouncy ball dropped from height *h* bounces every *T = 2·√(2h/g)*,
so dropping it 4x higher makes it bounce 2x slower. At 120 BPM the real heights are:

| Character | Drop height | Bounces every | Sound |
|---|---|---|---|
| Cat | 31 cm | 0.5 s (every beat) | kick |
| Mouse | 8 cm | 0.25 s (8th notes) | jingle-bell ball |
| Kid | 1.2 m | 1 s (beats 2 & 4) | snare |
| Santa (roof) | 4.9 m | 2 s (once a bar) | bass, following the chords |
| Robin's ball | on a xylophone | the melody | Jingle Bells chorus (public domain, 1857) |

Everything is scaled 60 px per metre, so the heights on screen are true to each other.

```
python3 audio.py audio.wav
python3 video.py drop_a_ball_4x_higher.mp4 audio.wav
python3 video.py --stills out_dir 3.0 19.0      # preview frames
```
`score.py` holds all timing and the physics, so picture and sound always stay in sync.
