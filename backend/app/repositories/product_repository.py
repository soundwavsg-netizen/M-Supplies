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
    
    async def delete_product(self, product_id: str) -> bool:
        # Soft delete - just mark as inactive
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
        """Advanced product filtering with aggregation pipeline"""
        
        # Build aggregation pipeline
        pipeline = []
        
        # Match products
        match_stage = {'is_active': True}
        if filters:
            if filters.categories:
                match_stage['category'] = {'$in': filters.categories}
            if filters.search:
                match_stage['$or'] = [
                    {'name': {'$regex': filters.search, '$options': 'i'}},
                    {'description': {'$regex': filters.search, '$options': 'i'}},
                    {'seo_keywords': {'$in': [filters.search]}}
                ]
        
        pipeline.append({'$match': match_stage})
        
        # Join with variants
        pipeline.append({
            '$lookup': {
                'from': 'variants',
                'localField': 'id',
                'foreignField': 'product_id',
                'as': 'variants'
            }
        })
        
        # Filter variants based on criteria
        variant_filters = []
        if filters:
            if filters.colors:
                variant_filters.append({'variants.attributes.color': {'$in': filters.colors}})
            if filters.sizes:
                variant_filters.append({'variants.attributes.size_code': {'$in': filters.sizes}})
            if filters.type:
                variant_filters.append({'variants.attributes.type': filters.type})
            if filters.price_min is not None or filters.price_max is not None:
                price_filter = {}
                if filters.price_min is not None:
                    price_filter['$gte'] = filters.price_min
                if filters.price_max is not None:
                    price_filter['$lte'] = filters.price_max
                variant_filters.append({'variants.price_tiers.0.price': price_filter})
            if filters.in_stock_only:
                variant_filters.append({'variants.on_hand': {'$gt': 0}})
        
        # Apply variant filters
        if variant_filters:
            pipeline.append({'$match': {'$and': variant_filters}})
        
        # Add computed fields
        pipeline.append({
            '$addFields': {
                'price_range': {
                    '$let': {
                        'vars': {
                            'prices': {
                                '$map': {
                                    'input': '$variants',
                                    'as': 'variant',
                                    'in': {
                                        '$arrayElemAt': [
                                            '$$variant.price_tiers.price', 
                                            0
                                        ]
                                    }
                                }
                            }
                        },
                        'in': {
                            'min': {'$min': '$$prices'},
                            'max': {'$max': '$$prices'}
                        }
                    }
                },
                'in_stock': {
                    '$anyElementTrue': {
                        '$map': {
                            'input': '$variants',
                            'as': 'variant',
                            'in': {'$gt': ['$$variant.on_hand', 0]}
                        }
                    }
                },
                'best_seller_score': {'$rand': {}}  # Mock best seller score
            }
        })
        
        # Sort
        sort_stage = {}
        if sort_options:
            if sort_options.sort_by == 'price_low_high':
                sort_stage = {'price_range.min': 1}
            elif sort_options.sort_by == 'price_high_low':
                sort_stage = {'price_range.max': -1}
            elif sort_options.sort_by == 'newest':
                sort_stage = {'created_at': -1}
            else:  # best_sellers (default)
                sort_stage = {'best_seller_score': -1, 'featured': -1}
        else:
            sort_stage = {'featured': -1, 'created_at': -1}
        
        pipeline.append({'$sort': sort_stage})
        
        # Count total (before pagination)
        count_pipeline = pipeline + [{'$count': 'total'}]
        count_result = await self.products.aggregate(count_pipeline).to_list(length=1)
        total = count_result[0]['total'] if count_result else 0
        
        # Add pagination
        pipeline.extend([
            {'$skip': skip},
            {'$limit': limit}
        ])
        
        # Project final fields
        pipeline.append({
            '$project': {
                '_id': 0,  # Exclude MongoDB ObjectId
                'id': 1,
                'name': 1,
                'description': 1,
                'category': 1,
                'images': 1,
                'price_range': 1,
                'in_stock': 1,
                'featured': 1,
                'variants': {
                    '$map': {
                        'input': '$variants',
                        'as': 'variant',
                        'in': {
                            'id': '$$variant.id',
                            'sku': '$$variant.sku',
                            'attributes': '$$variant.attributes',
                            'price': {
                                '$getField': {
                                    'field': 'price',
                                    'input': {'$arrayElemAt': ['$$variant.price_tiers', 0]}
                                }
                            },
                            'on_hand': '$$variant.on_hand',
                            'available': {'$subtract': ['$$variant.on_hand', '$$variant.allocated']}
                        }
                    }
                }
            }
        })
        
        # Execute pipeline
        products = await self.products.aggregate(pipeline).to_list(length=limit)
        
        return {
            'products': products,
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
        
        # Get all categories
        categories = await self.products.distinct('category')
        
        # Get price range
        price_pipeline = [
            {'$group': {
                '_id': None,
                'min_price': {'$min': {'$arrayElemAt': ['$price_tiers.price', 0]}},
                'max_price': {'$max': {'$arrayElemAt': ['$price_tiers.price', 0]}}
            }}
        ]
        price_result = await self.variants.aggregate(price_pipeline).to_list(length=1)
        price_range = price_result[0] if price_result else {'min_price': 0, 'max_price': 100}
        
        return {
            'colors': sorted(colors),
            'sizes': sorted(sizes, key=lambda x: tuple(map(int, x.split('x')))),  # Sort by dimensions
            'types': sorted(types),
            'categories': sorted(categories),
            'price_range': {
                'min': price_range.get('min_price', 0),
                'max': price_range.get('max_price', 100)
            }
        }
