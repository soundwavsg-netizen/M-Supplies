import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Plus, Edit, Trash2, Package } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/products`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.category.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="admin-products-page">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Products</h1>
            <p className="text-gray-600">Manage your product catalog</p>
          </div>
          <Link to="/admin/products/new">
            <Button className="bg-teal-700 hover:bg-teal-800" data-testid="add-product-button">
              <Plus className="w-4 h-4 mr-2" />
              Add Product
            </Button>
          </Link>
        </div>

        {/* Search */}
        <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
          <Input
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            data-testid="product-search"
          />
        </div>

        {/* Products Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow" data-testid={`product-card-${product.id}`}>
              <div className="aspect-video bg-gray-100 overflow-hidden">
                <img
                  src={product.images[0] || 'https://via.placeholder.com/400x300?text=No+Image'}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="secondary">{product.category}</Badge>
                  {product.featured && <Badge className="bg-orange-500">Featured</Badge>}
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{product.name}</h3>
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-xl font-bold text-teal-700">
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
                  <div className="flex gap-2">
                    <Link to={`/admin/products/${product.id}/edit`}>
                      <Button size="sm" variant="outline" className="text-blue-600 hover:text-blue-700 border-blue-200 hover:border-blue-300">
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredProducts.length === 0 && (
          <div className="bg-white rounded-lg p-12 text-center">
            <Package className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-600 mb-4">No products found</p>
            <Link to="/admin/products/new">
              <Button>Add Your First Product</Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Products;
