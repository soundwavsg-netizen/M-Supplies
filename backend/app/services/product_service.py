from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilters, ProductSortOptions
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
import re

class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
    
    def _transform_variant_attributes(self, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Transform old variant attributes format to new schema format"""
        attributes = variant.get('attributes', {})
        
        # If already in new format, return as is
        if 'width_cm' in attributes and 'height_cm' in attributes and 'pack_size' in attributes:
            return variant
        
        # Transform old format to new format
        new_attributes = {}
        
        # Extract dimensions from size string like "25cm x 35cm"
        size_str = attributes.get('size', '')
        size_match = re.match(r'(\d+)cm\s*x\s*(\d+)cm', size_str)
        if size_match:
            width = int(size_match.group(1))
            height = int(size_match.group(2))
            new_attributes['width_cm'] = width
            new_attributes['height_cm'] = height
            new_attributes['size_code'] = f"{width}x{height}"
        else:
            # Fallback values if parsing fails
            new_attributes['width_cm'] = 25
            new_attributes['height_cm'] = 35
            new_attributes['size_code'] = "25x35"
        
        # Set type based on thickness or default to normal
        thickness = attributes.get('thickness', '')
        if 'bubble' in thickness.lower() or thickness == '100 micron':
            new_attributes['type'] = 'bubble wrap'
        else:
            new_attributes['type'] = 'normal'
        
        # Normalize color
        color = attributes.get('color', 'white').lower()
        color_mapping = {
            'white': 'white',
            'pastel pink': 'pastel pink',
            'champagne pink': 'champagne pink',
            'milk tea': 'milktea',
            'milktea': 'milktea',
            'black': 'black',
            'clear': 'clear',
            'blue': 'blue'
        }
        new_attributes['color'] = color_mapping.get(color, 'white')
        
        # Add pack_size - required field in new schema
        # Default to 50 if not present in old data
        new_attributes['pack_size'] = attributes.get('pack_size', 50)
        
        # Keep optional fields
        if 'thickness' in attributes:
            new_attributes['thickness'] = attributes['thickness']
        
        # Update the variant with new attributes
        variant_copy = variant.copy()
        variant_copy['attributes'] = new_attributes
        return variant_copy
    
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
        
        # Get variants and transform attributes
        variants = await self.product_repo.get_variants_by_product(product_id)
        transformed_variants = [self._transform_variant_attributes(variant) for variant in variants]
        product['variants'] = transformed_variants
        
        return product
    
    async def list_products_filtered(self, filters: Optional[ProductFilters] = None, 
                                   sort: Optional[ProductSortOptions] = None,
                                   skip: int = 0, limit: int = 50) -> Dict[str, Any]:
        """Get products with advanced filtering and sorting"""
        products_data = await self.product_repo.list_products_filtered(filters, sort, skip, limit)
        
        # Transform variant attributes in the products
        transformed_products = []
        for product in products_data['products']:
            product_copy = product.copy()
            if 'variants' in product_copy:
                transformed_variants = [self._transform_variant_attributes(variant) for variant in product_copy['variants']]
                product_copy['variants'] = transformed_variants
            transformed_products.append(product_copy)
        
        # Get filter options for frontend
        filter_options = await self.get_filter_options()
        
        return {
            'products': transformed_products,
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
                
                in_stock = any(v.get('stock_qty', 0) > 0 or v.get('on_hand', 0) > 0 for v in variants)
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
