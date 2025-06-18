#!/usr/bin/env python3
"""
Onsen Resort Management Game
A text-based business simulation game where you manage your own hot spring resort.
"""

import random
import time
import os
import sys
from onsen_pool import OnsenPool, Ingredient, INGREDIENTS
from facilities import Restaurant, GiftShop, Accommodation, Entertainment
from staff import Staff, StaffManager
from events import Weather, EventManager
from marketing import MarketingCampaign, Promotion, MarketingManager

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii_art():
    """Display the game's ASCII art title."""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║  ██████  ███    ██ ███████ ███████ ███    ██  ║
    ║ ██    ██ ████   ██ ██      ██      ████   ██  ║
    ║ ██    ██ ██ ██  ██ ███████ █████   ██ ██  ██  ║
    ║ ██    ██ ██  ██ ██      ██ ██      ██  ██ ██  ║
    ║  ██████  ██   ████ ███████ ███████ ██   ████  ║
    ║                                               ║
    ║        ♨️  RESORT MANAGEMENT GAME  ♨️         ║
    ╚═══════════════════════════════════════════════╝
    """)

def print_pool_ascii():
    """Display ASCII art for an onsen pool."""
    print("""
        .-~~~-.
      .'       `.
     :           :
     :           :    ♨️
      `.       .'
        `-...-'
    """)

def print_facility_ascii():
    """Display ASCII art for a facility."""
    print("""
       _______
      /       \\
     /         \\
    |  ╭┬┬┬╮   |
    |  ┝┷┷┷┥   |
    |  ╰┴┴┴╯   |
    |___________|
    """)

class OnsenResort:
    """Main class for the Onsen Resort business."""
    
    def __init__(self):
        self.name = "Unnamed Resort"
        self.money = 100000  # Starting capital
        self.day = 1
        self.season = "Spring"
        self.reputation = 50  # 0-100 scale
        self.pools = []
        self.facilities = []
        self.staff_manager = StaffManager()
        self.weather = Weather()
        self.event_manager = EventManager()
        self.marketing_manager = MarketingManager()
        self.guests = 0
        self.daily_income = 0
        self.daily_expenses = 0
        self.entry_fee = 2000  # Default entry fee in yen
        self.event_log = []
        
    def new_day(self):
        """Process a new day in the resort."""
        self.day += 1
        if self.day % 90 == 0:  # Change seasons every 90 days
            seasons = ["Spring", "Summer", "Autumn", "Winter"]
            current_index = seasons.index(self.season)
            self.season = seasons[(current_index + 1) % 4]
            
        # Update weather
        self.weather.update(self.season)
        
        # Reset daily stats
        self.daily_income = 0
        self.daily_expenses = 0
        self.guests = 0
        
        # Update staff
        self.staff_manager.work_day()
        
        # Update marketing
        self.marketing_manager.update_daily(self)
        
        # Calculate guests based on various factors
        self._calculate_guests()
        
        # Calculate income and expenses
        self._calculate_finances()
        
        # Process random events
        self._process_random_events()
        
        # Update accommodations
        for facility in self.facilities:
            if isinstance(facility, Accommodation):
                facility.update_occupancy(self.reputation, self.season)
        
        # Clean pools (automatic daily maintenance)
        for pool in self.pools:
            if pool.cleanliness < 70:  # Only clean if needed
                pool.cleanliness = min(100, pool.cleanliness + 20)
        
    def _calculate_guests(self):
        """Calculate the number of guests for the day."""
        base_guests = int(self.reputation / 2)
        
        # Season effects
        season_multiplier = {
            "Spring": 1.2,
            "Summer": 0.8,  # People prefer cooler places in summer
            "Autumn": 1.5,  # Peak season for onsen
            "Winter": 1.8   # Best season for onsen
        }
        
        # Weather effects
        weather_effect = self.weather.get_guest_impact()
        
        # Price sensitivity
        price_factor = 1.0
        if self.entry_fee > 3000:
            price_factor = 0.8
        elif self.entry_fee < 1500:
            price_factor = 1.3
        
        # Marketing effects
        marketing_multiplier = 1.0
        if self.marketing_manager.active_campaigns:
            marketing_multiplier = 1.1
        
        # Entry fee discount
        entry_fee_multiplier = self.marketing_manager.get_entry_fee_multiplier()
        
        # Calculate final guest count
        self.guests = int(base_guests * season_multiplier[self.season] * 
                          weather_effect * price_factor * marketing_multiplier)
        
        # Add some randomness
        self.guests = max(0, self.guests + random.randint(-10, 10))
        
    def _calculate_finances(self):
        """Calculate daily income and expenses."""
        # Income from entry fees (with promotions applied)
        entry_fee_multiplier = self.marketing_manager.get_entry_fee_multiplier()
        effective_entry_fee = self.entry_fee * entry_fee_multiplier
        self.daily_income = self.guests * effective_entry_fee
        
        # Basic daily expenses
        self.daily_expenses = 5000  # Base operating cost
        
        # Add expenses for pools
        for pool in self.pools:
            self.daily_expenses += pool.get_daily_cost()
        
        # Add expenses for facilities
        for facility in self.facilities:
            self.daily_expenses += facility.get_daily_cost()
            self.daily_income += facility.get_daily_income(self.guests)
        
        # Add staff salaries
        self.daily_expenses += self.staff_manager.get_total_salary()
        
        # Update money
        self.money += (self.daily_income - self.daily_expenses)
        
    def _process_random_events(self):
        """Process random events that might occur."""
        event_result = self.event_manager.trigger_random_event(self)
        if event_result:
            name, description, effect = event_result
            self.event_log.append(f"Day {self.day}: {name} - {effect}")
        
    def display_status(self):
        """Display the current status of the resort."""
        clear_screen()
        print_ascii_art()
        print(f"\n{self.name} - Day {self.day} ({self.season})")
        print(f"Weather: {self.weather}")
        print(f"Money: ¥{self.money:,}")
        print(f"Reputation: {self.reputation}/100")
        print(f"Guests today: {self.guests}")
        print(f"Daily income: ¥{self.daily_income:,}")
        print(f"Daily expenses: ¥{self.daily_expenses:,}")
        print(f"Profit/Loss: ¥{self.daily_income - self.daily_expenses:,}")
        
        # Show active promotions
        if self.marketing_manager.active_promotions:
            print("\nActive Promotions:")
            for promo in self.marketing_manager.active_promotions:
                print(f"- {promo.name} ({promo.discount_percent}% off, {promo.days_remaining} days left)")
        
        # Show active campaigns
        if self.marketing_manager.active_campaigns:
            print("\nActive Marketing Campaigns:")
            for campaign in self.marketing_manager.active_campaigns:
                print(f"- {campaign.name} ({campaign.days_remaining} days left)")
        
        print("\n" + "="*50)

def main_menu():
    """Display the main menu and handle user input."""
    resort = OnsenResort()
    resort.name = input("Welcome! Please name your onsen resort: ")
    
    while True:
        resort.display_status()
        print("\nMAIN MENU:")
        print("1. Manage Onsen Pools")
        print("2. Manage Facilities")
        print("3. Manage Staff")
        print("4. Set Entry Fee")
        print("5. Marketing & Promotion")
        print("6. Advance to Next Day")
        print("7. Save Game")
        print("8. Quit Game")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == "1":
            # Manage pools menu (to be implemented)
            pass
        elif choice == "2":
            # Manage facilities menu (to be implemented)
            pass
        elif choice == "3":
            # Manage staff menu (to be implemented)
            pass
        elif choice == "4":
            try:
                new_fee = int(input("Enter new entry fee (in yen): "))
                if new_fee < 0:
                    print("Entry fee cannot be negative.")
                else:
                    resort.entry_fee = new_fee
                    print(f"Entry fee set to ¥{resort.entry_fee}")
            except ValueError:
                print("Please enter a valid number.")
            input("Press Enter to continue...")
        elif choice == "5":
            # Marketing menu (to be implemented)
            pass
        elif choice == "6":
            resort.new_day()
        elif choice == "7":
            # Save game (to be implemented)
            print("Game saved! (Not really implemented yet)")
            input("Press Enter to continue...")
        elif choice == "8":
            if input("Are you sure you want to quit? (y/n): ").lower() == 'y':
                print("Thank you for playing!")
                break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    clear_screen()
    print_ascii_art()
    print("\nWelcome to the Onsen Resort Management Game!")
    print("In this game, you'll manage your own hot spring resort in Japan.")
    print("Build onsen pools, add facilities, hire staff, and attract guests!")
    input("\nPress Enter to start...")
    main_menu()
