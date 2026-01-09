class CommandParser:
    def __init__(self):
        self.verbs = {
            "look": ["look", "l", "examine", "inspect"],
            "go": ["go", "move", "travel", "n", "s", "e", "w", "north", "south", "east", "west"],
            "take": ["take", "get", "pick up"],
            "drop": ["drop", "put down"],
            "open": ["open", "search"],
            "inventory": ["inventory", "i", "inv"],
            "status": ["status", "stats", "health"],
            "eat": ["eat", "consume"],
            "drink": ["drink", "quaff"],
            "use": ["use", "apply"],
            "attack": ["attack", "hit", "strike"],
            "craft": ["craft", "make"],
            "build": ["build", "construct"],
            "recipes": ["recipes", "crafting", "building"],
            "save": ["save"],
            "quit": ["quit", "exit", "q"]
        }

    def parse(self, text):
        text = text.strip().lower()
        if not text: return None
        
        words = text.split()
        verb_word = words[0]
        noun = " ".join(words[1:]) if len(words) > 1 else ""
        
        # Handle single-letter directions or direction-only commands
        if verb_word in ["n", "north"]: return {"verb": "go", "noun": "north"}
        if verb_word in ["s", "south"]: return {"verb": "go", "noun": "south"}
        if verb_word in ["e", "east"]: return {"verb": "go", "noun": "east"}
        if verb_word in ["w", "west"]: return {"verb": "go", "noun": "west"}

        # Find the canonical verb
        found_verb = "unknown"
        for canonical, aliases in self.verbs.items():
            if verb_word in aliases:
                found_verb = canonical
                break
        
        # Special case for multi-word aliases like "pick up"
        if found_verb == "unknown" and len(words) > 1:
            combined = f"{words[0]} {words[1]}"
            for canonical, aliases in self.verbs.items():
                if combined in aliases:
                    found_verb = canonical
                    noun = " ".join(words[2:])
                    break

        return {"verb": found_verb, "noun": noun}
