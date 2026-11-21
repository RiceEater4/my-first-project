"""Script for 'What If Dad Jokes Were Bad On Purpose?' (Jett). Younger-sibling v2 order + open-loop subscribe.
Source: Marc Hye-Knudsen (Aarhus University) - first academic article on dad jokes (2021) + 2023 The Psychologist
piece: dad jokes as fatherly teasing; the groan is the goal ("weaponized anti-humor"); playful teasing that pokes
kids' egos without crossing a line may help them handle embarrassment (an argument, not a large experiment)."""
LINES = [
    ("Ever wondered why your dad tells the...", "Ever wondered why your dad tells the...", ('DAD',)),
    ("WORST jokes?!", "[shouting] WORST jokes?!", ('WORST',)),
    ("Hi hungry, I'm Dad. You groan. He laughs. Every. Single. Time.", "\"Hi hungry, I'm Dad.\" You groan. [laughs] He laughs. Every. Single. Time.", ('DAD', 'GROAN', 'EVERY')),
    ("So are dads just bad at jokes? A researcher looked into it... and nope. It's on purpose. The groan IS the joke. He calls it weaponized anti-humor.", "So are dads just bad at jokes? A researcher looked into it... and nope. [excited] It's on purpose. The groan IS the joke. He calls it weaponized anti-humor.", ('BAD', 'PURPOSE', 'GROAN', 'ANTI-HUMOR')),
    ("Your dad isn't failing. He's trolling you.", "[laughs] Your dad isn't failing. He's trolling you.", ('FAILING', 'TROLLING')),
    ("If your dad does this... SUBSCRIBE! 'Cause the reason why is actually kind of sweet.", "If your dad does this... [shouting] SUBSCRIBE! [excited] 'Cause the reason why is actually kind of sweet.", ('SUBSCRIBE', 'SWEET')),
    ("Dad jokes are a way of teasing you... a little bit of embarrassment, in a totally safe way. The idea is, it teaches you to handle cringe without falling apart.", "Dad jokes are a way of teasing you... a little bit of embarrassment, in a totally safe way. The idea is, it teaches you to handle cringe without falling apart.", ('TEASING', 'SAFE', 'CRINGE')),
    ("So every eye roll? That's training.", "So every eye roll? [excited] That's training.", ('EYE', 'TRAINING')),
    ("But here's the part nobody tells you...", "[intense] But here's the part nobody tells you...", ('NOBODY',)),
    ("One day... you'll start doing it too. And when your own kid groans... you'll finally get it.", "One day... you'll start doing it too. And when your own kid groans... [warmly] you'll finally get it.", ('TOO', 'GET')),
    ("Send this to your dad... or Santa's putting you on the naughty list.", "Send this to your dad... [mischievous] or Santa's putting you on the naughty list.", ('SEND', 'DAD', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "Ever wondered why | your dad tells the...",
    "WORST jokes?!",
    "Hi hungry, | I'm Dad. | You groan. | He laughs. | Every. Single. | Time.",
    "So are dads | just bad at jokes? | A researcher | looked into it... | and nope. | It's on purpose. | The groan IS the joke. | He calls it | weaponized anti-humor.",
    "Your dad isn't failing. | He's trolling you.",
    "If your dad | does this... | SUBSCRIBE! | 'Cause the reason why | is actually kind of sweet.",
    "Dad jokes are | a way of teasing you... | a little bit | of embarrassment, | in a totally safe way. | The idea is, | it teaches you | to handle cringe | without falling apart.",
    "So every eye roll? | That's training.",
    "But here's the part | nobody tells you...",
    "One day... | you'll start doing it too. | And when your own kid groans... | you'll finally get it.",
    "Send this to | your dad... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
