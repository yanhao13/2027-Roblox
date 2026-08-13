"""Generate a high-fidelity synthetic OMuleT dataset matching the paper's schema.

The real OMuleT dataset (arXiv:2411.19352) is Roblox-internal and not publicly
released. This script produces a schema-exact stand-in so the MATCHA pipeline
runs end-to-end; drop in the real files to replace it.

Outputs:
    data/omulet/game_catalog.csv   -> id,title,genre,platform,score,release_date,monthly_clicks,description
    data/omulet/requests.json      -> [{request_id, query, ground_truth_ids}]
"""
import csv
import json
import os
import random
from datetime import datetime, timedelta

random.seed(42)

GENRES = [
    "Simulation", "Adventure", "Horror", "Strategy", "FPS", "RPG", "Fighting",
    "Racing", "Sports", "Tycoon", "Obby", "Social", "Sandbox", "Puzzle",
    "Survival", "Tower Defense", "Anime", "Mystery", "Comedy", "Military", "Scary",
]
PLATFORMS = ["PC", "Mobile", "Xbox", "PlayStation"]
PLATFORM_W = [0.46, 0.30, 0.16, 0.08]

GENRE_BLURB = {
    "Simulation": "a life-sim experience where you build, decorate, and manage your own world",
    "Adventure": "an open-world adventure packed with quests, treasures, and exploration",
    "Horror": "a tense horror escape where you survive what lurks in the dark",
    "Strategy": "a deep strategy title where planning and positioning win the day",
    "FPS": "a fast-paced shooter with satisfying gunplay and competitive modes",
    "RPG": "an RPG with classes, leveling, and loot-driven progression",
    "Fighting": "a combat arena focused on combos, timing, and character mastery",
    "Racing": "a racing game with licensed-style vehicles and drift mechanics",
    "Sports": "a sports sim with team play, physics, and ranked seasons",
    "Tycoon": "a tycoon builder where you grow a business from scratch to a fortune",
    "Obby": "a platforming obstacle course testing precision and patience",
    "Social": "a hangout hub for chatting, roleplay, and mini-games with friends",
    "Sandbox": "a physics sandbox for building and tinkering with anything",
    "Puzzle": "a brain-teasing puzzle game with escalating logic challenges",
    "Survival": "a survival challenge against disasters, hunters, or the elements",
    "Tower Defense": "a tower-defense battleground to place units and repel waves",
    "Anime": "an anime-inspired battler with powers, quests, and transformations",
    "Mystery": "a social-deduction mystery where you find the culprit before it's you",
    "Comedy": "a lighthearted comedic experience full of silly gags and chaos",
    "Military": "a military roleplay of service, vehicles, and squad tactics",
    "Scary": "a jump-scare driven horror romp through haunted locations",
}

