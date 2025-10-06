import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Search, Filter, X, SlidersHorizontal } from 'lucide-react';
import axios from 'axios';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Products = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [filterOptions, setFilterOptions] = useState({
    colors: [],
    sizes: [],
    types: [],
    categories: [],
    price_range: { min: 0, max: 100 }
  });
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    categories: searchParams.get('category') ? searchParams.get('category').split(',') : [],
    colors: searchParams.get('color') ? searchParams.get('color').split(',') : [],
    sizes: searchParams.get('size') ? searchParams.get('size').split(',') : [],
    type: searchParams.get('type') || '',
    price_min: parseFloat(searchParams.get('price_min')) || null,
    price_max: parseFloat(searchParams.get('price_max')) || null,
    in_stock_only: searchParams.get('in_stock_only') === 'true'
  });
  
  const [sortBy, setSortBy] = useState(searchParams.get('sort') || 'best_sellers');
  const [pagination, setPagination] = useState({
    page: parseInt(searchParams.get('page')) || 1,
    limit: 20,
    total: 0,
    pages: 0
  });

  useEffect(() => {
    fetchFilterOptions();
  }, []);

  useEffect(() => {
    updateURL();
    fetchProducts();
  }, [filters, sortBy, pagination.page]);

  useEffect(() => {
    // Important business rule: If bubble wrap is selected, only show white color
    if (filters.type === 'bubble wrap' && !filters.colors.includes('white')) {
      setFilters(prev => ({
        ...prev,
        colors: ['white']
      }));
    }
  }, [filters.type]);

  const updateURL = () => {
    const params = {};
    
    if (filters.search) params.search = filters.search;
    if (filters.categories.length) params.category = filters.categories.join(',');
    if (filters.colors.length) params.color = filters.colors.join(',');
    if (filters.sizes.length) params.size = filters.sizes.join(',');
    if (filters.type) params.type = filters.type;
    if (filters.price_min !== null) params.price_min = filters.price_min;
    if (filters.price_max !== null) params.price_max = filters.price_max;
    if (filters.in_stock_only) params.in_stock_only = 'true';
    if (sortBy !== 'best_sellers') params.sort = sortBy;
    if (pagination.page > 1) params.page = pagination.page;
    
    setSearchParams(params);
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/products/filter-options`);
      setFilterOptions(response.data);
    } catch (error) {
      console.error('Failed to fetch filter options:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      setLoading(true);
      
      // Clean up filters (remove null/empty values)
      const cleanFilters = {};
      if (filters.search) cleanFilters.search = filters.search;
      if (filters.categories.length) cleanFilters.categories = filters.categories;
      if (filters.colors.length) cleanFilters.colors = filters.colors;
      if (filters.sizes.length) cleanFilters.sizes = filters.sizes;
      if (filters.type) cleanFilters.type = filters.type;
      if (filters.price_min !== null) cleanFilters.price_min = filters.price_min;
      if (filters.price_max !== null) cleanFilters.price_max = filters.price_max;
      if (filters.in_stock_only) cleanFilters.in_stock_only = filters.in_stock_only;

      const requestData = {
        filters: cleanFilters,
        sort: { sort_by: sortBy },
        page: pagination.page,
        limit: pagination.limit
      };

      const response = await axios.post(`${BACKEND_URL}/api/products/filter`, requestData);
      
      setProducts(response.data.products);
      setPagination(prev => ({
        ...prev,
        total: response.data.total,
        pages: response.data.pages
      }));
      
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  };

  const toggleArrayFilter = (key, value) => {
    setFilters(prev => {
      const currentArray = prev[key] || [];
      const newArray = currentArray.includes(value)
        ? currentArray.filter(item => item !== value)
        : [...currentArray, value];
      
      return { ...prev, [key]: newArray };
    });
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const clearAllFilters = () => {
    setFilters({
      search: '',
      categories: [],
      colors: [],
      sizes: [],
      type: '',
      price_min: null,
      price_max: null,
      in_stock_only: false
    });
    setSortBy('best_sellers');
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.categories.length) count += filters.categories.length;
    if (filters.colors.length) count += filters.colors.length;
    if (filters.sizes.length) count += filters.sizes.length;
    if (filters.type) count += 1;
    if (filters.price_min !== null || filters.price_max !== null) count += 1;
    if (filters.in_stock_only) count += 1;
    return count;
  };

  const availableColors = filters.type === 'bubble wrap' 
    ? filterOptions.colors.filter(color => color === 'white')
    : filterOptions.colors;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-4">Premium Polymailers & Supplies</h1>
          
          {/* Search and Sort */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search products..."
                value={filters.search}
                onChange={(e) => updateFilter('search', e.target.value)}
                className="pl-10"
              />
            </div>
            
            <div className="flex gap-2">
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="best_sellers">Best Sellers</SelectItem>
                  <SelectItem value="price_low_high">Price: Low to High</SelectItem>
                  <SelectItem value="price_high_low">Price: High to Low</SelectItem>
                  <SelectItem value="newest">Newest</SelectItem>
                </SelectContent>
              </Select>
              
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="md:hidden"
              >
                <SlidersHorizontal className="w-4 h-4 mr-2" />
                Filters {getActiveFilterCount() > 0 && `(${getActiveFilterCount()})`}
              </Button>
            </div>
          </div>
          
          {/* Active Filters */}
          {getActiveFilterCount() > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {filters.categories.map(category => (
                <Badge key={category} variant="secondary" className="cursor-pointer">
                  {category} 
                  <X 
                    className="w-3 h-3 ml-1" 
                    onClick={() => toggleArrayFilter('categories', category)}
                  />
                </Badge>
              ))}
              {filters.colors.map(color => (
                <Badge key={color} variant="secondary" className="cursor-pointer">
                  {color}
                  <X 
                    className="w-3 h-3 ml-1" 
                    onClick={() => toggleArrayFilter('colors', color)}
                  />
                </Badge>
              ))}
              {filters.sizes.map(size => (
                <Badge key={size} variant="secondary" className="cursor-pointer">
                  {size} cm
                  <X 
                    className="w-3 h-3 ml-1" 
                    onClick={() => toggleArrayFilter('sizes', size)}
                  />
                </Badge>
              ))}
              {filters.type && (
                <Badge variant="secondary" className="cursor-pointer">
                  {filters.type}
                  <X 
                    className="w-3 h-3 ml-1" 
                    onClick={() => updateFilter('type', '')}
                  />
                </Badge>
              )}
              <Button variant="ghost" size="sm" onClick={clearAllFilters}>
                Clear all
              </Button>
            </div>
          )}
        </div>

        <div className="flex gap-8">
          {/* Sidebar Filters - Desktop */}
          <div className={`w-64 ${showFilters ? 'block' : 'hidden md:block'}`}>
            <div className="bg-white rounded-lg p-6 shadow-sm space-y-6">
              <h3 className="font-semibold text-slate-900">Filters</h3>
              
              {/* Categories */}
              <div>
                <h4 className="font-medium text-slate-800 mb-3">Category</h4>
                {filterOptions.categories.map(category => (
                  <label key={category} className="flex items-center mb-2">
                    <input
                      type="checkbox"
                      checked={filters.categories.includes(category)}
                      onChange={() => toggleArrayFilter('categories', category)}
                      className="mr-2"
                    />
                    <span className="capitalize">{category}</span>
                  </label>
                ))}
              </div>
              
              {/* Type */}
              <div>
                <h4 className="font-medium text-slate-800 mb-3">Type</h4>
                <Select value={filters.type} onValueChange={(value) => updateFilter('type', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="All types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All types</SelectItem>
                    {filterOptions.types.map(type => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {filters.type === 'bubble wrap' && (
                  <p className="text-xs text-amber-600 mt-2">
                    ⚠️ Bubble wrap only available in white
                  </p>
                )}
              </div>
              
              {/* Colors */}
              <div>
                <h4 className="font-medium text-slate-800 mb-3">Colors</h4>
                {availableColors.map(color => (
                  <label key={color} className="flex items-center mb-2">
                    <input
                      type="checkbox"
                      checked={filters.colors.includes(color)}
                      onChange={() => toggleArrayFilter('colors', color)}
                      disabled={filters.type === 'bubble wrap' && color !== 'white'}
                      className="mr-2"
                    />
                    <span className="capitalize">{color}</span>
                  </label>
                ))}
              </div>
              
              {/* Sizes */}
              <div>
                <h4 className="font-medium text-slate-800 mb-3">Dimensions</h4>
                <div className="max-h-48 overflow-y-auto">
                  {filterOptions.sizes.map(size => (
                    <label key={size} className="flex items-center mb-2">
                      <input
                        type="checkbox"
                        checked={filters.sizes.includes(size)}
                        onChange={() => toggleArrayFilter('sizes', size)}
                        className="mr-2"
                      />
                      <span>{size} cm</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Availability */}
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.in_stock_only}
                    onChange={(e) => updateFilter('in_stock_only', e.target.checked)}
                    className="mr-2"
                  />
                  <span>In stock only</span>
                </label>
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="flex-1">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg p-4 shadow-sm animate-pulse">
                    <div className="bg-gray-200 h-48 rounded mb-4"></div>
                    <div className="bg-gray-200 h-4 rounded mb-2"></div>
                    <div className="bg-gray-200 h-6 rounded w-20"></div>
                  </div>
                ))}
              </div>
            ) : products.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {products.map(product => (
                    <Link
                      key={product.id}
                      to={`/products/${product.id}`}
                      className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                    >
                      <div className="aspect-square bg-gray-100 relative">
                        {product.images?.[0] ? (
                          <img
                            src={product.images[0]}
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-gradient-to-br from-teal-100 to-orange-100 flex items-center justify-center">
                            <span className="text-gray-500">No image</span>
                          </div>
                        )}
                        {product.featured && (
                          <Badge className="absolute top-2 right-2 bg-orange-500">
                            Featured
                          </Badge>
                        )}
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-slate-900 mb-2">{product.name}</h3>
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description}</p>
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-lg font-bold text-teal-700">
                              {formatPrice(product.price_range.min)}
                              {product.price_range.min !== product.price_range.max && 
                                ` - ${formatPrice(product.price_range.max)}`}
                            </span>
                          </div>
                          <Badge variant={product.in_stock ? "default" : "secondary"}>
                            {product.in_stock ? "In Stock" : "Out of Stock"}
                          </Badge>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
                
                {/* Pagination */}
                {pagination.pages > 1 && (
                  <div className="flex justify-center items-center gap-2">
                    <Button
                      variant="outline"
                      disabled={pagination.page === 1}
                      onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                    >
                      Previous
                    </Button>
                    <span className="mx-4">
                      Page {pagination.page} of {pagination.pages}
                    </span>
                    <Button
                      variant="outline"
                      disabled={pagination.page === pagination.pages}
                      onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Filter className="w-12 h-12 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
                <p className="text-gray-600 mb-4">Try adjusting your filters or search terms</p>
                <Button onClick={clearAllFilters}>Clear all filters</Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Products;