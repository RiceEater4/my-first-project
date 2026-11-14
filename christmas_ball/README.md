# What If You Drop a Ball in the Snow? (Christmas pixel short)

1080x1920, 60 fps, 38 s seamless loop, no voice: just bounces and music.

**The fact:** a perfectly bouncy ball dropped from height *h* bounces every *T = 2·√(2h/g)*,
so dropping it 4x higher makes it bounce 2x slower. At 120 BPM the real heights are:

| Ball | Drop height | Bounces every | Sound |
|---|---|---|---|
| Red | 31 cm | 0.5 s (every beat) | kick |
| Gold | 8 cm | 0.25 s (8th notes) | sleigh bells |
| Green | 1.2 m | 1 s (beats 2 & 4) | snare |
| Blue | 4.9 m | 2 s (once a bar) | bass, following the chords |
| Silver | between 5 glowing spots in the snow | the melody | Jingle Bells chorus (public domain, 1857) |

Only balls, snow, mountains, trees and sky. Each ball gathers out of drifting snow at its
drop height and bursts back into snow on a chime at the end. The camera follows one ball at
a time. Captions use plain words, no numbers. Nothing drifts: instead, about 20 times a second a
scatter of pixels swaps with a neighbour, so every surface twinkles in place, and each
ball's coloured glow lights the snow beneath it.

```
python3 audio.py audio.wav
python3 video.py drop_a_ball_in_the_snow.mp4 audio.wav
python3 video.py --stills out_dir 3.0 19.0      # preview frames
```
`score.py` holds all timing and the physics, so picture and sound always stay in sync.
