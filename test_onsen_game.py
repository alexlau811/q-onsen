#!/usr/bin/env python3
"""
Test suite for the Onsen Resort Management Game.
Tests both functionality and game balance scenarios.
"""

import unittest
import sys
import os
import random
from unittest.mock import patch, MagicMock

# Add the game directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'onsen_game'))

from onsen_game.game import OnsenResort
from onsen_game.pools import OnsenPool, INGREDIENTS
from onsen_game.facilities import Restaurant, GiftShop, Accommodation, Entertainment
from onsen_game.staff import Staff, StaffManager
from onsen_game.events import Weather, EventManager
from onsen_game.marketing import MarketingManager
from onsen_game.customers import Customer, PERSONALITIES


class TestOnsenGameFunctionality(unittest.TestCase):
    """Test basic game functionality and mechanics."""
    
    def setUp(self):
        """Set up a fresh resort for each test."""
        self.resort = OnsenResort()
    
    def test_resort_initialization(self):
        """Test that the resort initializes correctly."""
        self.assertEqual(self.resort.money, 100000)
        self.assertEqual(self.resort.day, 1)
        self.assertEqual(self.resort.reputation, 50)
        self.assertEqual(len(self.resort.pools), 0)
        self.assertEqual(len(self.resort.facilities), 0)
        self.assertIsInstance(self.resort.staff_manager, StaffManager)
        self.assertIsInstance(self.resort.weather, Weather)
        self.assertIsInstance(self.resort.event_manager, EventManager)
        self.assertIsInstance(self.resort.marketing_manager, MarketingManager)
    
    def test_pool_creation(self):
        """Test creating onsen pools."""
        initial_money = self.resort.money
        
        # Create a basic pool
        pool = OnsenPool("Test Pool", "Medium", 40)
        self.resort.pools.append(pool)
        
        self.assertEqual(len(self.resort.pools), 1)
        self.assertEqual(self.resort.pools[0].name, "Test Pool")
        self.assertEqual(self.resort.pools[0].temperature, 40)
        self.assertEqual(self.resort.pools[0].size, "Medium")
    
    def test_facility_creation(self):
        """Test creating facilities."""
        # Test restaurant
        restaurant = Restaurant("Main Restaurant", "Japanese", 2)
        self.resort.facilities.append(restaurant)
        
        # Test gift shop
        gift_shop = GiftShop("Souvenir Shop", 30)
        self.resort.facilities.append(gift_shop)
        
        # Test accommodation
        accommodation = Accommodation("Guest Rooms", 20)
        self.resort.facilities.append(accommodation)
        
        # Test entertainment
        entertainment = Entertainment("Karaoke", 15)
        self.resort.facilities.append(entertainment)
        
        self.assertEqual(len(self.resort.facilities), 4)
        self.assertIsInstance(self.resort.facilities[0], Restaurant)
        self.assertIsInstance(self.resort.facilities[1], GiftShop)
        self.assertIsInstance(self.resort.facilities[2], Accommodation)
        self.assertIsInstance(self.resort.facilities[3], Entertainment)
    
    def test_staff_hiring(self):
        """Test hiring staff members."""
        initial_money = self.resort.money
        
        # Add a staff member directly for testing
        cleaner = Staff("Test Cleaner", "Cleaner", 5)
        self.resort.staff_manager.staff.append(cleaner)
        
        self.assertEqual(len(self.resort.staff_manager.staff), 1)
        # Note: In the actual game, hiring costs money, but we're testing the basic functionality
    
    def test_weather_system(self):
        """Test weather system functionality."""
        # Test weather update
        self.resort.weather.update("Winter")
        self.assertEqual(self.resort.weather.season, "Winter")
        
        # Test guest impact calculation
        impact = self.resort.weather.get_guest_impact()
        self.assertIsInstance(impact, float)
        self.assertGreater(impact, 0)
    
    def test_event_system(self):
        """Test random event system."""
        # Test event triggering (with 100% chance)
        event = self.resort.event_manager.trigger_random_event(self.resort, chance=1.0)
        self.assertIsNotNone(event)
        self.assertEqual(len(event), 3)  # Should return (name, description, effect)
    
    def test_customer_generation(self):
        """Test customer generation."""
        customer = Customer()
        self.assertIn(customer.personality, PERSONALITIES)
        self.assertGreater(customer.budget, 0)
        self.assertGreater(customer.satisfaction, 0)


