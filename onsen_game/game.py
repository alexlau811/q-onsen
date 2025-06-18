#!/usr/bin/env python3
"""
Onsen Resort Management Game
A text-based business simulation game where you manage your own hot spring resort.
"""

import random
import time
import os
import sys
from .pools import OnsenPool, Ingredient, INGREDIENTS
from .facilities import Restaurant, GiftShop, Accommodation, Entertainment
from .staff import Staff, StaffManager
from .events import Weather, EventManager
from .marketing import MarketingCampaign, Promotion, MarketingManager
from .customers import Customer, PERSONALITIES
from .ascii_art import generate_onsen_ascii, generate_facilities_summary, generate_rooms_summary

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii_art():
    """Display the game's ASCII art title."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ██████  ███    ██ ███████ ███████ ███    ██               ║
    ║  ██    ██ ████   ██ ██      ██      ████   ██               ║
    ║  ██    ██ ██ ██  ██ ███████ █████   ██ ██  ██               ║
    ║  ██    ██ ██  ██ ██      ██ ██      ██  ██ ██               ║
    ║   ██████  ██   ████ ███████ ███████ ██   ████               ║
    ║                                                              ║
    ║        ♨️  RESORT MANAGEMENT GAME  ♨️                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def print_pool_ascii():
    """Display ASCII art for an onsen pool."""
    print("""
         .---.              .---.
        /     \\            /     \\
       /       \\          /       \\
      /         \\________/         \\
     |                              |
     |     ♨️       ♨️       ♨️     |
     |                              |
     |  ~~~~~    ~~~~~    ~~~~~     |
     |                              |
      \\                            /
       \\__________________________/
    """)

def print_facility_ascii():
    """Display ASCII art for a facility."""
    print("""
            _____________________
           /                     \\
          /                       \\
         /                         \\
        |     ┌─────────────┐      |
        |     │  ┌───────┐  │      |
        |     │  │       │  │      |
        |     │  │       │  │      |
        |     │  └───────┘  │      |
        |     └─────────────┘      |
        |                          |
        |  ┌────┐        ┌────┐   |
        |  │    │        │    │   |
        |  └────┘        └────┘   |
        |__________________________|
    """)

class OnsenResort:
    """Main class for the Onsen Resort business."""
    
    def __init__(self):
        self.name = "Unnamed Resort"
        self.money = 75000  # Starting capital (reduced from 100000)
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
        self.customer_feedback = []  # Store daily customer feedback
        self.daily_visitors = []  # Store daily visitor data
        self.last_upgrade_day = 1  # Track when the last upgrade was made
        self.boredom_factor = 0  # Increases over time without upgrades
        
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
        self.customer_feedback = []
        self.daily_visitors = []
        
        # Update staff
        self.staff_manager.work_day()
        
        # Update marketing
        self.marketing_manager.update_daily(self)
        
        # Update boredom factor - increases if no upgrades for a while
        days_since_upgrade = self.day - self.last_upgrade_day
        if days_since_upgrade > 30:  # After 30 days without upgrades
            self.boredom_factor = min(30, (days_since_upgrade - 30) // 10)  # Max 30% reduction
            if self.boredom_factor > 0 and self.boredom_factor % 5 == 0:
                self.event_log.append(f"Day {self.day}: Guests are getting bored with the same old facilities!")
        
        # Calculate guests based on various factors
        self._calculate_guests()
        
        # Calculate income and expenses
        self._calculate_finances()
        
        # Update resort reputation based on guest satisfaction
        self._update_reputation()
        
        # Generate random events
        event = self.event_manager.trigger_random_event(self)
        if event:
            event_name, event_desc, effect_desc = event
            self.event_log.append(f"Day {self.day}: {event_name} - {event_desc} {effect_desc}")
        
        # Update pools
        for pool in self.pools:
            # Decrease cleanliness
            pool.cleanliness = max(0, pool.cleanliness - random.randint(10, 20))
            
            # Check if there are cleaners to maintain the pools
            cleaners = self.staff_manager.get_staff_by_role("Cleaner")
            if cleaners:
                avg_skill = sum(staff.skill_level for staff in cleaners) / len(cleaners)
                for pool in self.pools:
                    # Higher skill means better cleaning
                    pool.cleanliness = min(100, pool.cleanliness + int(5 * avg_skill))
        
        # Show end of day summary with customer feedback
        self._show_day_end_summary()
        
        # Update accommodations
        for facility in self.facilities:
            if isinstance(facility, Accommodation):
                facility.update_occupancy(self.reputation, self.season)
        
        # Clean pools (automatic daily maintenance)
        for pool in self.pools:
            if pool.cleanliness < 70:  # Only clean if needed
                pool.cleanliness = min(100, pool.cleanliness + 20)
        
    def _calculate_guests(self):
        """Calculate the number of guests for the day using customer personalities."""
        # Base potential visitors based on reputation and season
        season_multiplier = {
            "Winter": 1.5,  # Peak season for onsen
            "Autumn": 1.2,
            "Spring": 1.0,
            "Summer": 0.7   # Low season
        }.get(self.season, 1.0)
        
        # Check if resort has basic requirements to operate
        if not self.pools:
            self.daily_visitors = []
            self.guests = 0
            self.customer_feedback = []
            return
        
        # Calculate base potential visitors
        potential_visitors = int(self.reputation * 2 * season_multiplier)
        
        # Apply marketing effects
        marketing_boost = 1.0
        for campaign in self.marketing_manager.active_campaigns:
            if campaign.active:
                marketing_boost += 0.2  # Each active campaign adds 20% more potential visitors
        
        potential_visitors = int(potential_visitors * marketing_boost)
        
        # Apply boredom factor - reduces visitors over time without upgrades
        if self.boredom_factor > 0:
            potential_visitors = int(potential_visitors * (1 - self.boredom_factor / 100))
        
        # Check if facilities are operational
        non_operational_facilities = sum(1 for facility in self.facilities if not facility.is_operational)
        if non_operational_facilities > 0 and self.facilities:
            # Reduce visitors based on percentage of non-operational facilities
            facility_penalty = non_operational_facilities / len(self.facilities)
            potential_visitors = int(potential_visitors * (1 - facility_penalty * 0.5))
        
        # Generate a mix of customer personalities
        customer_types = list(PERSONALITIES.keys())
        
        # Adjust mix based on season and marketing
        if self.season == "Winter":
            # More luxury enthusiasts and health conscious in winter
            customer_types.extend(["Luxury Enthusiast", "Health Conscious"])
        elif self.season == "Summer":
            # More budget travelers and social butterflies in summer
            customer_types.extend(["Budget Traveler", "Social Butterfly"])
        
        # Create potential visitors with different personalities
        potential_customers = []
        for _ in range(potential_visitors):
            personality = random.choice(customer_types)
            potential_customers.append(Customer(personality))
        
        # Determine which customers will actually visit
        actual_visitors = []
        for customer in potential_customers:
            if customer.will_visit(self):
                actual_visitors.append(customer)
        
        # If reputation is very low, there might be no visitors at all
        if self.reputation < 30 and random.random() < 0.8:
            actual_visitors = []
        
        # Store the visitors for the day
        self.daily_visitors = actual_visitors
        self.guests = len(actual_visitors)
        
        # Generate feedback from a sample of visitors
        self.customer_feedback = []
        if self.guests > 0:
            # Take a sample of visitors for feedback (max 5)
            feedback_sample = random.sample(actual_visitors, min(5, len(actual_visitors)))
            for customer in feedback_sample:
                self.customer_feedback.append({
                    "personality": customer.personality,
                    "satisfaction": customer.satisfaction,
                    "feedback": customer.get_feedback()
                })
        
    def _calculate_finances(self):
        """Calculate daily income and expenses."""
        # Income from entry fees (with promotions applied)
        entry_fee_multiplier = self.marketing_manager.get_entry_fee_multiplier()
        effective_entry_fee = self.entry_fee * entry_fee_multiplier
        self.daily_income = self.guests * effective_entry_fee
        
        # Basic daily expenses
        self.daily_expenses = 8000  # Base operating cost (increased from 5000)
        
        # Add land rent - fixed expense regardless of resort size
        land_rent = 15000  # Daily land rent (increased from 10000)
        self.daily_expenses += land_rent
        
        # Add expenses for pools
        for pool in self.pools:
            self.daily_expenses += pool.get_daily_cost()
        
        # Add expenses for facilities
        for facility in self.facilities:
            self.daily_expenses += facility.get_daily_cost()
            
            # Check if facility has enough staff to operate properly
            required_staff = facility.staff_required
            staff_count = self._count_staff_for_facility(facility)
            
            # Calculate operational efficiency based on staffing
            if staff_count == 0:
                # No staff, facility barely functions
                operational_efficiency = 0.2
                facility.is_operational = False
            elif staff_count < required_staff:
                # Understaffed, reduced efficiency
                operational_efficiency = 0.5 + (0.5 * staff_count / required_staff)
                facility.is_operational = True
            else:
                # Fully staffed
                operational_efficiency = 1.0
                facility.is_operational = True
            
            # Apply operational efficiency to income
            facility_income = facility.get_daily_income(self.guests) * operational_efficiency
            self.daily_income += facility_income
        
        # Add staff salaries
        staff_salaries = self.staff_manager.get_total_salary()
        self.daily_expenses += staff_salaries
        
        # Check if we can pay staff
        if self.money < staff_salaries:
            # Can't pay staff, they will be unhappy and might leave
            self._handle_unpaid_staff()
        
        # Update money
        self.money += (self.daily_income - self.daily_expenses)
        
    def _handle_unpaid_staff(self):
        """Handle the situation when staff can't be paid."""
        # Drastically reduce staff happiness
        for staff in self.staff_manager.staff[:]:  # Create a copy to iterate safely
            staff.happiness -= 30
            
            # Staff might leave if too unhappy
            if staff.happiness <= 0 or random.random() < 0.5:  # 50% chance of leaving when unpaid
                self.staff_manager.staff.remove(staff)
                self.event_log.append(f"Day {self.day}: {staff.name} left due to unpaid wages!")
        
    def _count_staff_for_facility(self, facility):
        """Count how many staff are available for a specific facility type."""
        facility_type_to_roles = {
            Restaurant: ["Chef", "Server"],
            GiftShop: ["Attendant"],
            Accommodation: ["Receptionist", "Attendant", "Cleaner"],
            Entertainment: ["Attendant"]
        }
        
        # Get the appropriate roles for this facility type
        applicable_roles = []
        for facility_class, roles in facility_type_to_roles.items():
            if isinstance(facility, facility_class):
                applicable_roles = roles
                break
        
        # Count staff with applicable roles
        count = 0
        for role in applicable_roles:
            count += len(self.staff_manager.get_staff_by_role(role))
            
        return count
        
    def _update_reputation(self):
        """Update resort reputation based on guest satisfaction."""
        if not self.daily_visitors:
            # No visitors means no change in reputation
            return
            
        # Calculate average satisfaction from all visitors
        total_satisfaction = sum(customer.satisfaction for customer in self.daily_visitors)
        avg_satisfaction = total_satisfaction / len(self.daily_visitors)
        
        # Convert satisfaction to reputation change
        # If satisfaction is above 50, reputation increases
        # If satisfaction is below 50, reputation decreases
        reputation_change = (avg_satisfaction - 50) / 8  # Changed from /10 to make reputation changes more dramatic
        
        # Apply the change
        self.reputation = max(0, min(100, self.reputation + reputation_change))
        
        # Add a small daily reputation decay to make it harder to maintain high reputation
        if self.reputation > 50:
            self.reputation -= 0.5
        
    def _show_day_end_summary(self):
        """Show the end of day summary with customer feedback."""
        clear_screen()
        print_ascii_art()
        print(f"\n{self.name} - End of Day {self.day} ({self.season})")
        print(f"Weather: {self.weather}")
        
        # Show customer feedback one by one
        if self.customer_feedback:
            print("\n\033[1;36m=== CUSTOMER FEEDBACK ===\033[0m")
            for i, feedback in enumerate(self.customer_feedback, 1):
                satisfaction_level = feedback['satisfaction']
                satisfaction_text = "Excellent" if satisfaction_level >= 80 else \
                                   "Good" if satisfaction_level >= 60 else \
                                   "Average" if satisfaction_level >= 40 else \
                                   "Poor" if satisfaction_level >= 20 else "Terrible"
                
                satisfaction_color = "\033[1;32m" if satisfaction_level >= 60 else \
                                    "\033[1;33m" if satisfaction_level >= 40 else \
                                    "\033[1;31m"
                
                print(f"\nFeedback #{i} - \033[1;35m{feedback['personality']}\033[0m:")
                print(f"Satisfaction: {satisfaction_color}{feedback['satisfaction']:.1f}/100 ({satisfaction_text})\033[0m")
                print(f"\"\033[3m{feedback['feedback']}\033[0m\"")
                
                # Pause between feedback
                if i < len(self.customer_feedback):
                    input("\nPress Enter to see next feedback...")
        else:
            print("\nNo visitors today. This is concerning!")
            if not self.pools:
                print("You need to build at least one onsen pool to attract guests.")
            elif self.entry_fee > 5000:
                print("Your entry fee may be too high. Consider lowering it.")
            elif self.reputation < 20:
                print("Your reputation is very low. Focus on improving your facilities and service.")
        
        # Show financial summary
        print("\n\033[1;36m=== FINANCIAL SUMMARY ===\033[0m")
        print(f"Guests: \033[1;36m{self.guests}\033[0m")
        print(f"Entry Fee: \033[1;32m¥{self.entry_fee:,}\033[0m")
        print(f"Income: \033[1;32m¥{self.daily_income:,}\033[0m")
        print(f"Expenses: \033[1;31m¥{self.daily_expenses:,}\033[0m")
        profit = self.daily_income - self.daily_expenses
        profit_color = "\033[1;32m" if profit >= 0 else "\033[1;31m"
        print(f"Profit: {profit_color}¥{profit:,}\033[0m" + (" \033[1;31m(LOSS)\033[0m" if profit < 0 else ""))
        print(f"Current funds: \033[1;33m¥{self.money:,}\033[0m")
        
        # Show reputation
        print(f"\nResort Reputation: \033[1;35m{self.reputation:.2f}/100\033[0m")
        reputation_text = "Excellent" if self.reputation >= 80 else \
                         "Good" if self.reputation >= 60 else \
                         "Average" if self.reputation >= 40 else \
                         "Poor" if self.reputation >= 20 else "Terrible"
        reputation_color = "\033[1;32m" if self.reputation >= 60 else \
                          "\033[1;33m" if self.reputation >= 40 else \
                          "\033[1;31m"
        print(f"Reputation Status: {reputation_color}{reputation_text}\033[0m")
        
        # Show staffing status
        print("\n\033[1;36m=== STAFFING STATUS ===\033[0m")
        if not self.staff_manager.staff:
            print("\033[1;31mNo staff employed! Facilities cannot operate properly.\033[0m")
        else:
            print(f"Total Staff: \033[1;36m{len(self.staff_manager.staff)}\033[0m")
            
            avg_skill = self.staff_manager.get_average_skill()
            skill_color = "\033[1;32m" if avg_skill >= 3.5 else \
                         "\033[1;33m" if avg_skill >= 2.5 else \
                         "\033[1;31m"
            print(f"Average Skill: {skill_color}{avg_skill:.1f}/5\033[0m")
            
            avg_happiness = self.staff_manager.get_average_happiness()
            happiness_color = "\033[1;32m" if avg_happiness >= 70 else \
                             "\033[1;33m" if avg_happiness >= 40 else \
                             "\033[1;31m"
            print(f"Average Happiness: {happiness_color}{avg_happiness:.1f}/100\033[0m")
            
            # Show understaffed facilities
            understaffed = []
            for facility in self.facilities:
                required = facility.staff_required
                actual = self._count_staff_for_facility(facility)
                if actual < required:
                    understaffed.append((facility.name, actual, required))
            
            if understaffed:
                print("\n\033[1;31mUnderstaffed Facilities:\033[0m")
                for name, actual, required in understaffed:
                    print(f"- {name}: \033[1;31m{actual}/{required}\033[0m staff")
        
        # Show daily events
        print("\n\033[1;36m=== TODAY'S EVENTS ===\033[0m")
        events_today = [event for event in self.event_log if f"Day {self.day}:" in event]
        if events_today:
            for event in events_today:
                print(f"• \033[1;33m{event.replace(f'Day {self.day}: ', '')}\033[0m")
        else:
            print("No special events occurred today.")
            
        # Show boredom factor if relevant
        if self.boredom_factor > 0:
            boredom_color = "\033[1;33m" if self.boredom_factor < 15 else "\033[1;31m"
            print(f"\nGuest Boredom Factor: {boredom_color}{self.boredom_factor}%\033[0m")
            print(f"Days since last upgrade: \033[1;33m{self.day - self.last_upgrade_day}\033[0m")
            print("\033[1;33mGuests are getting bored with the same facilities. Consider upgrades!\033[0m")
        
        # Show business advice based on current state
        print("\n\033[1;36m=== BUSINESS ADVICE ===\033[0m")
        if self.reputation < 30:
            print("\033[1;31mYour reputation needs serious improvement!\033[0m")
        
        if not self.pools:
            print("\033[1;31mBuild at least one onsen pool to attract guests.\033[0m")
        elif all(pool.cleanliness < 50 for pool in self.pools):
            print("\033[1;33mYour pools are too dirty. Clean them to improve guest satisfaction.\033[0m")
        
        if self.entry_fee > 5000:
            print("\033[1;33mYour entry fee is very high. Consider lowering it to attract more guests.\033[0m")
        elif self.entry_fee < 1000 and self.reputation > 50:
            print("\033[1;32mYour entry fee is quite low. You could increase it given your good reputation.\033[0m")
        
        if not self.staff_manager.staff:
            print("\033[1;31mHire some staff to improve service quality.\033[0m")
        elif self.staff_manager.get_average_happiness() < 40:
            print("\033[1;33mYour staff happiness is low. Consider giving bonuses.\033[0m")
        
        if not self.facilities:
            print("\033[1;32mAdding facilities like restaurants or gift shops can increase income.\033[0m")
        
        input("\nPress Enter to continue to the next day...")
        
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
        print(f"\n\033[1;36m{self.name}\033[0m - Day {self.day} ({self.season})")
        print(f"Weather: \033[1;34m{self.weather}\033[0m")
        print(f"Money: \033[1;33m¥{self.money:,}\033[0m")
        print(f"Entry Fee: \033[1;32m¥{self.entry_fee:,}\033[0m")
        print(f"Reputation: \033[1;35m{self.reputation:.2f}\033[0m/100")
        print(f"Guests today: \033[1;36m{self.guests}\033[0m")
        print(f"Daily income: \033[1;32m¥{self.daily_income:,}\033[0m")
        print(f"Daily expenses: \033[1;31m¥{self.daily_expenses:,}\033[0m")
        profit = self.daily_income - self.daily_expenses
        profit_color = "\033[1;32m" if profit >= 0 else "\033[1;31m"
        print(f"Profit/Loss: {profit_color}¥{profit:,}\033[0m")
        
        # Display dynamic onsen pool ASCII art
        print("\n\033[1;36m=== YOUR ONSEN POOLS ===\033[0m")
        print(generate_onsen_ascii(self.pools))
        
        # Display facilities summary
        print("\n\033[1;36m=== FACILITIES SUMMARY ===\033[0m")
        print(generate_facilities_summary(self.facilities))
        
        # Display rooms summary
        print("\n\033[1;36m=== ACCOMMODATION SUMMARY ===\033[0m")
        print(generate_rooms_summary(self.facilities))
        
        # Show active promotions
        if self.marketing_manager.active_promotions:
            print("\n\033[1;33mActive Promotions:\033[0m")
            for promo in self.marketing_manager.active_promotions:
                print(f"- \033[1;33m{promo.name}\033[0m ({promo.discount_percent}% off, {promo.days_remaining} days left)")
        
        # Show active campaigns
        if self.marketing_manager.active_campaigns:
            print("\n\033[1;36mActive Marketing Campaigns:\033[0m")
            for campaign in self.marketing_manager.active_campaigns:
                print(f"- \033[1;36m{campaign.name}\033[0m ({campaign.days_remaining} days left)")
        
        print("\n" + "="*50)

