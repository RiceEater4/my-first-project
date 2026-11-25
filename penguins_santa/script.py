"""Script for 'What If Penguins Met Santa?' (narrated by Jett).
Each line: (caption text = exactly what is said, text sent to the voice with acting tags, highlight words).
Facts: polar bears live only in the Arctic; almost all penguins live south of the equator, so they never
meet in the wild. Antarctic penguins have almost no land predators and show little fear of things walking up.
Penguins walk ~2 km/h; polar bears can run ~40 km/h. Penguins swim fast. The great auk was a flightless,
black-and-white North Atlantic seabird that sailors called "penguin"; the last pair was killed in 1844 and
the southern birds inherited the name."""
LINES = [
    ("Penguins have never seen a polar bear.", "Penguins have never seen a polar bear.", ('NEVER', 'POLAR')),
    ("WHAAAAT?!", "[shouting] WHAAAAT?!", ('WHAAAAT',)),
    ("But every Christmas card puts them together. Right next to Santa.", "[excited] But every Christmas card puts them together. Right next to Santa.", ('CHRISTMAS', 'SANTA')),
    ("Here's the thing. Polar bears live at the top of the world... in the Arctic.", "Here's the thing. Polar bears live at the top of the world... in the Arctic.", ('TOP', 'ARCTIC')),
    ("Penguins live at the bottom. Almost all of them, south of the equator.", "Penguins live at the bottom. Almost all of them, south of the equator.", ('BOTTOM', 'SOUTH')),
    ("The whole planet is between them.", "[intense] The whole planet is between them.", ('PLANET',)),
    ("So what if a penguin moved up north... to meet Santa?", "[excited] So what if a penguin moved up north... to meet Santa?", ('NORTH', 'SANTA')),
    ("Penguins grew up with almost no predators on land. So they're not scared of things walking up to them.", "Penguins grew up with almost no predators on land. So they're not scared of things walking up to them.", ('PREDATORS', 'SCARED')),
    ("Even a polar bear.", "[intense] Even a polar bear.", ('POLAR', 'BEAR')),
    ("On land, a penguin waddles about two kilometers an hour. A polar bear runs forty.", "On land, a penguin waddles about two kilometers an hour. [intense] A polar bear runs forty.", ('TWO', 'FORTY')),
    ("RUN, BUDDY!", "[shouting] RUN, BUDDY!", ('RUN',)),
    ("His only chance is the water. Underwater, penguins are rockets.", "His only chance is the water. [excited] Underwater, penguins are rockets.", ('WATER', 'ROCKETS')),
    ("But plot twist... the north DID have a penguin.", "But plot twist... [shouting] the north DID have a penguin.", ('TWIST', 'DID')),
    ("The great auk. Black and white, couldn't fly, swam like a rocket. Sailors called it the penguin.", "The great auk. Black and white, couldn't fly, swam like a rocket. Sailors called it... the penguin.", ('AUK', 'PENGUIN')),
    ("Then hunters wiped it out. The last pair was killed in 1844.", "Then hunters wiped it out. The last pair was killed in eighteen forty-four.", ('WIPED', '1844')),
    ("So the birds down south got its name.", "So the birds down south... got its name.", ('NAME',)),
    ("Santa never met a penguin... but the north used to have its very own. Merry Christmas.", "Santa never met a penguin... but the north used to have its very own. [excited] Merry Christmas.", ('NEVER', 'OWN', 'CHRISTMAS')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "Penguins have never | seen a polar bear.",
    "WHAAAAT?!",
    "But every Christmas card | puts them together. | Right next to Santa.",
    "Here's the thing. | Polar bears live | at the top of the world... | in the Arctic.",
    "Penguins live | at the bottom. | Almost all of them, | south of the equator.",
    "The whole planet | is between them.",
    "So what if | a penguin moved up north... | to meet Santa?",
    "Penguins grew up | with almost no predators | on land. | So they're not scared | of things walking up | to them.",
    "Even a polar bear.",
    "On land, | a penguin waddles | about two kilometers | an hour. | A polar bear | runs forty.",
    "RUN, BUDDY!",
    "His only chance | is the water. | Underwater, | penguins are rockets.",
    "But plot twist... | the north DID | have a penguin.",
    "The great auk. | Black and white, | couldn't fly, | swam like a rocket. | Sailors called it | the penguin.",
    "Then hunters | wiped it out. | The last pair | was killed in 1844.",
    "So the birds down south | got its name.",
    "Santa never | met a penguin... | but the north | used to have its very own. | Merry Christmas.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
