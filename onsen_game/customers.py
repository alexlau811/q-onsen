#!/usr/bin/env python3
"""
Customer module for the Onsen Resort Management Game.
Defines different customer personalities and their preferences.
"""

import random

# Customer personality types and their characteristics
PERSONALITIES = {
    "Relaxation Seeker": {
        "description": "Values peaceful atmosphere and comfort above all",
        "preferences": {
            "temperature": (38, 40),  # Preferred temperature range
            "cleanliness": 90,        # Minimum acceptable cleanliness (increased from 85)
            "staff_skill": 70,        # Minimum acceptable staff skill (increased from 60)
            "price_sensitivity": 0.8, # Lower means more sensitive to price
            "facility_importance": 0.5, # How much they care about facilities
        },
        "feedback": [
            "The water temperature was perfect for relaxation.",
            "I wish the pools were cleaner, it affected my relaxation.",
            "The staff was so attentive, I felt completely at ease.",
            "The atmosphere was too noisy for proper relaxation.",
            "This is exactly the peaceful retreat I was looking for."
        ]
    },
    "Luxury Enthusiast": {
        "description": "Expects premium service and amenities",
        "preferences": {
            "temperature": (39, 41),
            "cleanliness": 98,        # Increased from 95
            "staff_skill": 95,        # Increased from 90
            "price_sensitivity": 0.4,
            "facility_importance": 0.9,
        },
        "feedback": [
            "The service was not up to the premium standards I expect.",
            "Absolutely worth every yen - a truly luxurious experience!",
            "The facilities were impressive, but staff training needs improvement.",
            "I expect perfection at these prices, and was disappointed.",
            "A wonderful high-end experience, I'll recommend it to my circle."
        ]
    },
    "Health Conscious": {
        "description": "Focused on health benefits and natural ingredients",
        "preferences": {
            "temperature": (40, 42),
            "cleanliness": 95,        # Increased from 90
            "staff_skill": 75,        # Increased from 70
            "price_sensitivity": 0.6,
            "facility_importance": 0.7,
        },
        "feedback": [
            "I appreciated the mineral content information for each pool.",
            "The water didn't seem to have the therapeutic properties advertised.",
            "My skin feels amazing after using the special mineral pools!",
            "I was hoping for more health-focused amenities.",
            "The staff was knowledgeable about the health benefits of each pool."
        ]
    },
    "Budget Traveler": {
        "description": "Looking for good value and affordable experience",
        "preferences": {
            "temperature": (37, 41),
            "cleanliness": 80,        # Increased from 75
            "staff_skill": 55,        # Increased from 50
            "price_sensitivity": 1.0,
            "facility_importance": 0.4,
        },
        "feedback": [
            "Great value for the price, but basic amenities.",
            "Too expensive for what was offered.",
            "I found the experience affordable and satisfying.",
            "I wish there were more budget-friendly food options.",
            "A good balance of quality and affordability."
        ]
    },
    "Traditional Purist": {
        "description": "Values authentic Japanese onsen experience",
        "preferences": {
            "temperature": (41, 43),
            "cleanliness": 90,        # Increased from 85
            "staff_skill": 85,        # Increased from 80
            "price_sensitivity": 0.7,
            "facility_importance": 0.6,
        },
        "feedback": [
            "This felt like an authentic traditional onsen experience.",
            "Too commercialized, lost the traditional essence of onsen.",
            "I appreciated the respect for Japanese bathing customs.",
            "The modern additions detracted from the traditional atmosphere.",
            "A perfect balance of tradition and comfort."
        ]
    },
    "Social Butterfly": {
        "description": "Enjoys the social aspects of onsen bathing",
        "preferences": {
            "temperature": (38, 40),
            "cleanliness": 85,        # Increased from 80
            "staff_skill": 75,
            "price_sensitivity": 0.6,
            "facility_importance": 0.8,
        },
        "feedback": [
            "The communal areas were perfect for meeting fellow travelers!",
            "The atmosphere was too quiet and restrictive.",
            "Loved the group activities and social spaces.",
            "The staff created a wonderful community feeling.",
            "I wish there were more opportunities to socialize."
        ]
    }
}

