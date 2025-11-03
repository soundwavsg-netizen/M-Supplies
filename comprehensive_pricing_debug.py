#!/usr/bin/env python3
"""
Comprehensive Pricing Debug Test
Check all products for pricing inconsistencies and identify the actual issue
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-store.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

class ComprehensivePricingDebugger:
    def __init__(self):
        self.session = None
        self.admin_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Authenticate admin user"""
        print("🔐 Authenticating Admin...")
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.admin_token = data.get('access_token')
                    print("✅ Admin authenticated")
                else:
                    print(f"❌ Admin authentication failed: {resp.status}")
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
    
    async def get_all_products_with_pricing(self):
        """Get all products and their detailed pricing information"""
        print("\n📊 Getting All Products with Detailed Pricing...")
        
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    print(f"Found {len(products)} products")
                    
                    detailed_products = []
                    
                    for product in products:
                        product_id = product.get('id')
                        product_name = product.get('name', 'Unknown')
                        
                        # Get detailed product info
                        try:
                            async with self.session.get(f"{API_BASE}/products/{product_id}") as detail_resp:
                                if detail_resp.status == 200:
                                    detailed_product = await detail_resp.json()
                                    detailed_products.append(detailed_product)
                                    
                                    print(f"\n🔍 PRODUCT: {product_name}")
                                    variants = detailed_product.get('variants', [])
                                    
                                    for i, variant in enumerate(variants):
                                        attrs = variant.get('attributes', {})
                                        size_code = attrs.get('size_code', 'Unknown')
                                        pack_size = attrs.get('pack_size', 'Unknown')
                                        color = attrs.get('color', 'Unknown')
                                        
                                        price_tiers = variant.get('price_tiers', [])
                                        
                                        print(f"  Variant {i+1}: {size_code} - {pack_size} pcs/pack ({color})")
                                        print(f"    SKU: {variant.get('sku', 'Unknown')}")
                                        print(f"    Price Tiers: {json.dumps(price_tiers, indent=8)}")
                                        
                                        # Check for potential issues
                                        if len(price_tiers) > 1:
                                            prices = [tier.get('price', 0) for tier in price_tiers]
                                            if len(set(prices)) == 1:
                                                print(f"    ⚠️  WARNING: All price tiers have same price: ${prices[0]}")
                                        
                                        # Check for $14.99 pricing
                                        if price_tiers and price_tiers[0].get('price') == 14.99:
                                            print(f"    💰 Shows $14.99 pricing")
                                
                                else:
                                    print(f"❌ Failed to get details for {product_name}: {detail_resp.status}")
                        except Exception as e:
                            print(f"❌ Error getting details for {product_name}: {str(e)}")
                    
                    return detailed_products
                    
                else:
                    print(f"❌ Failed to get products: {resp.status}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error getting products: {str(e)}")
            return []
    
    async def check_customer_vs_admin_pricing(self, products):
        """Compare customer vs admin pricing for all products"""
        print("\n🔍 Comparing Customer vs Admin Pricing...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for product in products:
            product_id = product.get('id')
            product_name = product.get('name', 'Unknown')
            
            print(f"\n🔍 Checking {product_name}...")
            
            # Get customer view
            try:
                async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                    if resp.status == 200:
                        customer_product = await resp.json()
                        customer_variants = customer_product.get('variants', [])
                        
                        # Get admin view
                        async with self.session.get(f"{API_BASE}/products/{product_id}", headers=headers) as admin_resp:
                            if admin_resp.status == 200:
                                admin_product = await admin_resp.json()
                                admin_variants = admin_product.get('variants', [])
                                
                                # Compare pricing
                                for i, (customer_variant, admin_variant) in enumerate(zip(customer_variants, admin_variants)):
                                    customer_price_tiers = customer_variant.get('price_tiers', [])
                                    admin_price_tiers = admin_variant.get('price_tiers', [])
                                    
                                    customer_price = customer_price_tiers[0].get('price', 0) if customer_price_tiers else 0
                                    admin_price = admin_price_tiers[0].get('price', 0) if admin_price_tiers else 0
                                    
                                    if customer_price != admin_price:
                                        print(f"  ❌ PRICING MISMATCH - Variant {i+1}:")
                                        print(f"      Customer sees: ${customer_price}")
                                        print(f"      Admin sees: ${admin_price}")
                                    else:
                                        print(f"  ✅ Variant {i+1}: Both see ${customer_price}")
                            else:
                                print(f"  ❌ Failed to get admin view: {admin_resp.status}")
                    else:
                        print(f"  ❌ Failed to get customer view: {resp.status}")
                        
            except Exception as e:
                print(f"  ❌ Error comparing pricing: {str(e)}")
    
    async def find_products_with_identical_pricing(self, products):
        """Find products where multiple variants have identical pricing"""
        print("\n🔍 Finding Products with Identical Variant Pricing...")
        
        for product in products:
            product_name = product.get('name', 'Unknown')
            variants = product.get('variants', [])
            
            if len(variants) < 2:
                continue
            
            # Check if multiple variants have same pricing
            variant_prices = []
            for variant in variants:
                price_tiers = variant.get('price_tiers', [])
                if price_tiers:
                    price = price_tiers[0].get('price', 0)
                    variant_prices.append(price)
            
            if len(variant_prices) > 1:
                unique_prices = set(variant_prices)
                if len(unique_prices) == 1:
                    print(f"⚠️  {product_name}: All {len(variants)} variants have same price: ${variant_prices[0]}")
                elif 14.99 in variant_prices:
                    count_14_99 = variant_prices.count(14.99)
                    if count_14_99 > 1:
                        print(f"💰 {product_name}: {count_14_99} variants show $14.99 pricing")
    
    async def test_specific_product_by_name(self, search_name):
        """Test a specific product by searching for name"""
        print(f"\n🔍 Searching for product containing '{search_name}'...")
        
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    matching_products = []
                    for product in products:
                        product_name = product.get('name', '').lower()
                        if search_name.lower() in product_name:
                            matching_products.append(product)
                    
                    if matching_products:
                        print(f"Found {len(matching_products)} matching products:")
                        for product in matching_products:
                            await self.analyze_specific_product(product)
                    else:
                        print(f"No products found containing '{search_name}'")
                        print("Available products:")
                        for product in products:
                            print(f"  - {product.get('name', 'Unknown')}")
                    
                else:
                    print(f"❌ Failed to search products: {resp.status}")
                    
        except Exception as e:
            print(f"❌ Error searching products: {str(e)}")
    
    async def analyze_specific_product(self, product):
        """Analyze a specific product in detail"""
        product_id = product.get('id')
        product_name = product.get('name', 'Unknown')
        
        print(f"\n📊 DETAILED ANALYSIS: {product_name}")
        print("=" * 50)
        
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    detailed_product = await resp.json()
                    variants = detailed_product.get('variants', [])
                    
                    print(f"Product ID: {product_id}")
                    print(f"Total Variants: {len(variants)}")
                    
                    for i, variant in enumerate(variants):
                        attrs = variant.get('attributes', {})
                        print(f"\nVariant {i+1}:")
                        print(f"  ID: {variant.get('id')}")
                        print(f"  SKU: {variant.get('sku')}")
                        print(f"  Size: {attrs.get('size_code', 'Unknown')}")
                        print(f"  Pack Size: {attrs.get('pack_size', 'Unknown')}")
                        print(f"  Color: {attrs.get('color', 'Unknown')}")
                        print(f"  Type: {attrs.get('type', 'Unknown')}")
                        
                        price_tiers = variant.get('price_tiers', [])
                        print(f"  Price Tiers ({len(price_tiers)} tiers):")
                        for j, tier in enumerate(price_tiers):
                            print(f"    Tier {j+1}: Min Qty {tier.get('min_quantity', 0)} = ${tier.get('price', 0)}")
                        
                        # Stock info
                        print(f"  Stock - on_hand: {variant.get('on_hand', 0)}, stock_qty: {variant.get('stock_qty', 0)}")
                    
                    # Check for pricing issues
                    print(f"\n🔍 PRICING ANALYSIS:")
                    
                    # Check if any variants have identical price_tiers
                    price_tier_signatures = []
                    for variant in variants:
                        price_tiers = variant.get('price_tiers', [])
                        signature = str(price_tiers)  # Simple string comparison
                        price_tier_signatures.append(signature)
                    
                    if len(set(price_tier_signatures)) < len(variants):
                        print("⚠️  WARNING: Some variants have identical price_tiers arrays")
                        for i, sig in enumerate(price_tier_signatures):
                            print(f"    Variant {i+1}: {sig}")
                    else:
                        print("✅ All variants have unique price_tiers arrays")
                    
                    # Check for $14.99 pricing
                    variants_with_14_99 = []
                    for i, variant in enumerate(variants):
                        price_tiers = variant.get('price_tiers', [])
                        if price_tiers and price_tiers[0].get('price') == 14.99:
                            variants_with_14_99.append(i+1)
                    
                    if variants_with_14_99:
                        print(f"💰 Variants showing $14.99: {variants_with_14_99}")
                    
                else:
                    print(f"❌ Failed to get product details: {resp.status}")
                    
        except Exception as e:
            print(f"❌ Error analyzing product: {str(e)}")
    
    async def run_comprehensive_debug(self):
        """Run comprehensive pricing debug"""
        print("🔍 COMPREHENSIVE PRICING DEBUG TEST")
        print("=" * 60)
        
        # Authenticate
        await self.authenticate()
        
        # Get all products with pricing
        products = await self.get_all_products_with_pricing()
        
        # Find products with identical pricing issues
        await self.find_products_with_identical_pricing(products)
        
        # Compare customer vs admin pricing
        await self.check_customer_vs_admin_pricing(products)
        
        # Test specific products mentioned in the issue
        await self.test_specific_product_by_name("baby blue")
        await self.test_specific_product_by_name("blue")
        
        print("\n" + "=" * 60)
        print("🔍 COMPREHENSIVE DEBUG COMPLETE")
        print("=" * 60)

async def main():
    async with ComprehensivePricingDebugger() as debugger:
        await debugger.run_comprehensive_debug()

if __name__ == "__main__":
    asyncio.run(main())