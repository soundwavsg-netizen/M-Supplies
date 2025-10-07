from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from app.schemas.product import ProductFilters, ProductSortOptions

class ProductRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.products = db.products
        self.variants = db.variants
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        product_id = str(uuid.uuid4())
        product_data['id'] = product_id
        product_data['created_at'] = datetime.now(timezone.utc)
        product_data['updated_at'] = datetime.now(timezone.utc)
        
        await self.products.insert_one(product_data)
        return product_data
    
    async def create_variant(self, variant_data: Dict[str, Any]) -> Dict[str, Any]:
        variant_data['id'] = str(uuid.uuid4())
        variant_data['created_at'] = datetime.now(timezone.utc)
        
        await self.variants.insert_one(variant_data)
        return variant_data
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return await self.products.find_one({'id': product_id})
    
    async def get_variant_by_id(self, variant_id: str) -> Optional[Dict[str, Any]]:
        return await self.variants.find_one({'id': variant_id})
    
    async def get_variants_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        cursor = self.variants.find({'product_id': product_id})
        return await cursor.to_list(length=100)
    
    async def list_products(self, skip: int = 0, limit: int = 50, category: Optional[str] = None, 
                           search: Optional[str] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        query = {}
        if category:
            query['category'] = category
        if is_active is not None:
            query['is_active'] = is_active
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        cursor = self.products.find(query).skip(skip).limit(limit).sort('created_at', -1)
        return await cursor.to_list(length=limit)
    
    async def update_product(self, product_id: str, update_data: Dict[str, Any]) -> bool:
        update_data['updated_at'] = datetime.now(timezone.utc)
        result = await self.products.update_one(
            {'id': product_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def update_variant(self, variant_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.variants.update_one(
            {'id': variant_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def delete_variants_by_product(self, product_id: str) -> bool:
        """Delete all variants for a specific product"""
        result = await self.variants.delete_many({'product_id': product_id})
        return result.deleted_count > 0
    
    async def delete_product(self, product_id: str) -> bool:
        # Soft delete - mark product as inactive AND delete its variants
        # First delete all variants for this product
        await self.delete_variants_by_product(product_id)
        
        # Then mark product as inactive
        result = await self.products.update_one(
            {'id': product_id},
            {'$set': {'is_active': False, 'updated_at': datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def get_categories(self) -> List[str]:
        categories = await self.products.distinct('category')
        return categories
    
    async def list_products_filtered(self, filters: Optional[ProductFilters] = None,
                                   sort_options: Optional[ProductSortOptions] = None,
                                   skip: int = 0, limit: int = 50) -> Dict[str, Any]:
        """Advanced product filtering - simplified approach"""
        
        # First, get all products with variants
        products_with_variants = []
        
        # Build product query
        product_query = {'is_active': True}
        if filters and filters.categories:
            product_query['category'] = {'$in': filters.categories}
        if filters and filters.search:
            product_query['$or'] = [
                {'name': {'$regex': filters.search, '$options': 'i'}},
                {'description': {'$regex': filters.search, '$options': 'i'}}
            ]
        
        # Get products
        products = await self.products.find(product_query).to_list(length=None)
        
        for product in products:
            # Get variants for this product
            variant_query = {'product_id': product['id']}
            
            # Apply variant filters
            if filters:
                if filters.colors:
                    variant_query['attributes.color'] = {'$in': filters.colors}
                if filters.sizes:
                    variant_query['attributes.size_code'] = {'$in': filters.sizes}
                if filters.type:
                    variant_query['attributes.type'] = filters.type
                if filters.in_stock_only:
                    variant_query['on_hand'] = {'$gt': 0}
            
            variants = await self.variants.find(variant_query).to_list(length=None)
            
            # Apply price filter if specified
            if filters and (filters.price_min is not None or filters.price_max is not None):
                filtered_variants = []
                for variant in variants:
                    price = variant['price_tiers'][0]['price']
                    if filters.price_min is not None and price < filters.price_min:
                        continue
                    if filters.price_max is not None and price > filters.price_max:
                        continue
                    filtered_variants.append(variant)
                variants = filtered_variants
            
            # Skip products with no matching variants
            if not variants:
                continue
            
            # Calculate price range and stock status
            prices = [v['price_tiers'][0]['price'] for v in variants]
            in_stock = any(v['on_hand'] > 0 for v in variants)
            
            # Transform variant data
            variant_data = []
            for v in variants:
                variant_data.append({
                    'id': v['id'],
                    'sku': v['sku'],
                    'attributes': v['attributes'],
                    'price': v['price_tiers'][0]['price'],
                    'on_hand': v['on_hand'],
                    'available': v['on_hand'] - v.get('allocated', 0)
                })
            
            # Build product result
            product_result = {
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'category': product['category'],
                'images': product.get('images', []),
                'price_range': {
                    'min': min(prices) if prices else 0,
                    'max': max(prices) if prices else 0
                },
                'in_stock': in_stock,
                'featured': product.get('featured', False),
                'variants': variant_data,
                'best_seller_score': hash(product['id']) % 1000  # Mock score for sorting
            }
            
            products_with_variants.append(product_result)
        
        # Sort products
        if sort_options:
            if sort_options.sort_by == 'price_low_high':
                products_with_variants.sort(key=lambda p: p['price_range']['min'])
            elif sort_options.sort_by == 'price_high_low':
                products_with_variants.sort(key=lambda p: p['price_range']['max'], reverse=True)
            elif sort_options.sort_by == 'newest':
                products_with_variants.sort(key=lambda p: p['id'], reverse=True)  # Use ID as proxy for newest
            else:  # best_sellers (default)
                products_with_variants.sort(key=lambda p: (p['featured'], p['best_seller_score']), reverse=True)
        else:
            products_with_variants.sort(key=lambda p: (p['featured'], p['id']), reverse=True)
        
        # Pagination
        total = len(products_with_variants)
        paginated_products = products_with_variants[skip:skip + limit]
        
        return {
            'products': paginated_products,
            'total': total
        }
    
    async def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options from existing variants"""
        
        # Get all unique colors
        colors = await self.variants.distinct('attributes.color')
        
        # Get all unique sizes
        sizes = await self.variants.distinct('attributes.size_code')
        
        # Get all unique types
        types = await self.variants.distinct('attributes.type')
        
        # Get all categories (only from active products)
        categories = await self.products.distinct('category', {'is_active': True})
        
        # Get price range (exclude 0 values)
        price_pipeline = [
            {'$unwind': '$price_tiers'},
            {'$match': {'price_tiers.price': {'$gt': 0}}},  # Exclude 0 values
            {'$group': {
                '_id': None,
                'min_price': {'$min': '$price_tiers.price'},
                'max_price': {'$max': '$price_tiers.price'}
            }}
        ]
        price_result = await self.variants.aggregate(price_pipeline).to_list(length=1)
        price_range = price_result[0] if price_result else {'min_price': 0, 'max_price': 100}
        
        # Safe size sorting - handle different formats
        def safe_size_sort(size_str):
            try:
                if 'x' in size_str:
                    return tuple(map(int, size_str.split('x')))
                else:
                    # For non-standard formats, just use string sorting
                    return (0, 0)
            except:
                return (0, 0)
        
        return {
            'colors': sorted(colors),
            'sizes': sorted(sizes, key=safe_size_sort),
            'types': sorted(types),
            'categories': sorted(categories),
            'price_range': {
                'min': price_range.get('min_price', 0),
                'max': price_range.get('max_price', 100)
            }
        }