class Customer:
    """Represents a customer with specific preferences and behaviors."""
    
    def __init__(self, personality_type=None):
        if personality_type is None:
            personality_type = random.choice(list(PERSONALITIES.keys()))
        
        self.personality = personality_type
        self.preferences = PERSONALITIES[personality_type]["preferences"]
        self.satisfaction = 50  # Base satisfaction level (0-100)
        
    def evaluate_resort(self, resort):
        """Evaluate the resort based on customer preferences."""
        # Start with base satisfaction
        self.satisfaction = 50
        
        # Check if resort has basic requirements
        if not resort.pools:
            self.satisfaction = 10  # Very unsatisfied if there are no pools
            return self.satisfaction
            
        # Evaluate pools
        if resort.pools:
            pool_satisfaction = 0
            for pool in resort.pools:
                # Temperature satisfaction
                min_temp, max_temp = self.preferences["temperature"]
                if min_temp <= pool.temperature <= max_temp:
                    pool_satisfaction += 20
                else:
                    # Penalty increases the further from preferred range
                    temp_diff = min(abs(pool.temperature - min_temp), abs(pool.temperature - max_temp))
                    pool_satisfaction -= temp_diff * 5
                
                # Cleanliness satisfaction - more severe penalties for dirty pools
                if pool.cleanliness >= self.preferences["cleanliness"]:
                    pool_satisfaction += 15
                else:
                    cleanliness_diff = self.preferences["cleanliness"] - pool.cleanliness
                    # Exponential penalty for uncleanliness
                    pool_satisfaction -= cleanliness_diff * (cleanliness_diff / 10)
                
                # Special ingredients bonus
                if pool.ingredients:
                    pool_satisfaction += 10 * len(pool.ingredients)
            
            # Average pool satisfaction
            pool_satisfaction = pool_satisfaction / len(resort.pools)
            self.satisfaction += pool_satisfaction * 0.4  # Pools are 40% of satisfaction
        else:
            # No pools is a major problem
            self.satisfaction -= 30
        
        # Staff skill evaluation - more important for luxury customers
        staff_importance = 1.0
        if self.personality == "Luxury Enthusiast":
            staff_importance = 1.5
        
        avg_staff_skill = resort.staff_manager.get_average_skill()
        if avg_staff_skill >= self.preferences["staff_skill"]:
            self.satisfaction += 15 * staff_importance
        else:
            skill_diff = self.preferences["staff_skill"] - avg_staff_skill
            self.satisfaction -= skill_diff * 0.3 * staff_importance
        
        # Price evaluation
        price_factor = 1.0
        # Define reasonable price ranges based on personality
        reasonable_price = {
            "Budget Traveler": 1500,
            "Relaxation Seeker": 2500,
            "Health Conscious": 3000,
            "Traditional Purist": 3500,
            "Social Butterfly": 3000,
            "Luxury Enthusiast": 5000
        }.get(self.personality, 2500)
        
        # Calculate how much the current price deviates from reasonable price
        price_ratio = resort.entry_fee / reasonable_price
        
        if price_ratio > 1:
            # Price is higher than reasonable - apply penalty based on sensitivity
            price_factor = 1.0 - (price_ratio - 1) * self.preferences["price_sensitivity"]
            # More severe penalty for extreme prices
            if price_ratio > 2:
                price_factor *= 0.5
        elif resort.entry_fee < reasonable_price * 0.5:
            # Price is suspiciously low - might indicate poor quality
            price_factor = 0.9
        
        # Apply price factor to satisfaction
        self.satisfaction *= max(0.1, price_factor)  # Ensure it doesn't go to zero
        
        # Facilities evaluation - different types of customers care about different facilities
        if resort.facilities:
            facility_bonus = 0
            
            for facility in resort.facilities:
                # Check if facility is operational
                if not facility.is_operational:
                    # Non-operational facilities cause dissatisfaction
                    facility_bonus -= 10
                    continue
                
                # Base bonus for having operational facilities
                facility_bonus += 3
                
                # Additional bonuses based on customer type and facility type
                if self.personality == "Luxury Enthusiast" and hasattr(facility, 'quality_level') and getattr(facility, 'quality_level', 0) >= 3:
                    facility_bonus += 5
                elif self.personality == "Budget Traveler" and hasattr(facility, 'price_tier') and getattr(facility, 'price_tier', 0) == 1:
                    facility_bonus += 3
                elif self.personality == "Health Conscious" and hasattr(facility, 'type_name') and getattr(facility, 'type_name', '') in ["Spa Treatment", "Massage"]:
                    facility_bonus += 7
                elif self.personality == "Traditional Purist" and hasattr(facility, 'style') and getattr(facility, 'style', '') == "Japanese":
                    facility_bonus += 5
                elif self.personality == "Social Butterfly" and hasattr(facility, 'type_name') and getattr(facility, 'type_name', '') in ["Karaoke", "Game Room"]:
                    facility_bonus += 6
            
            # Apply facility importance multiplier
            facility_bonus *= self.preferences["facility_importance"]
            self.satisfaction += min(25, facility_bonus)  # Cap at +25
        
        # Weather impact
        weather_impact = resort.weather.get_guest_impact() - 1.0
        self.satisfaction += weather_impact * 10
        
        # Boredom factor - long-term guests get bored if no new upgrades
        if resort.boredom_factor > 0:
            self.satisfaction -= resort.boredom_factor * 0.5
        
        # Cap satisfaction between 0 and 100
        self.satisfaction = max(0, min(100, self.satisfaction))
        
        return self.satisfaction
    
    def get_feedback(self):
        """Get feedback based on satisfaction level."""
        feedback_pool = PERSONALITIES[self.personality]["feedback"]
        
        if self.satisfaction >= 80:
            # Positive feedback
            return random.choice(feedback_pool[0:2])
        elif self.satisfaction >= 50:
            # Neutral feedback
            return random.choice(feedback_pool[2:3])
        else:
            # Negative feedback
            return random.choice(feedback_pool[3:5])
    
    def will_visit(self, resort):
        """Determine if the customer will visit based on their evaluation."""
        # First check if entry fee is unreasonably high
        # Different customer types have different thresholds
        max_acceptable_fee = {
            "Budget Traveler": 3000,
            "Relaxation Seeker": 5000,
            "Health Conscious": 6000,
            "Traditional Purist": 7000,
            "Social Butterfly": 6000,
            "Luxury Enthusiast": 10000
        }.get(self.personality, 5000)
        
        # Apply price sensitivity to the threshold
        price_sensitivity = self.preferences["price_sensitivity"]
        max_acceptable_fee = max_acceptable_fee * (2 - price_sensitivity)
        
        # If entry fee is above the threshold, drastically reduce visit chance
        if resort.entry_fee > max_acceptable_fee:
            # The higher above threshold, the less likely to visit
            fee_ratio = resort.entry_fee / max_acceptable_fee
            if fee_ratio > 2:  # If more than double the acceptable fee
                return False  # Will not visit at all
            else:
                # Exponentially decreasing chance as fee increases
                visit_chance = 1 / (fee_ratio * fee_ratio * 2)
                return random.random() < visit_chance
        
        # Normal evaluation for reasonable fees
        satisfaction_prediction = self.evaluate_resort(resort)
        
        # Base chance increases with satisfaction
        visit_chance = satisfaction_prediction / 100
        
        # Add some randomness
        visit_chance += random.uniform(-0.1, 0.1)
        
        # Cap between 0 and 1
        visit_chance = max(0, min(1, visit_chance))
        
        return random.random() < visit_chance
