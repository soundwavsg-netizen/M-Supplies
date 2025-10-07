from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilters, ProductSortOptions
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
import re

class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
    
    async def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        # Extract variants
        variants_data = product_data.model_dump().pop('variants', [])
        
        # Create product
        product_dict = product_data.model_dump(exclude={'variants'})
        product = await self.product_repo.create_product(product_dict)
        
        # Create variants
        variants = []
        for variant_data in variants_data:
            variant_data['product_id'] = product['id']
            variant = await self.product_repo.create_variant(variant_data)
            variants.append(variant)
        
        product['variants'] = variants
        return product
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        product = await self.product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Get variants
        variants = await self.product_repo.get_variants_by_product(product_id)
        product['variants'] = variants
        
        return product
    
    async def list_products_filtered(self, filters: Optional[ProductFilters] = None, 
                                   sort: Optional[ProductSortOptions] = None,
                                   skip: int = 0, limit: int = 50) -> Dict[str, Any]:
        """Get products with advanced filtering and sorting"""
        products_data = await self.product_repo.list_products_filtered(filters, sort, skip, limit)
        
        # Get filter options for frontend
        filter_options = await self.get_filter_options()
        
        return {
            'products': products_data['products'],
            'total': products_data['total'],
            'page': (skip // limit) + 1,
            'pages': (products_data['total'] + limit - 1) // limit,
            'filter_options': filter_options
        }
    
    async def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options from existing products"""
        return await self.product_repo.get_filter_options()
    
    async def list_products(self, skip: int = 0, limit: int = 50, category: Optional[str] = None,
                           search: Optional[str] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        products = await self.product_repo.list_products(skip, limit, category, search, is_active)
        
        # For each product, get variants and calculate price range
        result = []
        for product in products:
            variants = await self.product_repo.get_variants_by_product(product['id'])
            
            # Calculate price range
            if variants:
                all_prices = []
                for variant in variants:
                    for tier in variant.get('price_tiers', []):
                        all_prices.append(tier['price'])
                
                price_range = {
                    'min': min(all_prices) if all_prices else 0,
                    'max': max(all_prices) if all_prices else 0
                }
                
                in_stock = any(v.get('stock_qty', 0) > 0 for v in variants)
            else:
                price_range = {'min': 0, 'max': 0}
                in_stock = False
            
            result.append({
                'id': product['id'],
                'name': product['name'],
                'category': product['category'],
                'images': product.get('images', []),
                'price_range': price_range,
                'in_stock': in_stock,
                'featured': product.get('featured', False)
            })
        
        return result
    
    async def update_product(self, product_id: str, update_data: ProductUpdate) -> Dict[str, Any]:
        # Check if product exists
        product = await self.product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Extract variants from update data
        update_dict = update_data.model_dump(exclude_unset=True)
        variants_data = update_dict.pop('variants', None)
        
        # Update product fields (excluding variants)
        if update_dict:
            await self.product_repo.update_product(product_id, update_dict)
        
        # Handle variants update if provided
        if variants_data is not None:
            # Delete existing variants for this product
            await self.product_repo.delete_variants_by_product(product_id)
            
            # Create new variants
            for variant_data in variants_data:
                variant_data['product_id'] = product_id
                await self.product_repo.create_variant(variant_data)
        
        # Return updated product
        return await self.get_product(product_id)
    
    async def delete_product(self, product_id: str) -> bool:
        return await self.product_repo.delete_product(product_id)
    
    async def get_categories(self) -> List[str]:
        return await self.product_repo.get_categories()
