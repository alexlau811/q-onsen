#!/usr/bin/env python3
"""
Quick test script to verify game functionality and check balance.
"""

import sys
import os

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

def test_basic_functionality():
    """Test basic game functionality."""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        # Create resort
        resort = OnsenResort()
        print(f"✅ Resort created with ¥{resort.money:,} starting money")
        
        # Add a pool
        pool = OnsenPool("Test Pool", "Medium", 40)
        resort.pools.append(pool)
        print(f"✅ Pool added: {pool.name}")
        
        # Add a facility
        restaurant = Restaurant("Test Restaurant", "Japanese", 2)
        resort.facilities.append(restaurant)
        print(f"✅ Facility added: {restaurant.name}")
        
        # Hire staff (add directly for testing)
        staff = Staff("Test Cleaner", "Cleaner", 5)
        resort.staff_manager.staff.append(staff)
        print(f"✅ Staff added: {staff.name}")
        
        # Run one day
        initial_money = resort.money
        resort.new_day()
        print(f"✅ Day simulation completed")
        print(f"   Money change: ¥{resort.money - initial_money:,}")
        print(f"   Guests: {resort.guests}")
        print(f"   Reputation: {resort.reputation}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        return False

def test_game_balance():
    """Test game balance scenarios."""
    print("\n⚖️  Testing Game Balance...")
    
    scenarios = [
        ("Minimal Resort", create_minimal_resort),
        ("Balanced Resort", create_balanced_resort),
        ("Premium Resort", create_premium_resort)
    ]
    
    results = {}
    
    for scenario_name, setup_func in scenarios:
        print(f"\n📊 Testing {scenario_name}...")
        
        try:
            resort = OnsenResort()
            setup_func(resort)
            
            initial_money = resort.money
            profits = []
            
            # Simulate 10 days
            for day in range(10):
                day_start = resort.money
                resort.new_day()
                daily_profit = resort.money - day_start
                profits.append(daily_profit)
            
            total_profit = resort.money - initial_money
            avg_profit = sum(profits) / len(profits)
            profitable_days = sum(1 for p in profits if p > 0)
            
            results[scenario_name] = {
                'total_profit': total_profit,
                'avg_daily_profit': avg_profit,
                'profitable_days': profitable_days,
                'final_reputation': resort.reputation,
                'final_guests': resort.guests
            }
            
            print(f"   Total Profit: ¥{total_profit:,}")
            print(f"   Avg Daily Profit: ¥{avg_profit:,.0f}")
            print(f"   Profitable Days: {profitable_days}/10")
            print(f"   Final Reputation: {resort.reputation}")
            
        except Exception as e:
            print(f"❌ Error testing {scenario_name}: {e}")
            results[scenario_name] = None
    
    return results

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
        GiftShop("Gift Shop", 2)  # Size 2 = medium
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
        GiftShop("Premium Shop", 3)  # Size 3 = large
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

def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\n🔍 Testing Edge Cases...")
    
    try:
        resort = OnsenResort()
        
        # Test with no pools
        print("Testing resort with no pools...")
        initial_rep = resort.reputation
        resort.new_day()
        if resort.reputation <= initial_rep:
            print("✅ Reputation correctly decreased without pools")
        else:
            print("⚠️  Reputation didn't decrease without pools")
        
        # Test hiring with insufficient funds
        print("Testing hiring with insufficient funds...")
        resort.money = 100  # Very low money
        
        # Try to hire from available candidates
        if resort.staff_manager.available_candidates:
            initial_staff_count = len(resort.staff_manager.staff)
            hired_staff = resort.staff_manager.hire(0)  # Try to hire first candidate
            if hired_staff:
                print("⚠️  Hiring succeeded despite low funds (may need balance adjustment)")
            else:
                print("✅ Correctly prevented hiring with insufficient funds")
        else:
            print("⚠️  No candidates available to test hiring")
        
        # Test extreme entry fee
        print("Testing extreme entry fee...")
        resort.entry_fee = 50000  # Very high fee
        resort.new_day()
        print(f"   Guests with high fee: {resort.guests}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in edge case testing: {e}")
        return False

def main():
    """Run all tests."""
    print("🎮 Onsen Resort Management Game - Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    basic_test_passed = test_basic_functionality()
    
    if not basic_test_passed:
        print("\n❌ Basic functionality tests failed. Please fix core issues first.")
        return
    
    # Test game balance
    balance_results = test_game_balance()
    
    # Test edge cases
    edge_test_passed = test_edge_cases()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"Basic Functionality: {'✅ PASS' if basic_test_passed else '❌ FAIL'}")
    print(f"Edge Cases: {'✅ PASS' if edge_test_passed else '❌ FAIL'}")
    
    print("\nBalance Analysis:")
    for scenario, results in balance_results.items():
        if results:
            status = "✅ Profitable" if results['total_profit'] > 0 else "⚠️  Unprofitable"
            print(f"  {scenario}: {status} (¥{results['total_profit']:,} total)")
        else:
            print(f"  {scenario}: ❌ Failed to test")
    
    print("\n🎯 Recommendations:")
    if balance_results.get("Minimal Resort") and balance_results["Minimal Resort"]['total_profit'] < 0:
        print("  - Consider adjusting starting money or reducing initial costs")
    
    if balance_results.get("Premium Resort") and balance_results["Premium Resort"]['total_profit'] < balance_results.get("Balanced Resort", {}).get('total_profit', 0):
        print("  - Premium setup might need better profit margins")
    
    print("\n✨ Testing complete!")

if __name__ == "__main__":
    main()
