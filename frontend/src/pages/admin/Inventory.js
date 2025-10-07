import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Package, AlertTriangle, TrendingUp, Edit, Plus, ShoppingBag } from 'lucide-react';
import StockAdjustmentModal from '@/components/admin/StockAdjustmentModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Inventory = () => {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedVariant, setSelectedVariant] = useState(null);

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/admin/inventory`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInventory(response.data);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredInventory = inventory.filter(item =>
    item.sku.toLowerCase().includes(search.toLowerCase()) ||
    item.product_name.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="admin-inventory-page">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Centralized Inventory</h1>
          <p className="text-gray-600">Multi-channel stock management</p>
        </div>

        {/* Summary Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <Package className="w-8 h-8 text-teal-700" />
            </div>
            <p className="text-gray-600 text-sm">Total SKUs</p>
            <p className="text-3xl font-bold text-slate-900">{inventory.length}</p>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-gray-600 text-sm">Total On Hand</p>
            <p className="text-3xl font-bold text-slate-900">
              {inventory.reduce((sum, item) => sum + item.on_hand, 0)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-8 h-8 text-orange-600" />
            </div>
            <p className="text-gray-600 text-sm">Allocated</p>
            <p className="text-3xl font-bold text-slate-900">
              {inventory.reduce((sum, item) => sum + item.allocated, 0)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <p className="text-gray-600 text-sm">Low Stock Items</p>
            <p className="text-3xl font-bold text-slate-900">
              {inventory.filter(item => item.is_low_stock).length}
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900 mb-1">Inventory Management</h2>
              <p className="text-sm text-gray-600">Add new products or search existing inventory</p>
            </div>
            <div className="flex gap-3">
              <Link to="/admin/packing">
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Package className="w-4 h-4 mr-2" />
                  📦 Packing Interface
                </Button>
              </Link>
              <Link to="/admin/promotions">
                <Button className="bg-purple-600 hover:bg-purple-700">
                  <Package className="w-4 h-4 mr-2" />
                  🎟️ Promotions
                </Button>
              </Link>
              <Link to="/admin/products/new">
                <Button className="bg-teal-700 hover:bg-teal-800">
                  <Plus className="w-4 h-4 mr-2" />
                  Add New Product
                </Button>
              </Link>
              <Link to="/admin/products">
                <Button variant="outline" className="border-teal-200 text-teal-700 hover:bg-teal-50">
                  <ShoppingBag className="w-4 h-4 mr-2" />
                  Manage Products
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
          <Input
            placeholder="Search by SKU or product name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            data-testid="inventory-search"
          />
        </div>

        {/* Inventory Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    SKU
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    On Hand
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Allocated
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Available
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Safety Stock
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredInventory.map((item) => (
                  <tr key={item.variant_id} className="hover:bg-gray-50" data-testid={`inventory-row-${item.sku}`}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.sku}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {item.product_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                      {item.on_hand}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                      {item.allocated}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-semibold text-teal-700">
                      {item.available}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-600">
                      {item.safety_stock}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {item.is_low_stock ? (
                        <Badge variant="destructive" className="bg-red-100 text-red-800">
                          Low Stock
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          In Stock
                        </Badge>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedVariant(item)}
                        data-testid={`adjust-stock-${item.sku}`}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {filteredInventory.length === 0 && (
          <div className="bg-white rounded-lg p-12 text-center">
            <p className="text-gray-600">No inventory items found</p>
          </div>
        )}
      </div>

      {selectedVariant && (
        <StockAdjustmentModal
          variant={selectedVariant}
          onClose={() => setSelectedVariant(null)}
          onSuccess={() => {
            setSelectedVariant(null);
            fetchInventory();
          }}
        />
      )}
    </div>
  );
};

export default Inventory;