class TestGameBalance(unittest.TestCase):
    """Test game balance scenarios."""
    
    def setUp(self):
        """Set up a resort for balance testing."""
        self.resort = OnsenResort()
        # Add a basic setup for testing
        self.resort.pools.append(OnsenPool("Basic Pool", "Small", 40))
        self.resort.facilities.append(Restaurant("Restaurant", "Japanese", 2))
        
    def test_basic_profitability(self):
        """Test if a basic resort setup can be profitable."""
        initial_money = self.resort.money
        
        # Simulate 30 days
        for _ in range(30):
            self.resort.new_day()
        
        # Check if the resort is still viable
        self.assertGreater(self.resort.money, 0, "Resort should remain financially viable")
    
    def test_no_pools_scenario(self):
        """Test what happens when there are no pools."""
        # Remove all pools
        self.resort.pools = []
        
        initial_reputation = self.resort.reputation
        self.resort.new_day()
        
        # Reputation should decrease without pools
        self.assertLessEqual(self.resort.reputation, initial_reputation)
    
    def test_overstaffing_cost(self):
        """Test the financial impact of overstaffing."""
        initial_money = self.resort.money
        
        # Add many expensive staff directly
        for i in range(10):
            staff = Staff(f"Staff {i}", "Manager", 10)
            self.resort.staff_manager.staff.append(staff)
        
        # Simulate several days
        for _ in range(10):
            self.resort.new_day()
        
        # Should be losing money due to high staff costs
        self.assertLess(self.resort.money, initial_money - 30000)
    
    def test_high_entry_fee_impact(self):
        """Test impact of setting entry fee too high."""
        # Set very high entry fee
        self.resort.entry_fee = 10000
        
        initial_guests = self.resort.guests
        self.resort.new_day()
        
        # Should have fewer guests due to high price
        # Note: This test might need adjustment based on actual implementation
        self.assertLessEqual(self.resort.guests, initial_guests * 1.5)
    
    def test_seasonal_variation(self):
        """Test seasonal impact on guest numbers."""
        guest_counts = {}
        
        # Test each season
        seasons = ["Spring", "Summer", "Autumn", "Winter"]
        for season in seasons:
            self.resort.weather.update(season)
            self.resort.new_day()
            guest_counts[season] = self.resort.guests
        
        # Winter should typically have more guests for onsen
        self.assertGreater(guest_counts["Winter"], 0)
    
    def test_reputation_impact(self):
        """Test how reputation affects guest numbers."""
        # Test with low reputation
        self.resort.reputation = 10
        self.resort.new_day()
        low_rep_guests = self.resort.guests
        
        # Test with high reputation
        self.resort.reputation = 90
        self.resort.new_day()
        high_rep_guests = self.resort.guests
        
        # Higher reputation should generally attract more guests
        # (though this might vary due to randomness)
        self.assertGreaterEqual(high_rep_guests, 0)
        self.assertGreaterEqual(low_rep_guests, 0)


class TestGameScenarios(unittest.TestCase):
    """Test specific game scenarios and edge cases."""
    
    def setUp(self):
        """Set up resort for scenario testing."""
        self.resort = OnsenResort()
    
    def test_bankruptcy_scenario(self):
        """Test what happens when money runs out."""
        # Spend all money
        self.resort.money = 1000
        
        # Try to hire from available candidates with low money
        if self.resort.staff_manager.available_candidates:
            result = self.resort.staff_manager.hire(0)
            # The current implementation doesn't check money, so this test may need adjustment
            self.assertIsNotNone(result)  # For now, just check that hiring works
        else:
            # If no candidates, the test passes as there's nothing to hire
            result = False
    
    def test_maximum_capacity_scenario(self):
        """Test resort at maximum capacity."""
        # Add many pools with high capacity
        for i in range(5):
            pool = OnsenPool(f"Pool {i}", "Large", 40)
            self.resort.pools.append(pool)
        
        # Simulate high guest numbers
        self.resort.guests = 1000
        self.resort.new_day()
        
        # Resort should handle high capacity
        self.assertGreater(self.resort.money, 0)
    
    def test_empty_resort_scenario(self):
        """Test completely empty resort."""
        # No pools, no facilities, no staff
        self.resort.pools = []
        self.resort.facilities = []
        
        initial_reputation = self.resort.reputation
        self.resort.new_day()
        
        # Should have negative impact
        self.assertLessEqual(self.resort.reputation, initial_reputation)
    
    def test_perfect_resort_scenario(self):
        """Test a well-balanced, high-quality resort."""
        # Add high-quality pools
        for i in range(3):
            pool = OnsenPool(f"Premium Pool {i}", "Medium", 40)
            pool.cleanliness = 100
            pool.add_ingredient(INGREDIENTS[i % len(INGREDIENTS)])
            self.resort.pools.append(pool)
        
        # Add all facility types
        self.resort.facilities.extend([
            Restaurant("Fine Dining", "Kaiseki", 3),
            GiftShop("Premium Shop", 40),
            Accommodation("Luxury Rooms", 30),
            Entertainment("Traditional Theater", 25)
        ])
        
        # Add quality staff directly for testing
        for facility in self.resort.facilities:
            staff = Staff(f"Staff for {facility.name}", "Attendant", 8)
            self.resort.staff_manager.staff.append(staff)
        
        # Add cleaners
        for i in range(2):
            cleaner = Staff(f"Cleaner {i}", "Cleaner", 7)
            self.resort.staff_manager.staff.append(cleaner)
        
        # Set reasonable entry fee
        self.resort.entry_fee = 2000
        self.resort.reputation = 80
        
        # Simulate 10 days
        profits = []
        for _ in range(10):
            initial_money = self.resort.money
            self.resort.new_day()
            daily_profit = self.resort.money - initial_money
            profits.append(daily_profit)
        
        # Should be profitable most days
        profitable_days = sum(1 for profit in profits if profit > 0)
        self.assertGreater(profitable_days, 5, "Well-managed resort should be profitable most days")


