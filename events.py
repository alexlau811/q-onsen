"""
Events module for the Onsen Resort Management Game.
This module handles weather and random events that affect the resort.
"""

import random

class Weather:
    """Class to handle weather simulation."""
    
    def __init__(self):
        self.conditions = "Clear"
        self.temperature = 20  # Celsius
        self.season = "Spring"
    
    def update(self, season):
        """Update the weather based on season and randomness."""
        self.season = season
        
        # Base temperature by season
        base_temps = {
            "Spring": 15,
            "Summer": 28,
            "Autumn": 18,
            "Winter": 5
        }
        
        # Random variation
        variation = random.randint(-5, 5)
        self.temperature = base_temps[season] + variation
        
        # Weather conditions based on season and randomness
        weather_chances = {
            "Spring": {"Clear": 0.5, "Cloudy": 0.3, "Rain": 0.2},
            "Summer": {"Clear": 0.6, "Cloudy": 0.2, "Rain": 0.15, "Storm": 0.05},
            "Autumn": {"Clear": 0.4, "Cloudy": 0.3, "Rain": 0.2, "Fog": 0.1},
            "Winter": {"Clear": 0.3, "Cloudy": 0.3, "Snow": 0.3, "Blizzard": 0.1}
        }
        
        # Select weather condition
        rand = random.random()
        cumulative = 0
        for condition, chance in weather_chances[season].items():
            cumulative += chance
            if rand <= cumulative:
                self.conditions = condition
                break
    
    def get_guest_impact(self):
        """Calculate how the weather impacts guest numbers."""
        # Base multiplier
        multiplier = 1.0
        
        # Adjust based on weather conditions
        if self.conditions == "Clear":
            multiplier *= 1.2
        elif self.conditions == "Cloudy":
            multiplier *= 1.0
        elif self.conditions == "Rain":
            multiplier *= 0.8
        elif self.conditions == "Storm":
            multiplier *= 0.5
        elif self.conditions == "Snow":
            multiplier *= 1.1  # Snow can be attractive for onsen
        elif self.conditions == "Blizzard":
            multiplier *= 0.6
        elif self.conditions == "Fog":
            multiplier *= 0.9
        
        # Extreme temperatures reduce visitors
        if self.temperature > 35 or self.temperature < -5:
            multiplier *= 0.7
        
        return multiplier
    
    def __str__(self):
        """String representation of the weather."""
        return f"{self.conditions}, {self.temperature}°C"


class Event:
    """Class for random events that can occur at the resort."""
    
    def __init__(self, name, description, effect_description, effect_function):
        self.name = name
        self.description = description
        self.effect_description = effect_description
        self.effect_function = effect_function
    
    def apply(self, resort):
        """Apply the event's effects to the resort."""
        self.effect_function(resort)
        return self.effect_description
    
    def __str__(self):
        """String representation of the event."""
        return f"{self.name}: {self.description}"


class EventManager:
    """Class to manage and trigger random events."""
    
    def __init__(self):
        self.events = self._create_events()
    
    def _create_events(self):
        """Create a list of possible random events."""
        events = []
        
        # Positive events
        events.append(Event(
            "Celebrity Visit",
            "A famous celebrity has visited your onsen!",
            "Reputation increased and more guests are coming!",
            lambda resort: setattr(resort, 'reputation', min(100, resort.reputation + 10))
        ))
        
        events.append(Event(
            "Travel Magazine Feature",
            "Your onsen was featured in a popular travel magazine!",
            "Reputation increased significantly!",
            lambda resort: setattr(resort, 'reputation', min(100, resort.reputation + 15))
        ))
        
        events.append(Event(
            "Local Festival",
            "A local festival is bringing more tourists to the area!",
            "Expect more guests for the next few days!",
            lambda resort: setattr(resort, 'guests', int(resort.guests * 1.5))
        ))
        
        events.append(Event(
            "Hot Spring Quality Improved",
            "The mineral content of your hot spring has naturally improved!",
            "Guest satisfaction has increased!",
            lambda resort: self._improve_pools(resort)
        ))
        
        # Negative events
        events.append(Event(
            "Plumbing Issue",
            "There's a problem with the hot spring plumbing!",
            "Repairs will cost money and temporarily reduce guest satisfaction.",
            lambda resort: self._plumbing_issue(resort)
        ))
        
        events.append(Event(
            "Health Inspection",
            "A surprise health inspection has found some issues.",
            "You must pay a fine and fix the problems.",
            lambda resort: setattr(resort, 'money', resort.money - 10000)
        ))
        
        events.append(Event(
            "Staff Conflict",
            "There's a conflict among your staff members.",
            "Staff happiness has decreased.",
            lambda resort: self._staff_conflict(resort)
        ))
        
        events.append(Event(
            "Competing Onsen Opened",
            "A new onsen resort has opened nearby.",
            "You might see fewer guests for a while.",
            lambda resort: setattr(resort, 'reputation', max(0, resort.reputation - 5))
        ))
        
        # Neutral or mixed events
        events.append(Event(
            "Travel Blogger Visit",
            "A popular travel blogger is visiting your onsen!",
            "Their review could help or hurt your reputation...",
            lambda resort: self._blogger_review(resort)
        ))
        
        events.append(Event(
            "Weather Phenomenon",
            "Unusual weather has affected the local area.",
            "This could change guest patterns temporarily.",
            lambda resort: None  # Effect handled by weather system
        ))
        
        return events
    
    def _improve_pools(self, resort):
        """Improve the quality of all pools."""
        for pool in resort.pools:
            pool.popularity = min(100, pool.popularity + 5)
    
    def _plumbing_issue(self, resort):
        """Handle a plumbing issue event."""
        repair_cost = random.randint(5000, 20000)
        resort.money -= repair_cost
        
        # Affect a random pool if any exist
        if resort.pools:
            pool = random.choice(resort.pools)
            pool.cleanliness = max(0, pool.cleanliness - 30)
    
    def _staff_conflict(self, resort):
        """Handle a staff conflict event."""
        for staff in resort.staff:
            staff.happiness = max(0, staff.happiness - random.randint(5, 15))
    
    def _blogger_review(self, resort):
        """Handle a travel blogger review event."""
        # Quality affects the review
        quality_factors = [
            len(resort.pools) > 0,
            len(resort.facilities) > 0,
            resort.reputation > 50,
            any(pool.cleanliness > 70 for pool in resort.pools) if resort.pools else False
        ]
        
        # Count positive factors
        positive_count = sum(1 for factor in quality_factors if factor)
        
        # Determine review outcome
        if positive_count >= 3:
            # Good review
            resort.reputation = min(100, resort.reputation + random.randint(5, 10))
        elif positive_count <= 1:
            # Bad review
            resort.reputation = max(0, resort.reputation - random.randint(5, 10))
    
    def trigger_random_event(self, resort, chance=0.2):
        """Possibly trigger a random event with the given chance."""
        if random.random() < chance:
            event = random.choice(self.events)
            effect_description = event.apply(resort)
            return (event.name, event.description, effect_description)
        return None