# ~120 curated real Roblox-style titles (name -> genre)
CURATED = [
    ("Adopt Me!", "Simulation"), ("Welcome to Bloxburg", "Simulation"),
    ("Pet Simulator X", "Simulation"), ("Bee Swarm Simulator", "Simulation"),
    ("Lumber Tycoon 2", "Tycoon"), ("Restaurant Tycoon 2", "Tycoon"),
    ("Theme Park Tycoon 2", "Tycoon"), ("Miner's Haven", "Tycoon"),
    ("Cruise Ship Tycoon", "Tycoon"), ("Wizard Tycoon 2", "Tycoon"),
    ("Blox Fruits", "Adventure"), ("Jailbreak", "Adventure"),
    ("Dungeon Quest", "Adventure"), ("The Wild West", "Adventure"),
    ("Dragon Adventures", "Adventure"), ("Islands", "Adventure"),
    ("Doors", "Horror"), ("Piggy", "Horror"), ("The Mimic", "Horror"),
    ("3008", "Horror"), ("Bear", "Horror"), ("Dead Silence", "Horror"),
    ("Tower Defense Simulator", "Tower Defense"), ("All Star Tower Defense", "Tower Defense"),
    ("Tower Heroes", "Tower Defense"), ("Elemental Tower Defense", "Tower Defense"),
    ("Arsenal", "FPS"), ("Phantom Forces", "FPS"), ("Bad Business", "FPS"),
    ("Counter Blox", "FPS"), ("Energy Assault", "FPS"),
    ("World Zero", "RPG"), ("Vesteria", "RPG"), ("Fantastic Frontier", "RPG"),
    ("Swordburst 2", "RPG"), ("A Universal Time", "RPG"),
    ("Anime Fighting Simulator", "Fighting"), ("The Strongest Battlegrounds", "Fighting"),
    ("Untitled Boxing Game", "Fighting"), ("Martial Arts Battle Arena", "Fighting"),
    ("Vehicle Legends", "Racing"), ("Driving Empire", "Racing"),
    ("Car Crushers 2", "Racing"), ("Midnight Racing Tokyo", "Racing"),
    ("Blade Ball", "Sports"), ("Basketball Legends", "Sports"),
    ("Soccer Legends", "Sports"), ("Football Fusion 2", "Sports"),
    ("Tower of Hell", "Obby"), ("Mega Easy Obby", "Obby"),
    ("Juke's Towers of Hell", "Obby"), ("The Really Easy Obby", "Obby"),
    ("Brookhaven", "Social"), ("MeepCity", "Social"), ("Royale High", "Social"),
    ("Club Roblox", "Social"), ("Epic Minigames", "Social"),
    ("Build a Boat for Treasure", "Sandbox"), ("Plane Crazy", "Sandbox"),
    ("Build Island", "Sandbox"), ("Scrap Mechanic Simulator", "Sandbox"),
    ("Puzzle Doors", "Puzzle"), ("Color or Die", "Puzzle"), ("Riddles", "Puzzle"),
    ("Natural Disaster Survival", "Survival"), ("Survive the Killer", "Survival"),
    ("Flee the Facility", "Survival"), ("Escape Room", "Survival"),
    ("Shindo Life", "Anime"), ("Anime Adventures", "Anime"),
    ("King Legacy", "Anime"), ("A One Piece Game", "Anime"),
    ("Murder Mystery 2", "Mystery"), ("Mystery Dungeon", "Mystery"),
    ("RoCitizens", "Comedy"), ("Funky Friday", "Comedy"),
    ("Emergency Response: Liberty County", "Military"), ("War Tycoon", "Military"),
    ("State of Anarchy", "Military"), ("Military Combat Tycoon", "Military"),
    ("Alone in a Dark House", "Scary"), ("Identity Fraud", "Scary"),
    ("The Asylum", "Scary"), ("Nightmare Mansion", "Scary"),
    ("Work at a Pizza Place", "Tycoon"), ("Super Hero Tycoon", "Tycoon"),
    ("Zombie Rush", "Survival"), ("Flee the Zombies", "Survival"),
    ("Pet Story", "Simulation"), ("My Restaurant", "Simulation"),
    ("Treasure Quest", "Adventure"), ("Pirate's Life", "Adventure"),
    ("Clone Tycoon 2", "Tycoon"), ("Boxing Simulator", "Fighting"),
    ("Rocket Racing", "Racing"), ("Speed Run 4", "Obby"),
    ("Obby Creator", "Obby"), ("Color Block", "Puzzle"),
    ("Pls Donate", "Social"), ("Emergency Hamburg", "Military"),
]

ADJECTIVES = ["Mega", "Ultra", "Epic", "Super", "Mystic", "Neon", "Cyber", "Dark",
              "Royal", "Cosmic", "Tiny", "Giant", "Savage", "Frozen", "Burning",
              "Golden", "Shadow", "Turbo", "Hyper", "Pixel"]
NOUNS = ["World", "Quest", "Adventure", "Empire", "Legends", "Arena", "Battle",
         "Escape", "Factory", "Island", "Castle", "Dungeon", "City", "Kingdom",
         "Frontier", "Saga", "Tower", "Base", "Station", "Realm"]