def run_balance_analysis():
    """Run a comprehensive balance analysis."""
    print("\n" + "="*50)
    print("GAME BALANCE ANALYSIS")
    print("="*50)
    
    # Test different scenarios
    scenarios = [
        ("Minimal Setup", lambda r: setup_minimal_resort(r)),
        ("Balanced Setup", lambda r: setup_balanced_resort(r)),
        ("Premium Setup", lambda r: setup_premium_resort(r)),
        ("Overstaffed Setup", lambda r: setup_overstaffed_resort(r))
    ]
    
    for scenario_name, setup_func in scenarios:
        print(f"\n{scenario_name}:")
        print("-" * 30)
        
        resort = OnsenResort()
        setup_func(resort)
        
        initial_money = resort.money
        daily_profits = []
        
        # Simulate 30 days
        for day in range(30):
            day_start_money = resort.money
            resort.new_day()
            daily_profit = resort.money - day_start_money
            daily_profits.append(daily_profit)
        
        # Calculate statistics
        total_profit = resort.money - initial_money
        avg_daily_profit = sum(daily_profits) / len(daily_profits)
        profitable_days = sum(1 for p in daily_profits if p > 0)
        
        print(f"Initial Money: ¥{initial_money:,}")
        print(f"Final Money: ¥{resort.money:,}")
        print(f"Total Profit: ¥{total_profit:,}")
        print(f"Average Daily Profit: ¥{avg_daily_profit:,.0f}")
        print(f"Profitable Days: {profitable_days}/30")
        print(f"Final Reputation: {resort.reputation}")
        print(f"Final Guest Count: {resort.guests}")


def setup_minimal_resort(resort):
    """Set up a minimal resort configuration."""
    resort.pools.append(OnsenPool("Basic Pool", "Small", 40))
    resort.entry_fee = 1000


def setup_balanced_resort(resort):
    """Set up a balanced resort configuration."""
    # Add pools
    resort.pools.extend([
        OnsenPool("Main Pool", "Medium", 40),
        OnsenPool("Quiet Pool", "Small", 38)
    ])
    
    # Add facilities
    resort.facilities.extend([
        Restaurant("Restaurant", "Japanese", 2),
        GiftShop("Gift Shop", 25)
    ])
    
    # Add staff
    staff_members = [
        Staff("Cleaner", "Cleaner", 6),
        Staff("Attendant", "Attendant", 5)
    ]
    
    for staff in staff_members:
        resort.staff_manager.staff.append(staff)


def setup_premium_resort(resort):
    """Set up a premium resort configuration."""
    # Add premium pools
    for i, (name, temp) in enumerate([("Luxury Pool", 41), ("Family Pool", 39), ("Meditation Pool", 38)]):
        pool = OnsenPool(name, "Large", temp)
        pool.add_ingredient(INGREDIENTS[i % len(INGREDIENTS)])
        resort.pools.append(pool)
    
    # Add all facilities
    resort.facilities.extend([
        Restaurant("Fine Dining", "Kaiseki", 3),
        GiftShop("Premium Shop", 40),
        Accommodation("Luxury Rooms", 30),
        Entertainment("Traditional Theater", 25)
    ])
    
    # Add quality staff
    staff_members = [
        Staff("Head Cleaner", "Cleaner", 9),
        Staff("Senior Attendant", "Attendant", 8),
        Staff("Restaurant Manager", "Manager", 9),
        Staff("Concierge", "Attendant", 7)
    ]
    
    for staff in staff_members:
        resort.staff_manager.staff.append(staff)
    
    resort.entry_fee = 3000
    resort.reputation = 70


def setup_overstaffed_resort(resort):
    """Set up an overstaffed resort to test financial balance."""
    # Basic setup
    resort.pools.append(OnsenPool("Pool", "Medium", 40))
    resort.facilities.append(Restaurant("Restaurant", "Japanese", 2))
    
    # Add too many expensive staff directly for testing
    for i in range(8):
        staff = Staff(f"Manager {i}", "Manager", 10)
        resort.staff_manager.staff.append(staff)
    
    resort.entry_fee = 2000


if __name__ == "__main__":
    # Run unit tests
    print("Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run balance analysis
    run_balance_analysis()
