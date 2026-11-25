"""Script for 'What If Everyone Could See Your Fake Smile?' (narrated by Jett). Straight-to-camera explainer.
Facts: a genuine (Duchenne) smile engages the muscles around the eyes (crinkles/crow's feet); a posed smile mostly
moves the mouth, and people can often tell them apart. Gino & Flynn (2011, J. Experimental Social Psychology,
'Give them what they want'): recipients appreciated gifts they had asked for more than unrequested ones, while givers
wrongly expected unrequested gifts to be seen as more thoughtful."""
LINES = [
    ("Ever open a gift so bad you had to fake a smile...", "Ever open a gift so bad you had to fake a smile...", ('FAKE', 'SMILE')),
    ("and it made you FURIOUS?", "[shouting] and it made you FURIOUSSS?!", ('FURIOUS',)),
    ("Picture this. Christmas morning. Your aunt hands you a gift... and she's staring right at you. Everyone's watching. And it's... a candle shaped like a cat.", "Picture this. Christmas morning. Your aunt hands you a gift... and she's staring right at you. Everyone's watching. And it's... [laughs] a candle shaped like a cat.", ('AUNT', 'STARING', 'CAT')),
    ("So you do the face. Big smile. Wow, I love it.", "So you do the face. Big smile. [sarcastic] Wow... I love it.", ('FACE', 'LOVE')),
    ("But here's the problem. Everyone can tell.", "But here's the problem. [intense] Everyone can tell.", ('EVERYONE', 'TELL')),
    ("If you've ever faked it for a gift... SUBSCRIBE!", "If you've ever faked it for a gift... [shouting] SUBSCRIBE!", ('SUBSCRIBE',)),
    ("A real smile crinkles your eyes. A fake one only moves your mouth. And people spot the difference.", "A real smile crinkles your eyes. A fake one only moves your mouth. And people spot the difference.", ('EYES', 'MOUTH')),
    ("But here's what nobody tells you. It's not your fault.", "But here's what nobody tells you... [excited] It's not your fault.", ('NOBODY', 'FAULT')),
    ("Scientists found people pick surprise gifts because they think surprises look more thoughtful...", "Scientists found people pick surprise gifts because they think surprises look more thoughtful...", ('SURPRISE', 'THOUGHTFUL')),
    ("but people actually love the gifts they asked for way more.", "[excited] but people actually love the gifts they asked for way more.", ('ASKED', 'MORE')),
    ("So you're not ungrateful. You just got a cat candle.", "So you're not ungrateful. [laughs] You just got a cat candle.", ('UNGRATEFUL', 'CAT')),
    ("Here's the genius move. Make a wish list, and send it to everyone.", "Here's the genius move. Make a wish list... [excited] and send it to everyone.", ('GENIUS', 'WISH')),
    ("And if the cat candle still shows up? Smile with your eyes.", "And if the cat candle still shows up? [mischievous] Smile with your eyes.", ('EYES',)),
    ("Comment the worst gift you ever got... or Santa's putting you on the naughty list.", "Comment the worst gift you ever got... [mischievous] or Santa's putting you on the naughty list.", ('COMMENT', 'WORST', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "Ever open a gift | so bad you had to | fake a smile...",
    "and it made you | FURIOUS?",
    "Picture this. | Christmas morning. | Your aunt | hands you a gift... | and she's staring | right at you. | Everyone's watching. | And it's... | a candle | shaped like a cat.",
    "So you do the face. | Big smile. | Wow, | I love it.",
    "But here's the problem. | Everyone can tell.",
    "If you've ever faked it | for a gift... | SUBSCRIBE!",
    "A real smile | crinkles your eyes. | A fake one | only moves your mouth. | And people spot | the difference.",
    "But here's what | nobody tells you. | It's not your fault.",
    "Scientists found | people pick surprise gifts | because they think | surprises look | more thoughtful...",
    "but people actually love | the gifts they asked for | way more.",
    "So you're not ungrateful. | You just got | a cat candle.",
    "Here's the genius move. | Make a wish list, | and send it | to everyone.",
    "And if the cat candle | still shows up? | Smile with your eyes.",
    "Comment the worst gift | you ever got... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
