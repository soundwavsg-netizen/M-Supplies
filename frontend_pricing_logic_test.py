#!/usr/bin/env python3
"""
Frontend Pricing Logic Test
Test how the frontend would interpret the Baby Blue product pricing tiers
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-shop.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class FrontendPricingLogicTester:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def simulate_frontend_pricing_logic(self, price_tiers, quantity=1):
        """Simulate how frontend would calculate price based on quantity"""
        if not price_tiers:
            return 0
        
        # Sort price tiers by min_quantity (ascending)
        sorted_tiers = sorted(price_tiers, key=lambda x: x.get('min_quantity', 0))
        
        # Find the appropriate tier for the given quantity
        applicable_tier = sorted_tiers[0]  # Default to first tier
        
        for tier in sorted_tiers:
            if quantity >= tier.get('min_quantity', 0):
                applicable_tier = tier
            else:
                break
        
        return applicable_tier.get('price', 0)
    
    def simulate_frontend_display_price(self, price_tiers):
        """Simulate how frontend would display the 'starting from' price"""
        if not price_tiers:
            return 0
        
        # Frontend typically shows the lowest price or the price for quantity 1
        # Let's check both approaches
        
        # Approach 1: Lowest price across all tiers
        all_prices = [tier.get('price', 0) for tier in price_tiers]
        lowest_price = min(all_prices) if all_prices else 0
        
        # Approach 2: Price for quantity 1
        price_for_qty_1 = self.simulate_frontend_pricing_logic(price_tiers, 1)
        
        # Approach 3: First tier price (most common)
        first_tier_price = price_tiers[0].get('price', 0) if price_tiers else 0
        
        return {
            'lowest_price': lowest_price,
            'price_for_qty_1': price_for_qty_1,
            'first_tier_price': first_tier_price
        }
    
    async def test_baby_blue_pricing_logic(self):
        """Test Baby Blue product pricing logic as frontend would see it"""
        print("🔍 FRONTEND PRICING LOGIC TEST - Baby Blue Product")
        print("=" * 60)
        
        try:
            # Get Baby Blue product
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    baby_blue_product = None
                    for product in products:
                        if 'baby blue' in product.get('name', '').lower():
                            baby_blue_product = product
                            break
                    
                    if not baby_blue_product:
                        print("❌ Baby Blue product not found")
                        return
                    
                    product_id = baby_blue_product['id']
                    
                    # Get detailed product info
                    async with self.session.get(f"{API_BASE}/products/{product_id}") as detail_resp:
                        if detail_resp.status == 200:
                            product = await detail_resp.json()
                            variants = product.get('variants', [])
                            
                            print(f"📊 Product: {product.get('name')}")
                            print(f"Total Variants: {len(variants)}")
                            
                            for i, variant in enumerate(variants):
                                attrs = variant.get('attributes', {})
                                pack_size = attrs.get('pack_size', 'Unknown')
                                price_tiers = variant.get('price_tiers', [])
                                
                                print(f"\n🔍 Variant {i+1}: {pack_size} pcs/pack")
                                print(f"Raw Price Tiers: {json.dumps(price_tiers, indent=2)}")
                                
                                # Simulate different frontend pricing approaches
                                display_prices = self.simulate_frontend_display_price(price_tiers)
                                
                                print(f"Frontend Display Options:")
                                print(f"  Lowest Price: ${display_prices['lowest_price']}")
                                print(f"  Price for Qty 1: ${display_prices['price_for_qty_1']}")
                                print(f"  First Tier Price: ${display_prices['first_tier_price']}")
                                
                                # Test different quantities
                                test_quantities = [1, 25, 50, 100]
                                print(f"Price by Quantity:")
                                for qty in test_quantities:
                                    price = self.simulate_frontend_pricing_logic(price_tiers, qty)
                                    print(f"    Qty {qty}: ${price}")
                                
                                # Identify the issue
                                if pack_size == 50:
                                    variant_50_display = display_prices
                                elif pack_size == 100:
                                    variant_100_display = display_prices
                            
                            # Compare what frontend would show for both variants
                            print(f"\n🔍 FRONTEND COMPARISON:")
                            print(f"50-pack variant would display: ${variant_50_display.get('first_tier_price', 0)}")
                            print(f"100-pack variant would display: ${variant_100_display.get('first_tier_price', 0)}")
                            
                            # Check if both would show $14.99
                            if (variant_50_display.get('first_tier_price') == 14.99 and 
                                variant_100_display.get('first_tier_price') == 14.99):
                                print("❌ ISSUE CONFIRMED: Both variants would show $14.99 in frontend")
                            elif variant_100_display.get('first_tier_price') == 14.99:
                                print("⚠️  100-pack variant shows $14.99 as first tier price")
                                print("   This could be the source of user confusion")
                            else:
                                print("✅ Variants would show different prices in frontend")
                            
                            # Analyze the 100-pack pricing structure issue
                            print(f"\n🔍 100-PACK PRICING STRUCTURE ANALYSIS:")
                            variant_100 = variants[1] if len(variants) > 1 else None
                            if variant_100:
                                price_tiers_100 = variant_100.get('price_tiers', [])
                                print(f"Price Tiers: {json.dumps(price_tiers_100, indent=2)}")
                                
                                # The issue: First tier is min_quantity=25, price=$14.99
                                # But for quantity 1-24, there's no applicable tier!
                                print(f"\n🚨 PRICING STRUCTURE ISSUE IDENTIFIED:")
                                print(f"   - First tier starts at quantity 25 with price $14.99")
                                print(f"   - For quantities 1-24, frontend might default to first tier price")
                                print(f"   - This causes both variants to show $14.99 for small quantities")
                                
                                # Test edge case quantities
                                edge_quantities = [1, 24, 25, 49, 50, 99, 100]
                                print(f"\n🧪 EDGE CASE QUANTITY TESTING:")
                                for qty in edge_quantities:
                                    price = self.simulate_frontend_pricing_logic(price_tiers_100, qty)
                                    print(f"    Qty {qty}: ${price}")
                        
                        else:
                            print(f"❌ Failed to get product details: {detail_resp.status}")
                
                else:
                    print(f"❌ Failed to get products: {resp.status}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    async def test_correct_pricing_structure(self):
        """Show what the correct pricing structure should look like"""
        print(f"\n🔧 RECOMMENDED PRICING STRUCTURE FIX:")
        print("=" * 50)
        
        print("Current 100-pack structure (PROBLEMATIC):")
        current_structure = [
            {"min_quantity": 25, "price": 14.99},
            {"min_quantity": 50, "price": 7.99},
            {"min_quantity": 100, "price": 14.99}
        ]
        print(json.dumps(current_structure, indent=2))
        
        print("\nRecommended 100-pack structure (FIXED):")
        recommended_structure = [
            {"min_quantity": 1, "price": 14.99},   # Base price for 1-49 units
            {"min_quantity": 50, "price": 7.99},   # Bulk discount for 50-99 units  
            {"min_quantity": 100, "price": 14.99}  # Different pricing for 100+ units
        ]
        print(json.dumps(recommended_structure, indent=2))
        
        print("\nAlternative structure (if $7.99 should be base price):")
        alternative_structure = [
            {"min_quantity": 1, "price": 7.99},    # Base price
            {"min_quantity": 100, "price": 14.99}  # Premium pricing for large orders
        ]
        print(json.dumps(alternative_structure, indent=2))
    
    async def run_test(self):
        """Run the complete frontend pricing logic test"""
        await self.test_baby_blue_pricing_logic()
        await self.test_correct_pricing_structure()

async def main():
    async with FrontendPricingLogicTester() as tester:
        await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())