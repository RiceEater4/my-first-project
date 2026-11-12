# What If Penguins Gave Christmas Gifts? (pixel short)

1080x1920, 60 fps, 26.6 s seamless loop, no voice.

Cold open on the theft ("HE GOT ROBBED!!"), a quick rewind ("OK WAIT. LET ME EXPLAIN"), then the
story: the search ("nope." "nope."), the perfect pebble, the belly-sliding thief, an even better
pebble, the gift ("she said yes!!"), and the twist that gentoo penguins really do this. Every pebble
of their nest lands on a note of We Wish You a Merry Christmas (traditional, public domain).

Characters are drawn with 2x finer pixels than the background and every pose eases between
frames, so the motion is fluid.

```
python3 audio.py story.wav
python3 cold_open_audio.py story.wav audio.wav
python3 video.py what_if_penguins_gave_gifts.mp4 audio.wav
```
Title and description: `post.txt`.
