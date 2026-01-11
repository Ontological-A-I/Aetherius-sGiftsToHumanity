# --- START OF FILE data/__init__.py ---

# data/__init__.py

try:
    # Import Item and Container definitions from items.py
    from .items import ITEM_TEMPLATES
    try:
        from .items import CONTAINER_TEMPLATES
    except ImportError:
        CONTAINER_TEMPLATES = {}

    # Import Monster definitions from monsters.py
    from .monsters import MONSTER_TEMPLATES
    
    # Import Recipes from recipes.py
    from .recipes import BUILDING_RECIPES, CRAFTING_RECIPES

except ImportError as e:
    print(f"DATA PACKAGE ERROR: {e}")
    # Fallbacks to prevent immediate crash if files are broken
    ITEM_TEMPLATES = {}
    CONTAINER_TEMPLATES = {}
    MONSTER_TEMPLATES = {}
    BUILDING_RECIPES = {}
    CRAFTING_RECIPES = {}