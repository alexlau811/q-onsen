"""
Onsen Pool module for the Onsen Resort Management Game.
This module handles the creation and management of different types of onsen pools.
"""

class OnsenPool:
    """Base class for all onsen pools."""
    
    def __init__(self, name, size, temperature):
        self.name = name
        self.size = size  # Small, Medium, Large
        self.temperature = temperature  # in Celsius
        self.ingredients = []  # Special minerals or ingredients
        self.cleanliness = 100  # 0-100 scale
        self.popularity = 50  # 0-100 scale
        self.construction_cost = 0
        self.maintenance_cost = 0
        
        # Set costs based on size
        if size == "Small":
            self.construction_cost = 50000
            self.maintenance_cost = 1000
            self.capacity = 10
        elif size == "Medium":
            self.construction_cost = 100000
            self.maintenance_cost = 2000
            self.capacity = 25
        elif size == "Large":
            self.construction_cost = 200000
            self.maintenance_cost = 4000
            self.capacity = 50
    
    def add_ingredient(self, ingredient):
        """Add a special ingredient to the onsen water."""
        self.ingredients.append(ingredient)
        self.popularity += ingredient.popularity_bonus
        self.maintenance_cost += ingredient.cost
        
    def clean(self):
        """Clean the onsen pool."""
        self.cleanliness = 100
        
    def get_daily_cost(self):
        """Calculate the daily operating cost of the pool."""
        # Base maintenance cost
        cost = self.maintenance_cost
        
        # Temperature maintenance cost (higher for extreme temperatures)
        temp_factor = abs(self.temperature - 40) / 10  # 40°C is optimal
        cost += int(500 * temp_factor)
        
        return cost
    
    def get_guest_satisfaction(self):
        """Calculate how satisfied guests are with this pool."""
        satisfaction = 50  # Base satisfaction
        
        # Cleanliness factor
        satisfaction += (self.cleanliness - 50) / 2
        
        # Temperature factor - people prefer 38-42°C
        if 38 <= self.temperature <= 42:
            satisfaction += 10
        else:
            satisfaction -= abs(self.temperature - 40)
        
        # Ingredient bonuses
        for ingredient in self.ingredients:
            satisfaction += ingredient.satisfaction_bonus
        
        # Crowding factor
        # This would be calculated based on actual guests using the pool
        
        return max(0, min(100, satisfaction))
    
    def __str__(self):
        """String representation of the pool."""
        return (f"{self.name} ({self.size})\n"
                f"Temperature: {self.temperature}°C\n"
                f"Cleanliness: {self.cleanliness}/100\n"
                f"Popularity: {self.popularity}/100\n"
                f"Capacity: {self.capacity} guests\n"
                f"Maintenance: ¥{self.maintenance_cost}/day")


class Ingredient:
    """Special ingredients that can be added to onsen pools."""
    
    def __init__(self, name, cost, popularity_bonus, satisfaction_bonus, description):
        self.name = name
        self.cost = cost  # Daily cost to maintain
        self.popularity_bonus = popularity_bonus  # Bonus to pool popularity
        self.satisfaction_bonus = satisfaction_bonus  # Bonus to guest satisfaction
        self.description = description
    
    def __str__(self):
        """String representation of the ingredient."""
        return (f"{self.name}\n"
                f"Cost: ¥{self.cost}/day\n"
                f"Popularity: +{self.popularity_bonus}\n"
                f"Guest Satisfaction: +{self.satisfaction_bonus}\n"
                f"Description: {self.description}")


# Pre-defined ingredients
INGREDIENTS = [
    Ingredient("Sulfur", 500, 5, 3, 
               "Sulfur-rich waters are known for treating skin conditions."),
    Ingredient("Iron", 600, 3, 5, 
               "Iron-rich waters are said to be good for anemia and fatigue."),
    Ingredient("Sodium Bicarbonate", 400, 4, 4, 
               "These waters leave skin feeling smooth and are called 'Baking Soda Springs'."),
    Ingredient("Radium", 1000, 10, -5, 
               "Historically popular but now known to be harmful. High popularity but reduces satisfaction."),
    Ingredient("Green Tea Extract", 800, 8, 7, 
               "A luxurious addition that gives the water a pleasant aroma and skin benefits."),
    Ingredient("Sake", 1200, 15, 10, 
               "Bathing in sake is a premium experience that's very popular with guests."),
    Ingredient("Hydrogen Carbonate", 700, 6, 6, 
               "Known as 'Beauty Baths' for making skin smooth and beautiful."),
    Ingredient("Alum", 500, 4, 3, 
               "Creates an astringent effect that tightens skin."),
]
