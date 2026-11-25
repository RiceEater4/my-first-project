"""Script for 'What If Staying Home Made You Better?' / Huss Huss Huss (Jett) - FLIP formula, roast hook.
Hook -> flip (not a loser) -> name it (deliberate practice) -> how -> one-liner -> short subscribe -> the study
-> practicing alone -> what it means -> twist (only counts if it's hard) -> what to do -> CTA.
Source: Ericsson, Krampe & Tesch-Romer (1993), Berlin music academy violinists: best violinists ~10,000 hours of
practice by age 20, about double the future music teachers; practice alone rated the most relevant activity.
Narration is sped up 1.1-1.15x (pitch kept) before word timing."""
LINES = [
    ("Everybody in this town goes out partying except you, because you have NO FRIENDS...", "", ('PARTYING', 'YOU', 'FRIENDS')),
    ("HUSS! HUSS! HUUUUSSS!!!", "", ('HUSS', 'HUUUUSSS')),
    ("It's not because you're a loser. You're doing exactly what the best in the world did. It's called... deliberate practice.", "", ('LOSER', 'BEST', 'DELIBERATE', 'PRACTICE')),
    ("Not playing for fun. Practicing the stuff you're BAD at, alone, over and over... until your brain rewires itself.", "", ('BAD', 'ALONE', 'REWIRES')),
    ("They're making memories. You're making a highlight reel.", "", ('MEMORIES', 'HIGHLIGHT')),
    ("Grinding alone? SUBSCRIBE! HUSS! HUSS! The proof is crazy.", "", ('SUBSCRIBE', 'HUSS', 'CRAZY')),
    ("In 1993, scientists studied violin students at a top music school in Berlin. By age 20, the best ones had practiced about 10,000 hours... twice as much as the ones who ended up as music teachers.", "", ('1993', 'VIOLIN', 'BERLIN', '10000', 'TWICE')),
    ("And the thing they said helped the most? Practicing ALONE.", "", ('MOST', 'ALONE')),
    ("So every night you stayed in while everyone went out... those are hours they'll never get back.", "", ('NIGHT', 'NEVER')),
    ("But here's the part nobody tells you... it only counts if it's hard. Ten thousand hours of the easy stuff? Does nothing.", "", ('NOBODY', 'HARD', 'EASY', 'NOTHING')),
    ("So next time they all go out... pick the thing you suck at. And go. Huss. Huss. Huss.", "", ('SUCK', 'GO', 'HUSS')),
    ("Send this to the friend who never comes out... or Santa's putting you on the naughty list.", "", ('SEND', 'NEVER', 'NAUGHTY')),
]
TTS = ""
CAPTION_BREAKS = [
    "Everybody in this town | goes out partying | except you, | because you have | NO FRIENDS...",
    "HUSS! | HUSS! | HUUUUSSS!!!",
    "It's not because | you're a loser. | You're doing exactly | what the best | in the world did. | It's called... | deliberate practice.",
    "Not playing for fun. | Practicing the stuff | you're BAD at, | alone, | over and over... | until your brain | rewires itself.",
    "They're making memories. | You're making | a highlight reel.",
    "Grinding alone? | SUBSCRIBE! | HUSS! HUSS! | The proof is crazy.",
    "In 1993, | scientists studied | violin students | at a top music school | in Berlin. | By age 20, | the best ones | had practiced | about 10,000 hours... | twice as much | as the ones | who ended up | as music teachers.",
    "And the thing | they said | helped the most? | Practicing ALONE.",
    "So every night | you stayed in | while everyone went out... | those are hours | they'll never get back.",
    "But here's the part | nobody tells you... | it only counts | if it's hard. | Ten thousand hours | of the easy stuff? | Does nothing.",
    "So next time | they all go out... | pick the thing | you suck at. | And go. | Huss. Huss. Huss.",
    "Send this to | the friend | who never comes out... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
