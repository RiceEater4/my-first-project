# What If the Planets Played Christmas Music? (pixel short)

1080x1920, 60 fps, 42 s seamless loop, no voice: just bells and music.

Planets circle the Sun on golden garland orbits hung with bells. Every bell a planet passes
rings on the beat, and planets closer to the Sun go faster:

| Planet | Plays | Rhythm |
|---|---|---|
| Earth | kick | every beat |
| Mercury (closest) | sleigh bells | twice as fast |
| Venus | hand-bell chords | in between the beats |
| Mars | snare | every other beat |
| Jupiter (slowest) | bass | once a bar |

Then a comet plays *Deck the Halls* (traditional, public domain). Every note lights a star,
and when the camera pulls back the stars form a Christmas tree.

Curved edges use soft in-between pixels; nothing drifts, pixels twinkle in place, and the
planets' lit side turns with the Sun's light.

```
python3 audio.py audio.wav
python3 video.py planets_christmas_music.mp4 audio.wav
python3 video.py --stills out_dir 3.0 38.0      # preview frames
```