def manage_pools(resort):
    """Menu for managing onsen pools."""
    while True:
        clear_screen()
        print_ascii_art()
        print_pool_ascii()
        print("\nONSEN POOL MANAGEMENT")
        print("=" * 50)
        
        # Display existing pools
        if resort.pools:
            print("\nYour Onsen Pools:")
            for i, pool in enumerate(resort.pools):
                print(f"{i+1}. {pool.name} ({pool.size}, {pool.temperature}°C)")
        else:
            print("\nYou don't have any onsen pools yet!")
        
        print("\nOptions:")
        print("1. Build a new pool")
        print("2. View/Modify pool details")
        print("3. Add ingredients to a pool")
        print("4. Clean a pool")
        print("5. Return to main menu")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            # Build new pool
            name = input("Enter pool name: ")
            
            print("\nSelect pool size:")
            print("1. Small (¥50,000, capacity: 10)")
            print("2. Medium (¥100,000, capacity: 25)")
            print("3. Large (¥200,000, capacity: 50)")
            
            size_choice = input("Enter choice (1-3): ")
            if size_choice == "1":
                size = "Small"
                cost = 50000
            elif size_choice == "2":
                size = "Medium"
                cost = 100000
            elif size_choice == "3":
                size = "Large"
                cost = 200000
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                continue
            
            try:
                temp = float(input("Enter water temperature (°C): "))
                if temp < 20 or temp > 50:
                    print("Temperature should be between 20°C and 50°C for safety.")
                    input("Press Enter to continue...")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                continue
            
            # Check if resort can afford it
            if resort.money < cost:
                print(f"You don't have enough money! Cost: ¥{cost:,}, Your money: ¥{resort.money:,}")
                input("Press Enter to continue...")
                continue
            
            # Build the pool
            resort.money -= cost
            new_pool = OnsenPool(name, size, temp)
            resort.pools.append(new_pool)
            # Reset boredom factor when adding new pools
            resort.last_upgrade_day = resort.day
            resort.boredom_factor = 0
            print(f"Successfully built {name}!")
            print("Guests will be excited about the new pool!")
            input("Press Enter to continue...")
            
        elif choice == "2":
            if not resort.pools:
                print("You don't have any pools to modify!")
                input("Press Enter to continue...")
                continue
                
            try:
                pool_idx = int(input("Enter pool number to view/modify: ")) - 1
                if not 0 <= pool_idx < len(resort.pools):
                    print("Invalid pool number.")
                    input("Press Enter to continue...")
                    continue
                    
                pool = resort.pools[pool_idx]
                print(f"\n{pool}")
                
                print("\nModify:")
                print("1. Change name")
                print("2. Change temperature")
                print("3. Back")
                
                mod_choice = input("Enter choice (1-3): ")
                if mod_choice == "1":
                    new_name = input("Enter new name: ")
                    pool.name = new_name
                    print("Name updated!")
                elif mod_choice == "2":
                    try:
                        new_temp = float(input("Enter new temperature (°C): "))
                        if 20 <= new_temp <= 50:
                            pool.temperature = new_temp
                            print("Temperature updated!")
                        else:
                            print("Temperature should be between 20°C and 50°C for safety.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "3":
            if not resort.pools:
                print("You don't have any pools to add ingredients to!")
                input("Press Enter to continue...")
                continue
                
            try:
                pool_idx = int(input("Enter pool number to add ingredients to: ")) - 1
                if not 0 <= pool_idx < len(resort.pools):
                    print("Invalid pool number.")
                    input("Press Enter to continue...")
                    continue
                    
                pool = resort.pools[pool_idx]
                
                print("\nAvailable Ingredients:")
                for i, ingredient in enumerate(INGREDIENTS):
                    print(f"{i+1}. {ingredient.name} - ¥{ingredient.cost}/day")
                    print(f"   {ingredient.description}")
                
                try:
                    ing_idx = int(input("\nEnter ingredient number to add (0 to cancel): ")) - 1
                    if ing_idx == -1:
                        continue
                    if not 0 <= ing_idx < len(INGREDIENTS):
                        print("Invalid ingredient number.")
                        input("Press Enter to continue...")
                        continue
                        
                    ingredient = INGREDIENTS[ing_idx]
                    
                    # Check if ingredient is already in the pool
                    if any(ing.name == ingredient.name for ing in pool.ingredients):
                        print("This ingredient is already in the pool!")
                        input("Press Enter to continue...")
                        continue
                    
                    # Add the ingredient
                    pool.add_ingredient(ingredient)
                    print(f"Added {ingredient.name} to {pool.name}!")
                    input("Press Enter to continue...")
                    
                except ValueError:
                    print("Please enter a valid number.")
                    input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "4":
            if not resort.pools:
                print("You don't have any pools to clean!")
                input("Press Enter to continue...")
                continue
                
            try:
                pool_idx = int(input("Enter pool number to clean: ")) - 1
                if not 0 <= pool_idx < len(resort.pools):
                    print("Invalid pool number.")
                    input("Press Enter to continue...")
                    continue
                    
                pool = resort.pools[pool_idx]
                
                # Cleaning cost based on size
                cleaning_cost = {"Small": 2000, "Medium": 4000, "Large": 8000}[pool.size]
                
                print(f"Cleaning cost: ¥{cleaning_cost}")
                confirm = input("Proceed with cleaning? (y/n): ").lower()
                
                if confirm == 'y':
                    if resort.money < cleaning_cost:
                        print("You don't have enough money for cleaning!")
                    else:
                        resort.money -= cleaning_cost
                        pool.clean()
                        print(f"{pool.name} has been cleaned!")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

if __name__ == "__main__":
    clear_screen()
    print_ascii_art()
    print("\nWelcome to the Onsen Resort Management Game!")
    print("In this game, you'll manage your own hot spring resort in Japan.")
    print("Build onsen pools, add facilities, hire staff, and attract guests!")
    input("\nPress Enter to start...")
    main_menu()
def manage_facilities(resort):
    """Menu for managing resort facilities."""
    while True:
        clear_screen()
        print_ascii_art()
        print_facility_ascii()
        print("\nFACILITY MANAGEMENT")
        print("=" * 50)
        
        # Display existing facilities
        if resort.facilities:
            print("\nYour Facilities:")
            for i, facility in enumerate(resort.facilities):
                if isinstance(facility, Restaurant):
                    facility_type = "Restaurant"
                elif isinstance(facility, GiftShop):
                    facility_type = "Gift Shop"
                elif isinstance(facility, Accommodation):
                    facility_type = "Accommodation"
                elif isinstance(facility, Entertainment):
                    facility_type = "Entertainment"
                else:
                    facility_type = "Facility"
                print(f"{i+1}. {facility.name} ({facility_type})")
        else:
            print("\nYou don't have any facilities yet!")
        
        print("\nOptions:")
        print("1. Build a new facility")
        print("2. View facility details")
        print("3. Upgrade a facility")
        print("4. Return to main menu")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            # Build new facility
            print("\nSelect facility type:")
            print("1. Restaurant")
            print("2. Gift Shop")
            print("3. Accommodation")
            print("4. Entertainment")
            print("5. Cancel")
            
            type_choice = input("Enter choice (1-5): ")
            
            if type_choice == "5":
                continue
                
            name = input("Enter facility name: ")
            
            if type_choice == "1":
                # Restaurant
                print("\nSelect cuisine type:")
                cuisines = ["Japanese", "International", "Seafood", "BBQ", "Vegetarian"]
                for i, cuisine in enumerate(cuisines):
                    print(f"{i+1}. {cuisine}")
                
                try:
                    cuisine_idx = int(input("Enter choice (1-5): ")) - 1
                    if not 0 <= cuisine_idx < len(cuisines):
                        print("Invalid choice.")
                        input("Press Enter to continue...")
                        continue
                    
                    cuisine = cuisines[cuisine_idx]
                    
                    print("\nSelect price tier:")
                    print("1. Budget (¥200,000)")
                    print("2. Standard (¥400,000)")
                    print("3. Premium (¥600,000)")
                    
                    tier_choice = input("Enter choice (1-3): ")
                    if tier_choice == "1":
                        price_tier = 1
                        cost = 200000
                    elif tier_choice == "2":
                        price_tier = 2
                        cost = 400000
                    elif tier_choice == "3":
                        price_tier = 3
                        cost = 600000
                    else:
                        print("Invalid choice.")
                        input("Press Enter to continue...")
                        continue
                    
                    # Check if resort can afford it
                    if resort.money < cost:
                        print(f"You don't have enough money! Cost: ¥{cost:,}, Your money: ¥{resort.money:,}")
                        input("Press Enter to continue...")
                        continue
                    
                    # Build the restaurant
                    resort.money -= cost
                    new_facility = Restaurant(name, cuisine, price_tier)
                    resort.facilities.append(new_facility)
                    print(f"Successfully built {name} restaurant!")
                    
                except ValueError:
                    print("Please enter a valid number.")
                    input("Press Enter to continue...")
                    continue
                
            elif type_choice == "2":
                # Gift Shop
                print("\nSelect shop size:")
                print("1. Small (¥100,000)")
                print("2. Medium (¥200,000)")
                print("3. Large (¥300,000)")
                
                size_choice = input("Enter choice (1-3): ")
                if size_choice == "1":
                    size = 1
                    cost = 100000
                elif size_choice == "2":
                    size = 2
                    cost = 200000
                elif size_choice == "3":
                    size = 3
                    cost = 300000
                else:
                    print("Invalid choice.")
                    input("Press Enter to continue...")
                    continue
                
                # Check if resort can afford it
                if resort.money < cost:
                    print(f"You don't have enough money! Cost: ¥{cost:,}, Your money: ¥{resort.money:,}")
                    input("Press Enter to continue...")
                    continue
                
                # Build the gift shop
                resort.money -= cost
                new_facility = GiftShop(name, size)
                resort.facilities.append(new_facility)
                print(f"Successfully built {name} gift shop!")
                
            elif type_choice == "3":
                # Accommodation
                print("\nSelect accommodation style:")
                styles = ["Japanese", "Western", "Mixed"]
                for i, style in enumerate(styles):
                    print(f"{i+1}. {style}")
                
                try:
                    style_idx = int(input("Enter choice (1-3): ")) - 1
                    if not 0 <= style_idx < len(styles):
                        print("Invalid choice.")
                        input("Press Enter to continue...")
                        continue
                    
                    style = styles[style_idx]
                    
                    try:
                        rooms = int(input("Enter number of rooms (5-50): "))
                        if not 5 <= rooms <= 50:
                            print("Number of rooms should be between 5 and 50.")
                            input("Press Enter to continue...")
                            continue
                    except ValueError:
                        print("Please enter a valid number.")
                        input("Press Enter to continue...")
                        continue
                    
                    print("\nSelect quality level:")
                    print("1. Budget")
                    print("2. Standard")
                    print("3. Luxury")
                    
                    quality_choice = input("Enter choice (1-3): ")
                    if quality_choice == "1":
                        quality_level = 1
                    elif quality_choice == "2":
                        quality_level = 2
                    elif quality_choice == "3":
                        quality_level = 3
                    else:
                        print("Invalid choice.")
                        input("Press Enter to continue...")
                        continue
                    
                    # Calculate cost
                    cost = 500000 + (rooms * 50000 * quality_level)
                    
                    print(f"\nTotal construction cost: ¥{cost:,}")
                    confirm = input("Proceed with construction? (y/n): ").lower()
                    
                    if confirm != 'y':
                        continue
                    
                    # Check if resort can afford it
                    if resort.money < cost:
                        print(f"You don't have enough money! Cost: ¥{cost:,}, Your money: ¥{resort.money:,}")
                        input("Press Enter to continue...")
                        continue
                    
                    # Build the accommodation
                    resort.money -= cost
                    new_facility = Accommodation(name, style, rooms, quality_level)
                    resort.facilities.append(new_facility)
                    print(f"Successfully built {name} accommodation!")
                    
                except ValueError:
                    print("Please enter a valid number.")
                    input("Press Enter to continue...")
                    continue
                
            elif type_choice == "4":
                # Entertainment
                print("\nSelect entertainment type:")
                types = ["Karaoke", "Game Room", "Spa Treatment", "Massage", "Theater"]
                for i, type_name in enumerate(types):
                    print(f"{i+1}. {type_name}")
                
                try:
                    type_idx = int(input("Enter choice (1-5): ")) - 1
                    if not 0 <= type_idx < len(types):
                        print("Invalid choice.")
                        input("Press Enter to continue...")
                        continue
                    
                    type_name = types[type_idx]
                    
                    print("\nSelect facility size:")
                    print("1. Small (¥150,000)")
                    print("2. Medium (¥300,000)")
                    print("3. Large (¥450,000)")
                    
                    size_choice = input("Enter choice (1-3): ")
                    if size_choice == "1":
                        size = 1
                        cost = 150000
                    elif size_choice == "2":
                        size = 2
                        cost = 300000
                    elif size_choice == "3":
                        size = 3
                        cost = 450000
                    else:
                        print("Invalid choice.")
                        input("Press Enter to continue...")
                        continue
                    
                    # Check if resort can afford it
                    if resort.money < cost:
                        print(f"You don't have enough money! Cost: ¥{cost:,}, Your money: ¥{resort.money:,}")
                        input("Press Enter to continue...")
                        continue
                    
                    # Build the entertainment facility
                    resort.money -= cost
                    new_facility = Entertainment(name, type_name, size)
                    resort.facilities.append(new_facility)
                    print(f"Successfully built {name} {type_name}!")
                    
                except ValueError:
                    print("Please enter a valid number.")
                    input("Press Enter to continue...")
                    continue
            
            input("Press Enter to continue...")
            
        elif choice == "2":
            if not resort.facilities:
                print("You don't have any facilities to view!")
                input("Press Enter to continue...")
                continue
                
            try:
                facility_idx = int(input("Enter facility number to view: ")) - 1
                if not 0 <= facility_idx < len(resort.facilities):
                    print("Invalid facility number.")
                    input("Press Enter to continue...")
                    continue
                    
                facility = resort.facilities[facility_idx]
                print(f"\n{facility}")
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "3":
            if not resort.facilities:
                print("You don't have any facilities to upgrade!")
                input("Press Enter to continue...")
                continue
                
            try:
                facility_idx = int(input("Enter facility number to upgrade: ")) - 1
                if not 0 <= facility_idx < len(resort.facilities):
                    print("Invalid facility number.")
                    input("Press Enter to continue...")
                    continue
                    
                facility = resort.facilities[facility_idx]
                
                # Calculate upgrade cost based on current quality
                upgrade_cost = 10000 * (facility.quality // 10)
                
                print(f"\nCurrent quality: {facility.quality}/100")
                print(f"Upgrade cost: ¥{upgrade_cost:,}")
                print("This will increase quality by 10 points.")
                
                confirm = input("Proceed with upgrade? (y/n): ").lower()
                
                if confirm == 'y':
                    if resort.money < upgrade_cost:
                        print("You don't have enough money for the upgrade!")
                    else:
                        resort.money -= upgrade_cost
                        facility.upgrade(10)
                        # Reset boredom factor when upgrading facilities
                        resort.last_upgrade_day = resort.day
                        resort.boredom_factor = 0
                        print(f"{facility.name} has been upgraded to quality {facility.quality}!")
                        print("Guests will be excited about the improvements!")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
            time.sleep(1)
def manage_staff(resort):
    """Menu for managing resort staff."""
    while True:
        clear_screen()
        print_ascii_art()
        print("\nSTAFF MANAGEMENT")
        print("=" * 50)
        
        # Display current staff
        if resort.staff_manager.staff:
            print("\nYour Staff:")
            for i, staff in enumerate(resort.staff_manager.staff):
                print(f"{i+1}. {staff.name} - {staff.role} (Skill: {'★' * staff.skill_level}{'☆' * (5 - staff.skill_level)})")
        else:
            print("\nYou don't have any staff yet!")
        
        # Display total salary
        total_salary = resort.staff_manager.get_total_salary()
        print(f"\nTotal Daily Salary: ¥{total_salary:,}")
        
        print("\nOptions:")
        print("1. Hire new staff")
        print("2. View staff details")
        print("3. Fire staff")
        print("4. Give bonuses")
        print("5. Return to main menu")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            # Hire new staff
            if not resort.staff_manager.available_candidates:
                print("No candidates available. Refreshing candidate pool...")
                resort.staff_manager.refresh_candidates()
            
            print("\nAvailable Candidates:")
            for i, candidate in enumerate(resort.staff_manager.available_candidates):
                print(f"{i+1}. {candidate.name} - {candidate.role}")
                print(f"   Skill: {'★' * candidate.skill_level}{'☆' * (5 - candidate.skill_level)}")
                print(f"   Salary: ¥{int(candidate.salary)}/day")
            
            try:
                candidate_idx = int(input("\nEnter candidate number to hire (0 to refresh candidates): ")) - 1
                
                if candidate_idx == -1:
                    resort.staff_manager.refresh_candidates()
                    print("Candidate pool refreshed!")
                    input("Press Enter to continue...")
                    continue
                
                if not 0 <= candidate_idx < len(resort.staff_manager.available_candidates):
                    print("Invalid candidate number.")
                    input("Press Enter to continue...")
                    continue
                
                # Hire the candidate
                new_staff = resort.staff_manager.hire(candidate_idx)
                if new_staff:
                    print(f"Successfully hired {new_staff.name} as {new_staff.role}!")
                else:
                    print("Failed to hire candidate.")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "2":
            if not resort.staff_manager.staff:
                print("You don't have any staff to view!")
                input("Press Enter to continue...")
                continue
                
            try:
                staff_idx = int(input("Enter staff number to view: ")) - 1
                if not 0 <= staff_idx < len(resort.staff_manager.staff):
                    print("Invalid staff number.")
                    input("Press Enter to continue...")
                    continue
                    
                staff = resort.staff_manager.staff[staff_idx]
                print(f"\n{staff}")
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "3":
            if not resort.staff_manager.staff:
                print("You don't have any staff to fire!")
                input("Press Enter to continue...")
                continue
                
            try:
                staff_idx = int(input("Enter staff number to fire: ")) - 1
                if not 0 <= staff_idx < len(resort.staff_manager.staff):
                    print("Invalid staff number.")
                    input("Press Enter to continue...")
                    continue
                    
                staff = resort.staff_manager.staff[staff_idx]
                print(f"\nAre you sure you want to fire {staff.name}?")
                confirm = input("This action cannot be undone (y/n): ").lower()
                
                if confirm == 'y':
                    fired_staff = resort.staff_manager.fire(staff_idx)
                    if fired_staff:
                        print(f"{fired_staff.name} has been fired.")
                    else:
                        print("Failed to fire staff member.")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "4":
            if not resort.staff_manager.staff:
                print("You don't have any staff to give bonuses to!")
                input("Press Enter to continue...")
                continue
                
            try:
                print("\nBonus Options:")
                print("1. Give bonus to individual staff")
                print("2. Give bonus to all staff")
                
                bonus_choice = input("Enter choice (1-2): ")
                
                if bonus_choice == "1":
                    staff_idx = int(input("Enter staff number to give bonus: ")) - 1
                    if not 0 <= staff_idx < len(resort.staff_manager.staff):
                        print("Invalid staff number.")
                        input("Press Enter to continue...")
                        continue
                        
                    staff = resort.staff_manager.staff[staff_idx]
                    
                    try:
                        bonus_amount = int(input("Enter bonus amount (¥): "))
                        if bonus_amount <= 0:
                            print("Bonus amount must be positive.")
                            input("Press Enter to continue...")
                            continue
                            
                        if resort.money < bonus_amount:
                            print("You don't have enough money for this bonus!")
                            input("Press Enter to continue...")
                            continue
                            
                        resort.money -= bonus_amount
                        staff.give_bonus(bonus_amount)
                        print(f"Gave a ¥{bonus_amount:,} bonus to {staff.name}!")
                        print(f"Happiness increased to {staff.happiness}/100")
                        
                    except ValueError:
                        print("Please enter a valid number.")
                        
                elif bonus_choice == "2":
                    try:
                        bonus_amount = int(input("Enter bonus amount per staff (¥): "))
                        if bonus_amount <= 0:
                            print("Bonus amount must be positive.")
                            input("Press Enter to continue...")
                            continue
                            
                        total_bonus = bonus_amount * len(resort.staff_manager.staff)
                        
                        if resort.money < total_bonus:
                            print(f"You don't have enough money! Total cost: ¥{total_bonus:,}")
                            input("Press Enter to continue...")
                            continue
                            
                        resort.money -= total_bonus
                        for staff in resort.staff_manager.staff:
                            staff.give_bonus(bonus_amount)
                            
                        print(f"Gave a ¥{bonus_amount:,} bonus to all staff!")
                        print(f"Total cost: ¥{total_bonus:,}")
                        
                    except ValueError:
                        print("Please enter a valid number.")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            time.sleep(1)
def manage_marketing(resort):
    """Menu for managing marketing and promotions."""
    while True:
        clear_screen()
        print_ascii_art()
        print("\nMARKETING & PROMOTION")
        print("=" * 50)
        
        # Display active campaigns
        if resort.marketing_manager.active_campaigns:
            print("\nActive Marketing Campaigns:")
            for i, campaign in enumerate(resort.marketing_manager.active_campaigns):
                print(f"{i+1}. {campaign.name} ({campaign.days_remaining} days left)")
        else:
            print("\nNo active marketing campaigns.")
        
        # Display active promotions
        if resort.marketing_manager.active_promotions:
            print("\nActive Promotions:")
            for i, promo in enumerate(resort.marketing_manager.active_promotions):
                print(f"{i+1}. {promo.name} ({promo.discount_percent}% off, {promo.days_remaining} days left)")
        else:
            print("\nNo active promotions.")
        
        print("\nOptions:")
        print("1. Start marketing campaign")
        print("2. Start promotion")
        print("3. View campaign details")
        print("4. View promotion details")
        print("5. Return to main menu")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            # Start marketing campaign
            print("\nAvailable Marketing Campaigns:")
            for i, campaign in enumerate(resort.marketing_manager.campaigns):
                if any(active.name == campaign.name for active in resort.marketing_manager.active_campaigns):
                    print(f"{i+1}. {campaign.name} - ¥{campaign.cost:,} (Already active)")
                else:
                    print(f"{i+1}. {campaign.name} - ¥{campaign.cost:,}")
                print(f"   Duration: {campaign.duration} days")
                print(f"   Effect: {campaign.effect_description}")
            
            try:
                campaign_idx = int(input("\nEnter campaign number to start (0 to cancel): ")) - 1
                
                if campaign_idx == -1:
                    continue
                    
                if not 0 <= campaign_idx < len(resort.marketing_manager.campaigns):
                    print("Invalid campaign number.")
                    input("Press Enter to continue...")
                    continue
                
                campaign = resort.marketing_manager.campaigns[campaign_idx]
                
                # Check if campaign is already active
                if any(active.name == campaign.name for active in resort.marketing_manager.active_campaigns):
                    print("This campaign is already active!")
                    input("Press Enter to continue...")
                    continue
                
                # Check if resort can afford it
                if resort.money < campaign.cost:
                    print(f"You don't have enough money! Cost: ¥{campaign.cost:,}, Your money: ¥{resort.money:,}")
                    input("Press Enter to continue...")
                    continue
                
                # Start the campaign
                success = resort.marketing_manager.start_campaign(campaign_idx, resort)
                if success:
                    print(f"Successfully started {campaign.name} campaign!")
                else:
                    print("Failed to start campaign.")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "2":
            # Start promotion
            print("\nAvailable Promotions:")
            for i, promo in enumerate(resort.marketing_manager.promotions):
                if any(active.name == promo.name for active in resort.marketing_manager.active_promotions):
                    print(f"{i+1}. {promo.name} (Already active)")
                else:
                    print(f"{i+1}. {promo.name}")
                print(f"   Discount: {promo.discount_percent}% off {promo.target}")
                print(f"   Duration: {promo.duration} days")
            
            try:
                promo_idx = int(input("\nEnter promotion number to start (0 to cancel): ")) - 1
                
                if promo_idx == -1:
                    continue
                    
                if not 0 <= promo_idx < len(resort.marketing_manager.promotions):
                    print("Invalid promotion number.")
                    input("Press Enter to continue...")
                    continue
                
                promo = resort.marketing_manager.promotions[promo_idx]
                
                # Check if promotion is already active
                if any(active.name == promo.name for active in resort.marketing_manager.active_promotions):
                    print("This promotion is already active!")
                    input("Press Enter to continue...")
                    continue
                
                # Start the promotion
                success = resort.marketing_manager.start_promotion(promo_idx)
                if success:
                    print(f"Successfully started {promo.name} promotion!")
                else:
                    print("Failed to start promotion.")
                
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "3":
            # View campaign details
            if not resort.marketing_manager.campaigns:
                print("No marketing campaigns available!")
                input("Press Enter to continue...")
                continue
                
            try:
                campaign_idx = int(input("Enter campaign number to view: ")) - 1
                if not 0 <= campaign_idx < len(resort.marketing_manager.campaigns):
                    print("Invalid campaign number.")
                    input("Press Enter to continue...")
                    continue
                    
                campaign = resort.marketing_manager.campaigns[campaign_idx]
                print(f"\n{campaign}")
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "4":
            # View promotion details
            if not resort.marketing_manager.promotions:
                print("No promotions available!")
                input("Press Enter to continue...")
                continue
                
            try:
                promo_idx = int(input("Enter promotion number to view: ")) - 1
                if not 0 <= promo_idx < len(resort.marketing_manager.promotions):
                    print("Invalid promotion number.")
                    input("Press Enter to continue...")
                    continue
                    
                promo = resort.marketing_manager.promotions[promo_idx]
                print(f"\n{promo}")
                input("Press Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
                
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            time.sleep(1)
def main_menu():
    """Display the main menu and handle user input."""
    resort = OnsenResort()
    resort.name = input("Welcome! Please name your onsen resort: ")
    
    while True:
        resort.display_status()
        print("\n\033[1;36mMAIN MENU:\033[0m")
        print("\033[1;34m1. Manage Onsen Pools\033[0m")
        print("\033[1;34m2. Manage Facilities\033[0m")
        print("\033[1;34m3. Manage Staff\033[0m")
        print("\033[1;34m4. Set Entry Fee\033[0m")
        print("\033[1;34m5. Marketing & Promotion\033[0m")
        print("\033[1;34m6. Advance to Next Day\033[0m")
        print("\033[1;34m7. View Event Log\033[0m")
        print("\033[1;34m8. Quit Game\033[0m")
        print("\n\033[3;33mTip: Press Enter without typing anything to advance to the next day\033[0m")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == "":
            # Empty input means advance to next day
            resort.new_day()
        elif choice == "1":
            manage_pools(resort)
        elif choice == "2":
            manage_facilities(resort)
        elif choice == "3":
            manage_staff(resort)
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
            manage_marketing(resort)
        elif choice == "6":
            resort.new_day()
        elif choice == "7":
            clear_screen()
            print_ascii_art()
            print("\nEVENT LOG")
            print("=" * 50)
            
            if resort.event_log:
                for event in resort.event_log[-10:]:  # Show last 10 events
                    print(event)
            else:
                print("No events have occurred yet.")
                
            input("\nPress Enter to continue...")
        elif choice == "8":
            if input("Are you sure you want to quit? (y/n): ").lower() == 'y':
                print("Thank you for playing!")
                break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)
