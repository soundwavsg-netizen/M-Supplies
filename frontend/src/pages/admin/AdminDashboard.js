import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Package, ShoppingBag, Users, Tag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = () => {
  const [skuCount, setSkuCount] = useState('--');
  
  useEffect(() => {
    fetchInventoryCount();
  }, []);
  
  const fetchInventoryCount = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/admin/inventory`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSkuCount(`${response.data.length} SKUs`);
    } catch (error) {
      console.error('Error fetching inventory count:', error);
      setSkuCount('0 SKUs');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="admin-dashboard">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Admin Dashboard</h1>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Inventory"
            value={skuCount}
            icon={<Package className="w-8 h-8 text-teal-700" />}
            link="/admin/inventory"
          />
          <StatCard
            title="Orders"
            value="--"
            icon={<ShoppingBag className="w-8 h-8 text-teal-700" />}
            link="/admin/orders"
          />
          <StatCard
            title="Customers"
            value="--"
            icon={<Users className="w-8 h-8 text-teal-700" />}
            link="/admin/users"
          />
          <StatCard
            title="Coupons"
            value="2"
            icon={<Tag className="w-8 h-8 text-teal-700" />}
            link="/admin/coupons"
          />
        </div>

        <div className="bg-white rounded-lg p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            <Link to="/admin/inventory">
              <Button className="w-full" variant="outline">
                Manage Inventory
              </Button>
            </Link>
            <Link to="/admin/packing">
              <Button className="w-full" variant="default">
                📦 Packing Interface
              </Button>
            </Link>
            <Link to="/admin/promotions">
              <Button className="w-full" variant="outline" className="bg-purple-600 hover:bg-purple-700 text-white">
                🎟️ Promotions
              </Button>
            </Link>
            <Link to="/admin/gifts">
              <Button className="w-full" variant="outline" className="bg-pink-600 hover:bg-pink-700 text-white">
                🎁 Gift Management
              </Button>
            </Link>
            <Link to="/admin/orders">
              <Button className="w-full" variant="outline">
                View Orders
              </Button>
            </Link>
            <Link to="/admin/users">
              <Button className="w-full" variant="outline">
                Manage Users
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, link }) => {
  return (
    <Link to={link} className="block">
      <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between mb-4">
          <div className="bg-teal-50 rounded-lg p-3">{icon}</div>
        </div>
        <h3 className="text-gray-600 text-sm mb-1">{title}</h3>
        <p className="text-3xl font-bold text-slate-900">{value}</p>
      </div>
    </Link>
  );
};

export default AdminDashboard;
