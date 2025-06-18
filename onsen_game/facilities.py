"""
Facilities module for the Onsen Resort Management Game.
This module handles the creation and management of different facilities at the resort.
"""

class Facility:
    """Base class for all resort facilities."""
    
    def __init__(self, name, construction_cost, maintenance_cost, staff_required):
        self.name = name
        self.construction_cost = construction_cost
        self.maintenance_cost = maintenance_cost
        self.staff_required = staff_required
        self.quality = 50  # 0-100 scale
        self.popularity = 50  # 0-100 scale
        self.is_operational = True
    
    def upgrade(self, amount):
        """Upgrade the facility quality."""
        self.quality = min(100, self.quality + amount)
        self.popularity += amount // 2
        
    def get_daily_cost(self):
        """Calculate the daily operating cost of the facility."""
        return self.maintenance_cost
    
    def get_daily_income(self, total_guests):
        """Calculate the daily income from this facility."""
        # Base implementation - override in subclasses
        return 0
    
    def __str__(self):
        """String representation of the facility."""
        status = "Operational" if self.is_operational else "Closed"
        return (f"{self.name}\n"
                f"Quality: {self.quality}/100\n"
                f"Popularity: {self.popularity}/100\n"
                f"Maintenance: ¥{self.maintenance_cost}/day\n"
                f"Staff Required: {self.staff_required}\n"
                f"Status: {status}")


class Restaurant(Facility):
    """Restaurant facility where guests can dine."""
    
    def __init__(self, name, cuisine, price_tier):
        # Price tier affects costs and income (1=budget, 2=standard, 3=premium)
        construction_cost = 200000 * price_tier
        maintenance_cost = 5000 * price_tier
        staff_required = 2 * price_tier
        
        super().__init__(name, construction_cost, maintenance_cost, staff_required)
        
        self.cuisine = cuisine
        self.price_tier = price_tier
        self.menu_items = []
        
        # Set initial values based on price tier
        self.quality = 40 + (price_tier * 10)
        self.popularity = 40 + (price_tier * 5)
        
    def get_daily_income(self, total_guests):
        """Calculate the daily income from the restaurant."""
        # Estimate what percentage of total guests will eat here
        customer_percentage = self.popularity / 200  # Max 50% of all guests
        customers = int(total_guests * customer_percentage)
        
        # Average spending per customer based on price tier
        avg_spending = 1500 * self.price_tier
        
        return customers * avg_spending
    
    def __str__(self):
        """String representation of the restaurant."""
        base_str = super().__str__()
        price_tiers = {1: "Budget", 2: "Standard", 3: "Premium"}
        return (f"{base_str}\n"
                f"Cuisine: {self.cuisine}\n"
                f"Price Tier: {price_tiers[self.price_tier]}")


class GiftShop(Facility):
    """Gift shop where guests can buy souvenirs."""
    
    def __init__(self, name, size):
        # Size affects costs and income (1=small, 2=medium, 3=large)
        construction_cost = 100000 * size
        maintenance_cost = 2000 * size
        staff_required = max(1, size - 1)  # Small=1, Medium=1, Large=2
        
        super().__init__(name, construction_cost, maintenance_cost, staff_required)
        
        self.size = size
        self.inventory = []
        
        # Set initial values based on size
        self.quality = 50
        self.popularity = 40 + (size * 5)
        
    def get_daily_income(self, total_guests):
        """Calculate the daily income from the gift shop."""
        # Estimate what percentage of total guests will shop here
        customer_percentage = self.popularity / 300  # Max 33% of all guests
        customers = int(total_guests * customer_percentage)
        
        # Average spending per customer based on quality and size
        avg_spending = 500 + (self.quality * 10) + (self.size * 500)
        
        return customers * avg_spending
    
    def __str__(self):
        """String representation of the gift shop."""
        base_str = super().__str__()
        sizes = {1: "Small", 2: "Medium", 3: "Large"}
        return (f"{base_str}\n"
                f"Size: {sizes[self.size]}")


class Accommodation(Facility):
    """Accommodation facility where guests can stay overnight."""
    
    def __init__(self, name, style, rooms, quality_level):
        # Style: Western, Japanese, Mixed
        # Quality level affects costs and income (1=budget, 2=standard, 3=luxury)
        construction_cost = 500000 + (rooms * 50000 * quality_level)
        maintenance_cost = 10000 + (rooms * 500 * quality_level)
        staff_required = 2 + (rooms // 10)
        
        super().__init__(name, construction_cost, maintenance_cost, staff_required)
        
        self.style = style
        self.rooms = rooms
        self.quality_level = quality_level
        self.occupancy_rate = 50  # Percentage of rooms occupied
        
        # Set initial values based on quality level
        self.quality = 40 + (quality_level * 15)
        self.popularity = 40 + (quality_level * 10)
        
        # Room rates based on quality level
        self.room_rate = 5000 * quality_level
        
    def get_daily_income(self, total_guests):
        """Calculate the daily income from accommodations."""
        # Calculate occupied rooms
        occupied_rooms = int(self.rooms * (self.occupancy_rate / 100))
        
        # Income from room rates
        return occupied_rooms * self.room_rate
    
    def update_occupancy(self, resort_reputation, season):
        """Update the occupancy rate based on various factors."""
        # Base occupancy from reputation and quality
        base_occupancy = (resort_reputation + self.quality) / 2
        
        # Season effects
        season_multiplier = {
            "Spring": 1.1,
            "Summer": 1.2,
            "Autumn": 1.3,
            "Winter": 1.4  # Winter is peak season for onsen resorts
        }
        
        # Calculate final occupancy
        self.occupancy_rate = min(100, base_occupancy * season_multiplier[season])
    
    def __str__(self):
        """String representation of the accommodation."""
        base_str = super().__str__()
        quality_levels = {1: "Budget", 2: "Standard", 3: "Luxury"}
        return (f"{base_str}\n"
                f"Style: {self.style}\n"
                f"Rooms: {self.rooms}\n"
                f"Quality Level: {quality_levels[self.quality_level]}\n"
                f"Room Rate: ¥{self.room_rate}/night\n"
                f"Occupancy: {self.occupancy_rate:.1f}%")


class Entertainment(Facility):
    """Entertainment facility for guests."""
    
    def __init__(self, name, type_name, size):
        # Type: Karaoke, Game Room, Spa Treatment, etc.
        # Size affects costs and capacity (1=small, 2=medium, 3=large)
        construction_cost = 150000 * size
        maintenance_cost = 3000 * size
        staff_required = size
        
        super().__init__(name, construction_cost, maintenance_cost, staff_required)
        
        self.type_name = type_name
        self.size = size
        self.fee = 1000  # Base fee for using the facility
        
        # Set initial values based on size
        self.quality = 50
        self.popularity = 45 + (size * 5)
        
    def get_daily_income(self, total_guests):
        """Calculate the daily income from the entertainment facility."""
        # Estimate what percentage of total guests will use this facility
        usage_percentage = self.popularity / 250  # Max 40% of all guests
        users = int(total_guests * usage_percentage)
        
        # Income based on users and fee
        return users * self.fee
    
    def __str__(self):
        """String representation of the entertainment facility."""
        base_str = super().__str__()
        sizes = {1: "Small", 2: "Medium", 3: "Large"}
        return (f"{base_str}\n"
                f"Type: {self.type_name}\n"
                f"Size: {sizes[self.size]}\n"
                f"Usage Fee: ¥{self.fee}")
