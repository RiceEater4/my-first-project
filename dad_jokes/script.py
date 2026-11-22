"""Script for 'What If Dad Jokes Were Bad On Purpose?' (Jett) - FLIP formula (v2).
Hook -> flip ("not unfunny, on purpose") -> name it (anti-humor) -> how it works -> the hungry joke -> punchline
-> trolling one-liner -> short subscribe -> the researcher's idea -> eye-roll training -> twist -> CTA.
Source: Marc Hye-Knudsen (Aarhus University, Denmark): dad jokes as fatherly teasing; the groan is the goal
("anti-humor"); playful teasing may help kids handle embarrassment (an argument, not a large experiment).
Narration is sped up 1.1x (pitch kept) before word timing."""
LINES = [
    ("Ever wondered why your dad tells the...", "", ('DAD',)),
    ("WORST jokes?!", "", ('WORST',)),
    ("It's not because he's unfunny. He's doing it on purpose. It's called... anti-humor.", "", ('UNFUNNY', 'PURPOSE', 'ANTI-HUMOR')),
    ("A normal joke wants you to laugh. A dad joke wants you to groan.", "", ('LAUGH', 'GROAN')),
    ("You say, Dad, I'm hungry. And he goes... Hi hungry, I'm Dad. You groan.", "", ('HUNGRY', 'DAD', 'GROAN')),
    ("That groan? That's the punchline. The worse the joke... the better it worked.", "", ('GROAN', 'PUNCHLINE', 'WORSE', 'BETTER')),
    ("Your dad isn't failing. He's trolling you.", "", ('FAILING', 'TROLLING')),
    ("Got a dad like this? SUBSCRIBE! The reason's sweet.", "", ('SUBSCRIBE', 'SWEET')),
    ("A researcher in Denmark actually studied dad jokes. His idea? Dad jokes are a way of teasing you... a little bit of embarrassment, in a totally safe way. The idea is, it teaches you to handle cringe without falling apart.", "", ('DENMARK', 'TEASING', 'SAFE', 'CRINGE')),
    ("So every eye roll? That's training.", "", ('EYE', 'TRAINING')),
    ("But here's the part nobody tells you...", "", ('NOBODY',)),
    ("One day... you'll start doing it too. And when your own kid groans... you'll finally get it.", "", ('TOO', 'GET')),
    ("Send this to your dad... or Santa's putting you on the naughty list.", "", ('SEND', 'DAD', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "Ever wondered why | your dad tells the...",
    "WORST jokes?!",
    "It's not because | he's unfunny. | He's doing it | on purpose. | It's called... | anti-humor.",
    "A normal joke | wants you to laugh. | A dad joke | wants you to groan.",
    "You say, | Dad, I'm hungry. | And he goes... | Hi hungry, | I'm Dad. | You groan.",
    "That groan? | That's the punchline. | The worse the joke... | the better it worked.",
    "Your dad isn't failing. | He's trolling you.",
    "Got a dad | like this? | SUBSCRIBE! | The reason's sweet.",
    "A researcher in Denmark | actually studied | dad jokes. | His idea? | Dad jokes are | a way of teasing you... | a little bit | of embarrassment, | in a totally safe way. | The idea is, | it teaches you | to handle cringe | without falling apart.",
    "So every eye roll? | That's training.",
    "But here's the part | nobody tells you...",
    "One day... | you'll start doing it too. | And when your own kid groans... | you'll finally get it.",
    "Send this to | your dad... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
