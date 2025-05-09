# -*- coding: utf-8 -*-

# --- Player Character Template ---
player_character_template = {
    "name": "Oyuncu",
    "class": None, 
    "world_id": None, 
    "world_name_display": None, 
    "stats": {
        # Generic defaults, will be overwritten by class/faction selection
        "STR": 5, "END": 5, "WILL": 5, "ARC": 5, 
        "AGI": 5, "INS": 5, "CUN": 5, "CHA": 5, 
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
        "ashen_legion": {"STR": 8, "END": 7, "WILL": 6, "ARC": 2, "skills": ["Ölümsüz Saldırı"]},
        "shadow_syndicate": {"STR": 4, "END": 5, "WILL": 5, "ARC": 7, "skills": ["Gizli Hançer"]}, # Assuming ARC relates to cunning/forbidden knowledge
        "primordial_cult": {"STR": 5, "END": 6, "WILL": 8, "ARC": 4, "skills": ["Kaos Büyüsü"]} # Assuming WILL relates to resisting madness/channeling power
    },
    "animal_kingdom": {
        "vargar": {"STR": 7, "END": 6, "INS": 5, "AGI": 6, "skills": ["Sürü Saldırısı"]}, 
        "vulpex": {"STR": 4, "END": 5, "INS": 6, "AGI": 7, "skills": ["Tuzak Kurma"]}, 
        "noctis": {"STR": 3, "END": 4, "INS": 8, "AGI": 5, "skills": ["Kehanet Fısıltısı"]}, 
        "leporim": {"STR": 4, "END": 6, "INS": 4, "AGI": 8, "skills": ["Kaçış Ustası"]} 
        # Redefined stats for Animal Kingdom: STR, END, INS (Instinct), AGI (Agility)
        # Note: The template includes all possible stats; irrelevant ones will just keep default value if not overwritten.
        # Alternatively, the template could be minimal and stats added dynamically.
    }
}

# Helper function (optional)
def get_class_base_stats(world_id: str, class_id: str) -> dict:
    """Retrieves base stats and skills for a given class/faction in a world."""
    return CLASS_BASE_STATS.get(world_id, {}).get(class_id, {})