SUFFIXES = ["Simulator", "Tycoon", "Obby", "RP", "Clicker", "Defense", "Craft",
            "Build", "Survival", "Rush", "Party", "Story", "Escape", "Quest", "Raid"]


def _unique_name(i: int) -> str:
    a = ADJECTIVES[i % len(ADJECTIVES)]
    n = NOUNS[(i // len(ADJECTIVES)) % len(NOUNS)]
    s = SUFFIXES[(i // (len(ADJECTIVES) * len(NOUNS))) % len(SUFFIXES)]
    return f"{a} {n} {s}"


def main():
    os.makedirs("data/omulet", exist_ok=True)

    # ---- build the 2074-game catalog ----
    games = []
    seen = set()

    # curated real titles first
    for title, genre in CURATED:
        gid = f"game_{len(games) + 1:04d}"
        games.append({"id": gid, "title": title, "genre": genre})
        seen.add(title.lower())

    # fill the rest combinatorially, assigning genres round-robin
    i = 0
    while len(games) < 2074:
        name = _unique_name(i)
        i += 1
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        genre = GENRES[len(games) % len(GENRES)]
        gid = f"game_{len(games) + 1:04d}"
        games.append({"id": gid, "title": name, "genre": genre})

    # enrich with metadata
    now = datetime(2026, 8, 13)
    rows = []
    for g in games:
        platform = random.choices(PLATFORMS, weights=PLATFORM_W, k=1)[0]
        upvotes = int(random.lognormvariate(7.0, 1.6))  # popularity, long-tail
        release_date = (now - timedelta(days=random.randint(30, 2200))).strftime("%Y-%m-%d")
        score = round(random.uniform(0.55, 0.98), 3)
        blurb = GENRE_BLURB[g["genre"]]
        description = f"{g['title']} is {blurb} on Roblox."
        rows.append({
            "id": g["id"], "title": g["title"], "genre": g["genre"],
            "platform": platform, "score": score,
            "release_date": release_date, "monthly_clicks": upvotes,
            "description": description,
        })

    with open("data/omulet/game_catalog.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[+] wrote {len(rows)} games to data/omulet/game_catalog.csv")

    # ---- build the 553 requests ----
    genre_ids = {g: [] for g in GENRES}
    for r in rows:
        genre_ids[r["genre"]].append(r["id"])

    QUERY_TMPL = [
        "I want a {genre} game to play on {device}.",
        "Recommend me a {genre} game, something {adj} and fun.",
        "Looking for a {genre} game like {like}.",
        "What's a good {genre} game for {device}?",
        "Find me a {genre} game that's {adj} and not too hard.",
        "I'm bored, suggest a {genre} game I can play with friends.",
        "Give me a {genre} game that is popular and {adj}.",
    ]
    ADJ = ["chill", "intense", "casual", "addictive", "competitive", "relaxing", "fast-paced"]

    requests = []
    for idx in range(553):
        genre = random.choice(GENRES)
        device = random.choice(PLATFORMS)
        like = random.choice(rows)["title"]
        adj = random.choice(ADJ)
        query = random.choice(QUERY_TMPL).format(genre=genre.lower(), device=device, adj=adj, like=like)
        # average ~14.2 ground-truth games, drawn from the matching genre
        n_gt = int(random.lognormvariate(2.2, 0.6))
        n_gt = max(3, min(30, n_gt))
        pool = genre_ids[genre]
        gt = random.sample(pool, min(n_gt, len(pool)))
        requests.append({
            "request_id": f"req_{idx + 1:04d}",
            "query": query,
            "ground_truth_ids": gt,
        })

    with open("data/omulet/requests.json", "w") as f:
        json.dump(requests, f, ensure_ascii=False, indent=1)
    print(f"[+] wrote {len(requests)} requests to data/omulet/requests.json")


if __name__ == "__main__":
    main()
