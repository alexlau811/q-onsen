#!/usr/bin/env python3
"""
Silent test script for game balance analysis without user input.
"""

import sys
import os
from unittest.mock import patch

# Add the game directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'onsen_game'))

try:
    from onsen_game.game import OnsenResort
    from onsen_game.pools import OnsenPool, INGREDIENTS
    from onsen_game.facilities import Restaurant, GiftShop
    from onsen_game.staff import Staff
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def create_minimal_resort(resort):
    """Create a minimal resort setup."""
    resort.pools.append(OnsenPool("Basic Pool", "Small", 40))
    resort.entry_fee = 1000

def create_balanced_resort(resort):
    """Create a balanced resort setup."""
    # Pools
    resort.pools.extend([
        OnsenPool("Main Pool", "Medium", 40),
        OnsenPool("Quiet Pool", "Small", 38)
    ])
    
    # Facilities
    resort.facilities.extend([
        Restaurant("Restaurant", "Japanese", 2),
        GiftShop("Gift Shop", 2)
    ])
    
    # Staff (add directly for testing)
    cleaner = Staff("Cleaner", "Cleaner", 6)
    attendant = Staff("Attendant", "Attendant", 5)
    
    resort.staff_manager.staff.extend([cleaner, attendant])
    
    resort.entry_fee = 1500

def create_premium_resort(resort):
    """Create a premium resort setup."""
    # Premium pools with ingredients
    pool1 = OnsenPool("Luxury Pool", "Large", 41)
    pool1.add_ingredient(INGREDIENTS[0])  # Sulfur
    
    pool2 = OnsenPool("Family Pool", "Medium", 39)
    pool2.add_ingredient(INGREDIENTS[1])  # Iron
    
    resort.pools.extend([pool1, pool2])
    
    # Premium facilities
    resort.facilities.extend([
        Restaurant("Fine Dining", "Kaiseki", 3),
        GiftShop("Premium Shop", 3)
    ])
    
    # Quality staff (add directly for testing)
    staff_members = [
        Staff("Head Cleaner", "Cleaner", 9),
        Staff("Senior Attendant", "Attendant", 8),
        Staff("Manager", "Manager", 9)
    ]
    
    resort.staff_manager.staff.extend(staff_members)
    
    resort.entry_fee = 3000
    resort.reputation = 70

def test_scenario_silently(scenario_name, setup_func, days=10):
    """Test a scenario without user input."""
    print(f"\n📊 Testing {scenario_name}...")
    
    try:
        resort = OnsenResort()
        setup_func(resort)
        
        initial_money = resort.money
        profits = []
        
        # Mock input to avoid waiting for user input
        with patch('builtins.input', return_value=''):
            for day in range(days):
                day_start = resort.money
                resort.new_day()
                daily_profit = resort.money - day_start
                profits.append(daily_profit)
        
        total_profit = resort.money - initial_money
        avg_profit = sum(profits) / len(profits)
        profitable_days = sum(1 for p in profits if p > 0)
        
        print(f"   Total Profit: ¥{total_profit:,}")
        print(f"   Avg Daily Profit: ¥{avg_profit:,.0f}")
        print(f"   Profitable Days: {profitable_days}/{days}")
        print(f"   Final Reputation: {resort.reputation:.1f}")
        print(f"   Final Guest Count: {resort.guests}")
        
        return {
            'total_profit': total_profit,
            'avg_daily_profit': avg_profit,
            'profitable_days': profitable_days,
            'final_reputation': resort.reputation,
            'final_guests': resort.guests
        }
        
    except Exception as e:
        print(f"❌ Error testing {scenario_name}: {e}")
        return None

def main():
    """Run silent balance analysis."""
    print("🎮 Onsen Resort Management Game - Silent Balance Test")
    print("=" * 60)
    
    scenarios = [
        ("Minimal Resort", create_minimal_resort),
        ("Balanced Resort", create_balanced_resort),
        ("Premium Resort", create_premium_resort)
    ]
    
    results = {}
    
    for scenario_name, setup_func in scenarios:
        results[scenario_name] = test_scenario_silently(scenario_name, setup_func)
    
    # Summary
    print("\n📋 Balance Analysis Summary")
    print("=" * 40)
    
    for scenario, result in results.items():
        if result:
            status = "✅ Profitable" if result['total_profit'] > 0 else "⚠️  Unprofitable"
            roi = (result['total_profit'] / 100000) * 100  # ROI based on starting money
            print(f"{scenario}:")
            print(f"  Status: {status}")
            print(f"  Total Profit: ¥{result['total_profit']:,}")
            print(f"  ROI: {roi:.1f}%")
            print(f"  Avg Daily: ¥{result['avg_daily_profit']:,.0f}")
            print(f"  Success Rate: {result['profitable_days']}/10 days")
            print(f"  Final Reputation: {result['final_reputation']:.1f}")
            print()
        else:
            print(f"{scenario}: ❌ Failed to test")
    
    # Recommendations
    print("🎯 Balance Recommendations:")
    
    if results.get("Minimal Resort") and results["Minimal Resort"]['total_profit'] > 500000:
        print("  - Minimal setup might be too profitable - consider increasing costs")
    
    if results.get("Premium Resort") and results.get("Balanced Resort"):
        premium = results["Premium Resort"]
        balanced = results["Balanced Resort"]
        if premium and balanced and premium['total_profit'] < balanced['total_profit']:
            print("  - Premium setup should be more profitable than balanced setup")
    
    profitable_scenarios = [name for name, result in results.items() if result and result['total_profit'] > 0]
    print(f"  - {len(profitable_scenarios)}/3 scenarios are profitable")
    
    if len(profitable_scenarios) == 3:
        print("  - All scenarios are profitable - game balance looks good!")
    elif len(profitable_scenarios) < 2:
        print("  - Too few profitable scenarios - consider reducing costs or increasing income")

if __name__ == "__main__":
    main()
