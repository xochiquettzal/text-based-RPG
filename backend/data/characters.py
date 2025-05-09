# -*- coding: utf-8 -*-

# --- Player Character Template ---
player_character_template = {
    "name": "Oyuncu",
    "class": None,
    "world_id": None,
    "world_name_display": None,
    "stats": {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    },
    "inventory": [],
    "skills": [],
    "health": 100, 
    "current_location_id": None, 
    "history": [] 
}

# --- Class/Faction Base Stats & Skills ---
# Keys MUST match the race/faction IDs used elsewhere (HTML data attributes, scenarios)
CLASS_BASE_STATS = {
    "dark_fantasy": {
        "ashen_legion": {"strength": 14, "constitution": 15, "dexterity": 8, "intelligence": 7, "wisdom": 9, "charisma": 6, "skills": ["Ölümsüz Saldırı"]},
        "shadow_syndicate": {"strength": 8, "dexterity": 14, "constitution": 9, "intelligence": 13, "wisdom": 10, "charisma": 12, "skills": ["Gizli Hançer"]},
        "primordial_cult": {"strength": 11, "constitution": 12, "dexterity": 9, "intelligence": 8, "wisdom": 14, "charisma": 7, "skills": ["Kaos Büyüsü"]}
    },
    "animal_kingdom": {
        "vargar": {"strength": 14, "dexterity": 12, "constitution": 13, "intelligence": 8, "wisdom": 11, "charisma": 10, "skills": ["Sürü Saldırısı"]},
        "vulpex": {"strength": 7, "dexterity": 14, "constitution": 9, "intelligence": 15, "wisdom": 10, "charisma": 11, "skills": ["Tuzak Kurma"]},
        "noctis": {"strength": 6, "dexterity": 10, "constitution": 8, "intelligence": 14, "wisdom": 15, "charisma": 9, "skills": ["Kehanet Fısıltısı"]},
        "leporim": {"strength": 8, "dexterity": 12, "constitution": 10, "intelligence": 10, "wisdom": 9, "charisma": 13, "skills": ["Kaçış Ustası"]}
    }
}

# Helper function (optional)
def get_class_base_stats(world_id: str, class_id: str) -> dict:
    """Retrieves base stats and skills for a given class/faction in a world."""
    return CLASS_BASE_STATS.get(world_id, {}).get(class_id, {})
