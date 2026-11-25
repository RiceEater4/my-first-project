"""Script for 'What If Santa Actually Flew That Fast?' (narrated by Jett).
(caption text = exactly what is said (numbers as digits), text sent to the voice with acting tags, highlight words)
Facts / estimates: ~2 billion children under 15; roughly a third in Christian households, ~2.5 kids per home -> about
200 million homes. Time zones give Santa about 31 hours (classic estimate) -> ~1,800 homes per second. With homes
roughly half a kilometre apart that is ~100 million km -> ~1,000 km/s, about 3,000x the speed of sound (343 m/s).
Meteors burn up entering the atmosphere at about 11-70 km/s (20 km/s typical). Stopping from 1,000 km/s in a fraction
of a millisecond = hundreds of millions of g; fighter pilots black out around 9 g. NC State engineering professor
Larry Silverberg suggested Santa could use 'relativity clouds' to stretch time, giving him months to deliver."""
LINES = [
    ("If Santa delivered every present in one night... he'd explode.", "If Santa delivered every present in one night... he'd explode.", ('EXPLODE',)),
    ("WHAAAAT?!", "[shouting] WHAAAAT?!", ('WHAAAAT',)),
    ("Here's the math. Santa has to visit around 200 million homes.", "Here's the math. Santa has to visit around two hundred million homes.", ('200', 'MILLION')),
    ("Thanks to time zones, he gets 31 hours.", "Thanks to time zones, he gets thirty-one hours.", ('31',)),
    ("That's almost 1,800 houses every second.", "[excited] That's almost eighteen hundred houses... every second.", ('1,800', 'SECOND')),
    ("To pull that off, the sleigh has to fly 1,000 kilometers per second.", "To pull that off, the sleigh has to fly one thousand kilometers per second.", ('1,000',)),
    ("That's 3,000 times the speed of sound.", "[intense] That's three thousand times the speed of sound.", ('3,000', 'SOUND')),
    ("Meteors burn up at 20 kilometers per second. Santa's going 50 times faster.", "Meteors burn up at twenty kilometers per second. [excited] Santa's going fifty times faster.", ('BURN', '50')),
    ("So the reindeer catch fire, and burn up in a split second.", "So the reindeer catch fire... and burn up in a split second.", ('FIRE',)),
    ("And every stop hits Santa with millions of g's. Fighter pilots black out at 9.", "And every stop hits Santa with millions of g's. Fighter pilots black out at nine.", ('MILLIONS', '9')),
    ("Santa gets squished flat. Like a pancake.", "[excited] Santa gets squished flat. Like a pancake.", ('FLAT', 'PANCAKE')),
    ("Oh, and every house gets a sonic boom that shatters the windows.", "Oh, and every house gets a sonic boom... that shatters the windows.", ('BOOM', 'SHATTERS')),
    ("But plot twist... a real physics professor says Santa can do it.", "But plot twist... [excited] a real physics professor says Santa can do it.", ('TWIST', 'PROFESSOR')),
    ("Santa could use relativity to stretch time. For us, it's one night. For Santa, it's months.", "Santa could use relativity to stretch time. For us, it's one night. [excited] For Santa... it's months.", ('TIME', 'MONTHS')),
    ("So Santa isn't just magic... he's the smartest scientist alive.", "So Santa isn't just magic... he's the smartest scientist alive.", ('MAGIC', 'SCIENTIST')),
    ("Comment how you think Santa does it... and subscribe, or Santa's putting you on the naughty list.", "Comment how YOU think Santa does it... [mischievous] and subscribe, or Santa's putting you on the naughty list.", ('COMMENT', 'SUBSCRIBE', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "If Santa delivered | every present | in one night... | he'd explode.",
    "WHAAAAT?!",
    "Here's the math. | Santa has to visit | around 200 million homes.",
    "Thanks to time zones, | he gets 31 hours.",
    "That's almost | 1,800 houses | every second.",
    "To pull that off, | the sleigh has to fly | 1,000 kilometers | per second.",
    "That's 3,000 times | the speed of sound.",
    "Meteors burn up | at 20 kilometers | per second. | Santa's going | 50 times faster.",
    "So the reindeer | catch fire, | and burn up | in a split second.",
    "And every stop | hits Santa | with millions of g's. | Fighter pilots | black out at 9.",
    "Santa gets | squished flat. | Like a pancake.",
    "Oh, and every house | gets a sonic boom | that shatters | the windows.",
    "But plot twist... | a real physics professor | says Santa can do it.",
    "Santa could use | relativity | to stretch time. | For us, | it's one night. | For Santa, | it's months.",
    "So Santa | isn't just magic... | he's the smartest | scientist alive.",
    "Comment how you think | Santa does it... | and subscribe, | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
