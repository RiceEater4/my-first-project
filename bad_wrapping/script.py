"""Script for 'What If Bad Gift Wrapping Made You a Genius?' (narrated by Jett).
(caption text = exactly what is said, text sent to the voice with acting tags, highlight words)
Study: Rixom, Mas & Rixom (2020), 'Presentation matters: The effect of wrapping neatness on gift attitudes',
Journal of Consumer Psychology 30(2). Same gift wrapped neatly vs sloppily: from a friend, the sloppy one was liked
more; neat wrapping raised expectations the gift then failed to meet, sloppy wrapping lowered them so the gift beat
them. From an acquaintance, the neat one was liked more (neatness read as a sign of how much they value you)."""
LINES = [
    ("People who wrap presents badly...", "People who wrap presents badly...", ('BADLY',)),
    ("are GENIUSES!", "[shouting] are GENIUSESSS!", ('GENIUSES',)),
    ("Meet Tinsel. Tinsel wraps like a raccoon in a hurry.", "Meet Tinsel. Tinsel wraps like a raccoon... in a hurry.", ('TINSEL', 'RACCOON')),
    ("Tape everywhere. Paper ripped. The bow? Somewhere in there.", "Tape everywhere. Paper ripped. The bow? [laughs] Somewhere in there.", ('TAPE', 'RIPPED', 'BOW')),
    ("And then there's Holly. Holly's gifts look like they came from a fancy store.", "And then there's Holly. Holly's gifts look like they came from a fancy store.", ('HOLLY', 'FANCY')),
    ("Everyone thinks Holly wins Christmas.", "Everyone thinks Holly wins Christmas.", ('WINS',)),
    ("But scientists actually tested this. Same gift. One wrapped neat, one wrapped sloppy.", "But scientists actually tested this. Same gift. One wrapped neat... one wrapped sloppy.", ('TESTED', 'NEAT', 'SLOPPY')),
    ("And people liked the sloppy gift more.", "[excited] And people liked the sloppy gift MORE.", ('SLOPPY', 'MORE')),
    ("Here's why. A perfect wrap makes you expect something amazing...", "Here's why. A perfect wrap makes you expect something amazing...", ('PERFECT', 'AMAZING')),
    ("so when it's just a mug, you're disappointed.", "so when it's just a mug... you're disappointed.", ('MUG', 'DISAPPOINTED')),
    ("But a messy wrap lowers your expectations. So the gift feels better than you thought.", "But a messy wrap lowers your expectations. [excited] So the gift feels better than you thought.", ('LOWERS', 'BETTER')),
    ("So what if Santa found out? Tinsel just became head wrapper.", "So what if Santa found out? [excited] Tinsel just became head wrapper.", ('SANTA', 'HEAD')),
    ("But here's the part nobody tells you...", "[intense] But here's the part nobody tells you...", ('NOBODY',)),
    ("It only works with your friends and family.", "It only works with your friends and family.", ('FRIENDS', 'FAMILY')),
    ("Giving a gift to your boss? Wrap it perfect. To them, a neat wrap means you care.", "Giving a gift to your boss? Wrap it perfect. To them, a neat wrap means you care.", ('BOSS', 'PERFECT', 'CARE')),
    ("So Tinsel wraps for the family, Holly wraps for the boss, and everybody wins.", "So Tinsel wraps for the family... Holly wraps for the boss... [excited] and everybody wins.", ('FAMILY', 'BOSS', 'EVERYBODY')),
    ("Tag the worst wrapper you know... and subscribe, or Santa's putting you on the naughty list.", "Tag the worst wrapper you know... [mischievous] and subscribe, or Santa's putting you on the naughty list.", ('TAG', 'SUBSCRIBE', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "People who | wrap presents badly...",
    "are GENIUSES!",
    "Meet Tinsel. | Tinsel wraps | like a raccoon | in a hurry.",
    "Tape everywhere. | Paper ripped. | The bow? | Somewhere in there.",
    "And then | there's Holly. | Holly's gifts look | like they came | from a fancy store.",
    "Everyone thinks | Holly wins Christmas.",
    "But scientists | actually tested this. | Same gift. | One wrapped neat, | one wrapped sloppy.",
    "And people liked | the sloppy gift more.",
    "Here's why. | A perfect wrap | makes you expect | something amazing...",
    "so when it's | just a mug, | you're disappointed.",
    "But a messy wrap | lowers your expectations. | So the gift | feels better | than you thought.",
    "So what if | Santa found out? | Tinsel just became | head wrapper.",
    "But here's the part | nobody tells you...",
    "It only works | with your friends | and family.",
    "Giving a gift | to your boss? | Wrap it perfect. | To them, | a neat wrap | means you care.",
    "So Tinsel wraps | for the family, | Holly wraps | for the boss, | and everybody wins.",
    "Tag the worst wrapper | you know... | and subscribe, | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
