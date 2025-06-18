"""
ASCII art module for the Onsen Resort Management Game.
This module provides dynamic ASCII art for various game elements.
"""

# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "blue": "\033[1;34m",     # Regular water
    "green": "\033[1;32m",    # Green tea
    "red": "\033[1;31m",      # Iron/Radium
    "yellow": "\033[1;33m",   # Sulfur
    "magenta": "\033[1;35m",  # Sake
    "cyan": "\033[1;36m",     # Sodium Bicarbonate
    "white": "\033[1;37m",    # Hydrogen Carbonate
    "gray": "\033[1;90m",     # Alum
}

# Ingredient to color mapping
INGREDIENT_COLORS = {
    "Sulfur": "yellow",
    "Iron": "red",
    "Sodium Bicarbonate": "cyan",
    "Radium": "red",
    "Green Tea Extract": "green",
    "Sake": "magenta",
    "Hydrogen Carbonate": "white",
    "Alum": "gray",
}

def get_pool_color(pool):
    """Determine the color for a pool based on its ingredients."""
    if not pool.ingredients:
        return COLORS["blue"]  # Default color for water
    
    # Use the color of the first ingredient (could be enhanced to mix colors)
    ingredient_name = pool.ingredients[0].name
    color_name = INGREDIENT_COLORS.get(ingredient_name, "blue")
    return COLORS[color_name]

def generate_onsen_ascii(pools):
    """
    Generate dynamic ASCII art for onsen pools based on the number of pools and their ingredients.
    
    Args:
        pools: List of OnsenPool objects
    
    Returns:
        String containing the ASCII art representation
    """
    if not pools:
        return "No onsen pools built yet!"
    
    # Base pool template
    small_pool = [
        "    .---.",
        "   /     \\",
        "  /       \\",
        " |    ~    |",
        " |    ♨    |",
        "  \\       /",
        "   \\_____/"
    ]
    
    medium_pool = [
        "    .-----.",
        "   /       \\",
        "  /         \\",
        " |   ~   ~   |",
        " |   ♨   ♨   |",
        " |   ~   ~   |",
        "  \\         /",
        "   \\_______/"
    ]
    
    large_pool = [
        "    .-------.",
        "   /         \\",
        "  /           \\",
        " |  ~  ~  ~  ~ |",
        " |  ♨  ♨  ♨  ♨ |",
        " |  ~  ~  ~  ~ |",
        " |             |",
        "  \\           /",
        "   \\_________/"
    ]
    
    # Determine how many pools to show per row (max 3)
    pools_per_row = min(3, len(pools))
    rows_needed = (len(pools) + pools_per_row - 1) // pools_per_row  # Ceiling division
    
    result = []
    
    # Generate the ASCII art row by row
    for row in range(rows_needed):
        start_idx = row * pools_per_row
        end_idx = min(start_idx + pools_per_row, len(pools))
        row_pools = pools[start_idx:end_idx]
        
        # Get the appropriate pool template for each pool in this row
        pool_templates = []
        for pool in row_pools:
            if pool.size == "Small":
                template = small_pool
            elif pool.size == "Medium":
                template = medium_pool
            else:  # Large
                template = large_pool
            pool_templates.append((pool, template))
        
        # Determine the height of the tallest pool in this row
        max_height = max(len(template) for _, template in pool_templates)
        
        # Build the row line by line
        for line_idx in range(max_height):
            line = ""
            for pool, template in pool_templates:
                # If this pool's template has this line, add it
                if line_idx < len(template):
                    color = get_pool_color(pool)
                    line += color + template[line_idx] + COLORS["reset"] + "  "
                else:
                    # Add spaces for shorter pools to align everything
                    line += " " * (len(template[0]) + 2)
            result.append(line)
        
        # Add a blank line between rows
        result.append("")
    
    # Add a legend for the ingredients
    if any(pool.ingredients for pool in pools):
        result.append("Legend:")
        unique_ingredients = set()
        for pool in pools:
            for ingredient in pool.ingredients:
                unique_ingredients.add(ingredient.name)
        
        for ingredient in unique_ingredients:
            color = COLORS[INGREDIENT_COLORS.get(ingredient, "blue")]
            result.append(f"{color}♨{COLORS['reset']} - {ingredient}")
    
    return "\n".join(result)

def generate_facilities_summary(facilities):
    """
    Generate a text summary of facilities.
    
    Args:
        facilities: List of Facility objects
    
    Returns:
        String containing the facilities summary
    """
    if not facilities:
        return "No facilities built yet!"
    
    # Count facilities by type
    facility_counts = {}
    for facility in facilities:
        facility_type = facility.__class__.__name__
        if facility_type in facility_counts:
            facility_counts[facility_type] += 1
        else:
            facility_counts[facility_type] = 1
    
    result = []
    for facility_type, count in facility_counts.items():
        result.append(f"{facility_type}: {count}")
    
    return "\n".join(result)

def generate_rooms_summary(facilities):
    """
    Generate a text summary of accommodation rooms.
    
    Args:
        facilities: List of Facility objects
    
    Returns:
        String containing the rooms summary
    """
    room_counts = {"Economy": 0, "Standard": 0, "Luxury": 0, "Suite": 0}
    total_capacity = 0
    
    for facility in facilities:
        if facility.__class__.__name__ == "Accommodation":
            room_type = facility.room_type
            if room_type in room_counts:
                room_counts[room_type] += facility.rooms
                total_capacity += facility.capacity
    
    if total_capacity == 0:
        return "No accommodation rooms built yet!"
    
    result = [f"Total capacity: {total_capacity} guests"]
    for room_type, count in room_counts.items():
        if count > 0:
            result.append(f"{room_type} rooms: {count}")
    
    return "\n".join(result)
