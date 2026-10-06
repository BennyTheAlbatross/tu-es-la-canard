# Music files

`groovy-town.mp3` is the browser copy of Benny's supplied `groovy town.wav`.
The approved displayed song title is exactly `groovy town`.

The source WAV stays outside this repository and remains unchanged.
The MP3 was encoded with FFmpeg/libmp3lame, VBR quality 2, preserving the
source stereo channels and sample rate. Source metadata was removed; only
the approved title was explicitly added. No artist, date, credits, lyrics
or artwork have been supplied.

The Music page’s HTML5 player uses
`music/groovy-town.mp3`, with `controls` and `preload="none"`. Do not autoplay.
The MP3 is connected to the Music room; it is included in the static build.
