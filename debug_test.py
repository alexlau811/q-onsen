#!/usr/bin/env python3
"""
Debug test to find the source of the list index out of range error.
"""

import sys
import os
import traceback

# Add the game directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'onsen_game'))

from onsen_game.game import OnsenResort
from onsen_game.pools import OnsenPool, INGREDIENTS
from onsen_game.facilities import Restaurant, GiftShop
from onsen_game.staff import Staff

def test_balanced_resort():
    """Test balanced resort setup step by step."""
    print("Creating balanced resort...")
    
    try:
        resort = OnsenResort()
        print("✅ Resort created")
        
        # Pools
        print("Adding pools...")
        pool1 = OnsenPool("Main Pool", "Medium", 40)
        print(f"✅ Pool 1 created: {pool1.name}")
        
        pool2 = OnsenPool("Quiet Pool", "Small", 38)
        print(f"✅ Pool 2 created: {pool2.name}")
        
        resort.pools.extend([pool1, pool2])
        print(f"✅ Pools added to resort: {len(resort.pools)} pools")
        
        # Facilities
        print("Adding facilities...")
        restaurant = Restaurant("Restaurant", "Japanese", 2)
        print(f"✅ Restaurant created: {restaurant.name}")
        
        gift_shop = GiftShop("Gift Shop", 2)
        print(f"✅ Gift shop created: {gift_shop.name}")
        
        resort.facilities.extend([restaurant, gift_shop])
        print(f"✅ Facilities added to resort: {len(resort.facilities)} facilities")
        
        # Staff
        print("Adding staff...")
        cleaner = Staff("Cleaner", "Cleaner", 6)
        print(f"✅ Cleaner created: {cleaner.name}")
        
        attendant = Staff("Attendant", "Attendant", 5)
        print(f"✅ Attendant created: {attendant.name}")
        
        resort.staff_manager.staff.extend([cleaner, attendant])
        print(f"✅ Staff added to resort: {len(resort.staff_manager.staff)} staff")
        
        resort.entry_fee = 1500
        print("✅ Entry fee set")
        
        print("✅ Balanced resort setup complete!")
        return resort
        
    except Exception as e:
        print(f"❌ Error in balanced resort setup: {e}")
        traceback.print_exc()
        return None

def test_premium_resort():
    """Test premium resort setup step by step."""
    print("\nCreating premium resort...")
    
    try:
        resort = OnsenResort()
        print("✅ Resort created")
        
        # Premium pools with ingredients
        print("Adding premium pools...")
        pool1 = OnsenPool("Luxury Pool", "Large", 41)
        print(f"✅ Pool 1 created: {pool1.name}")
        
        print(f"Available ingredients: {len(INGREDIENTS)}")
        print(f"First ingredient: {INGREDIENTS[0].name}")
        
        pool1.add_ingredient(INGREDIENTS[0])  # Sulfur
        print("✅ Ingredient added to pool 1")
        
        pool2 = OnsenPool("Family Pool", "Medium", 39)
        print(f"✅ Pool 2 created: {pool2.name}")
        
        pool2.add_ingredient(INGREDIENTS[1])  # Iron
        print("✅ Ingredient added to pool 2")
        
        resort.pools.extend([pool1, pool2])
        print(f"✅ Pools added to resort: {len(resort.pools)} pools")
        
        # Premium facilities
        print("Adding premium facilities...")
        restaurant = Restaurant("Fine Dining", "Kaiseki", 3)
        print(f"✅ Restaurant created: {restaurant.name}")
        
        gift_shop = GiftShop("Premium Shop", 3)
        print(f"✅ Gift shop created: {gift_shop.name}")
        
        resort.facilities.extend([restaurant, gift_shop])
        print(f"✅ Facilities added to resort: {len(resort.facilities)} facilities")
        
        # Quality staff
        print("Adding quality staff...")
        staff_members = [
            Staff("Head Cleaner", "Cleaner", 9),
            Staff("Senior Attendant", "Attendant", 8),
            Staff("Manager", "Manager", 9)
        ]
        
        for staff in staff_members:
            print(f"✅ Staff created: {staff.name}")
        
        resort.staff_manager.staff.extend(staff_members)
        print(f"✅ Staff added to resort: {len(resort.staff_manager.staff)} staff")
        
        resort.entry_fee = 3000
        resort.reputation = 70
        print("✅ Entry fee and reputation set")
        
        print("✅ Premium resort setup complete!")
        return resort
        
    except Exception as e:
        print(f"❌ Error in premium resort setup: {e}")
        traceback.print_exc()
        return None

def main():
    print("🔍 Debug Test - Finding List Index Errors")
    print("=" * 50)
    
    # Test balanced resort
    balanced_resort = test_balanced_resort()
    
    # Test premium resort
    premium_resort = test_premium_resort()
    
    if balanced_resort:
        print(f"\n✅ Balanced resort created successfully")
        print(f"   Pools: {len(balanced_resort.pools)}")
        print(f"   Facilities: {len(balanced_resort.facilities)}")
        print(f"   Staff: {len(balanced_resort.staff_manager.staff)}")
    
    if premium_resort:
        print(f"\n✅ Premium resort created successfully")
        print(f"   Pools: {len(premium_resort.pools)}")
        print(f"   Facilities: {len(premium_resort.facilities)}")
        print(f"   Staff: {len(premium_resort.staff_manager.staff)}")

if __name__ == "__main__":
    main()
