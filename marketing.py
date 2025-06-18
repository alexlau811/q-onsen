"""
Marketing module for the Onsen Resort Management Game.
This module handles marketing campaigns and promotions.
"""

import random

class MarketingCampaign:
    """Class for marketing campaigns to promote the resort."""
    
    def __init__(self, name, cost, duration, effect_description, effect_function):
        self.name = name
        self.cost = cost
        self.duration = duration  # in days
        self.days_remaining = duration
        self.effect_description = effect_description
        self.effect_function = effect_function
        self.active = False
    
    def start(self, resort):
        """Start the marketing campaign."""
        if resort.money >= self.cost:
            resort.money -= self.cost
            self.active = True
            self.days_remaining = self.duration
            return True
        return False
    
    def apply_daily_effect(self, resort):
        """Apply the daily effect of the campaign."""
        if self.active:
            self.effect_function(resort)
            self.days_remaining -= 1
            
            if self.days_remaining <= 0:
                self.active = False
    
    def __str__(self):
        """String representation of the campaign."""
        status = "Active" if self.active else "Inactive"
        if self.active:
            return (f"{self.name} ({status}, {self.days_remaining} days left)\n"
                    f"Effect: {self.effect_description}")
        else:
            return (f"{self.name} ({status})\n"
                    f"Cost: ¥{self.cost:,}\n"
                    f"Duration: {self.duration} days\n"
                    f"Effect: {self.effect_description}")


class Promotion:
    """Class for special promotions and discounts."""
    
    def __init__(self, name, discount_percent, duration, target):
        self.name = name
        self.discount_percent = discount_percent
        self.duration = duration  # in days
        self.days_remaining = duration
        self.target = target  # "entry", "restaurant", "accommodation", "all"
        self.active = False
    
    def start(self):
        """Start the promotion."""
        self.active = True
        self.days_remaining = self.duration
    
    def update(self):
        """Update the promotion status."""
        if self.active:
            self.days_remaining -= 1
            if self.days_remaining <= 0:
                self.active = False
    
    def get_discount_multiplier(self):
        """Get the discount multiplier (e.g., 0.8 for 20% off)."""
        if self.active:
            return 1 - (self.discount_percent / 100)
        return 1.0
    
    def __str__(self):
        """String representation of the promotion."""
        status = "Active" if self.active else "Inactive"
        if self.active:
            return (f"{self.name} ({status}, {self.days_remaining} days left)\n"
                    f"Discount: {self.discount_percent}% off {self.target}")
        else:
            return (f"{self.name} ({status})\n"
                    f"Discount: {self.discount_percent}% off {self.target}\n"
                    f"Duration: {self.duration} days")


class MarketingManager:
    """Class to manage marketing campaigns and promotions."""
    
    def __init__(self):
        self.campaigns = self._create_campaigns()
        self.active_campaigns = []
        self.promotions = self._create_promotions()
        self.active_promotions = []
    
    def _create_campaigns(self):
        """Create a list of available marketing campaigns."""
        campaigns = []
        
        # Local newspaper ad
        campaigns.append(MarketingCampaign(
            "Local Newspaper Ad",
            5000,
            7,
            "Small increase in local visitors",
            lambda resort: setattr(resort, 'reputation', min(100, resort.reputation + 0.5))
        ))
        
        # Travel magazine feature
        campaigns.append(MarketingCampaign(
            "Travel Magazine Feature",
            20000,
            14,
            "Moderate increase in reputation and visitors",
            lambda resort: setattr(resort, 'reputation', min(100, resort.reputation + 1))
        ))
        
        # TV commercial
        campaigns.append(MarketingCampaign(
            "TV Commercial",
            50000,
            30,
            "Significant increase in reputation and visitors",
            lambda resort: setattr(resort, 'reputation', min(100, resort.reputation + 1.5))
        ))
        
        # Social media campaign
        campaigns.append(MarketingCampaign(
            "Social Media Campaign",
            15000,
            21,
            "Attracts younger visitors and increases online presence",
            lambda resort: self._social_media_effect(resort)
        ))
        
        # Tourism partnership
        campaigns.append(MarketingCampaign(
            "Tourism Partnership",
            30000,
            60,
            "Long-term steady increase in foreign visitors",
            lambda resort: setattr(resort, 'reputation', min(100, resort.reputation + 0.3))
        ))
        
        return campaigns
    
    def _create_promotions(self):
        """Create a list of available promotions."""
        promotions = []
        
        # Weekday discount
        promotions.append(Promotion(
            "Weekday Special",
            20,
            14,
            "entry"
        ))
        
        # Couples package
        promotions.append(Promotion(
            "Couples Package",
            15,
            7,
            "all"
        ))
        
        # Senior discount
        promotions.append(Promotion(
            "Senior Discount",
            25,
            30,
            "entry"
        ))
        
        # Family package
        promotions.append(Promotion(
            "Family Package",
            10,
            14,
            "all"
        ))
        
        # Restaurant discount
        promotions.append(Promotion(
            "Dining Special",
            15,
            10,
            "restaurant"
        ))
        
        return promotions
    
    def _social_media_effect(self, resort):
        """Special effect for social media campaign."""
        # Increases reputation
        resort.reputation = min(100, resort.reputation + 0.7)
        
        # Has a small chance of going viral
        if random.random() < 0.05:  # 5% chance each day
            resort.reputation = min(100, resort.reputation + random.randint(5, 10))
    
    def start_campaign(self, campaign_index, resort):
        """Start a marketing campaign."""
        if 0 <= campaign_index < len(self.campaigns):
            campaign = self.campaigns[campaign_index]
            if campaign.start(resort):
                self.active_campaigns.append(campaign)
                return True
        return False
    
    def start_promotion(self, promotion_index):
        """Start a promotion."""
        if 0 <= promotion_index < len(self.promotions):
            promotion = self.promotions[promotion_index]
            promotion.start()
            self.active_promotions.append(promotion)
            return True
        return False
    
    def update_daily(self, resort):
        """Update all active campaigns and promotions."""
        # Update campaigns
        for campaign in self.active_campaigns[:]:
            campaign.apply_daily_effect(resort)
            if not campaign.active:
                self.active_campaigns.remove(campaign)
        
        # Update promotions
        for promotion in self.active_promotions[:]:
            promotion.update()
            if not promotion.active:
                self.active_promotions.remove(promotion)
    
    def get_entry_fee_multiplier(self):
        """Get the combined discount multiplier for entry fees."""
        multiplier = 1.0
        for promotion in self.active_promotions:
            if promotion.active and (promotion.target == "entry" or promotion.target == "all"):
                multiplier *= promotion.get_discount_multiplier()
        return multiplier
