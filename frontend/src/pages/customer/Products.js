import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Search, Filter } from 'lucide-react';
import { productsAPI } from '@/lib/api';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const Products = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || null);
  const [sizeFilter, setSizeFilter] = useState(searchParams.get('size') || '');
  const [colorFilter, setColorFilter] = useState(searchParams.get('color') || '');
  const [sortBy, setSortBy] = useState(searchParams.get('sort') || 'name');
  
  // Available filter options (extracted from products)
  const [availableSizes, setAvailableSizes] = useState([]);
  const [availableColors, setAvailableColors] = useState([]);

  useEffect(() => {
    // Update URL when filters change
    const params = {};
    if (search) params.search = search;
    if (selectedCategory) params.category = selectedCategory;
    if (sizeFilter) params.size = sizeFilter;
    if (colorFilter) params.color = colorFilter;
    setSearchParams(params);
    
    fetchProducts();
  }, [selectedCategory, search, sizeFilter, colorFilter]);
  
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedCategory) params.category = selectedCategory;
      if (search) params.search = search;
      
      const response = await productsAPI.list(params);
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await productsAPI.getCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="products-page">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">Our Products</h1>
          <p className="text-xl text-gray-600">Premium polymailers for all your shipping needs</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
                data-testid="search-input"
              />
            </div>

            {/* Category Filter */}
            <div className="flex gap-2 flex-wrap">
              <Button
                variant={selectedCategory === null ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(null)}
              >
                All
              </Button>
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading products...</p>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-600 text-lg">No products found</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="products-grid">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const ProductCard = ({ product }) => {
  return (
    <Link
      to={`/products/${product.id}`}
      className="group bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300"
      data-testid={`product-card-${product.id}`}
    >
      <div className="aspect-square overflow-hidden bg-gray-100">
        <img
          src={product.images[0] || 'https://via.placeholder.com/400'}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <div className="p-6">
        <div className="flex items-center justify-between mb-2">
          <Badge variant="secondary">{product.category}</Badge>
          {product.featured && <Badge className="bg-orange-500">Featured</Badge>}
        </div>
        <h3 className="text-xl font-semibold text-slate-900 mb-2 group-hover:text-teal-700 transition-colors">
          {product.name}
        </h3>
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-2xl font-bold text-teal-700">
            {formatPrice(product.price_range.min)}
          </span>
          {product.price_range.max !== product.price_range.min && (
            <span className="text-sm text-gray-500">
              - {formatPrice(product.price_range.max)}
            </span>
          )}
        </div>
        <div className="flex items-center justify-between">
          <span className={`text-sm ${
            product.in_stock ? 'text-green-600' : 'text-red-600'
          }`}>
            {product.in_stock ? 'In Stock' : 'Out of Stock'}
          </span>
          <span className="text-teal-700 font-medium group-hover:translate-x-1 transition-transform">
            View Details →
          </span>
        </div>
      </div>
    </Link>
  );
};

export default Products;
