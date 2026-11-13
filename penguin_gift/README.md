# What If Penguins Gave Christmas Gifts? (pixel short)

1080x1920, 60 fps, 48 s seamless loop (pace knob K in score.py), no voice.

Cold open on the theft ("HE GOT ROBBED!!"), a quick rewind ("OK WAIT. LET ME EXPLAIN"), then the
story: the search ("nope." "nope."), the perfect pebble, the belly-sliding thief, a slip across the
ice and a belly-slide to an even better pebble, the gift ("she said yes!!"), the twist that gentoo
penguins really do this, and "a few weeks later..." an egg that hatches into a chick in a Santa hat. Every pebble
of their nest lands on a note of We Wish You a Merry Christmas (traditional, public domain).

Characters are drawn with 2x finer pixels than the background and every pose eases between
frames, so the motion is fluid.

```
python3 audio.py story.wav
python3 cold_open_audio.py story.wav audio.wav
python3 video.py what_if_penguins_gave_gifts.mp4 audio.wav
```
Title and description: `post.txt`.

## Blueprint remake (`video2.py`) — 86 s
Navy blueprint grid, floating ice diorama, navy-outlined pixel characters, unboxed bold captions.
Story: meet Pip and Penny -> he wants to give her a pebble -> the search -> the thief (set up behind
an iceberg) steals it -> a better pebble across the ice -> belly-slide -> the gift -> the twist ->
the nest -> the thief had a crush too -> the egg hatches.
```
python3 audio2.py story.wav
python3 cold_open_audio2.py story.wav audio.wav
python3 video2.py penguin_gift_blueprint.mp4 audio.wav
```
