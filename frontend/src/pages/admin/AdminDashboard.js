import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Package, ShoppingBag, Users, Tag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import axios from 'axios';
import { useAuthenticatedAPI } from '@/hooks/useAuthenticatedAPI';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = () => {
  const { idToken } = useAuthenticatedAPI();
  const [skuCount, setSkuCount] = useState('--');
  const [couponCount, setCouponCount] = useState('--');
  const [giftItemCount, setGiftItemCount] = useState('--');
  const [giftTierCount, setGiftTierCount] = useState('--');
  
  useEffect(() => {
    if (idToken) {
      fetchInventoryCount();
      fetchCouponCount();
      fetchGiftCounts();
    }
  }, [idToken]);
  
  const fetchInventoryCount = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/inventory`, {
        headers: { Authorization: `Bearer ${idToken}` }
      });
      setSkuCount(`${response.data.length} SKUs`);
    } catch (error) {
      console.error('Error fetching inventory count:', error);
      setSkuCount('0 SKUs');
    }
  };

  const fetchCouponCount = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/coupons`, {
        headers: { Authorization: `Bearer ${idToken}` }
      });
      setCouponCount(response.data.length || 0);
    } catch (error) {
      console.error('Error fetching coupon count:', error);
      setCouponCount(0);
    }
  };

  const fetchGiftCounts = async () => {
    try {
      const [itemsRes, tiersRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/admin/gift-items`, {
          headers: { Authorization: `Bearer ${idToken}` }
        }),
        axios.get(`${BACKEND_URL}/api/admin/gift-tiers`, {
          headers: { Authorization: `Bearer ${idToken}` }
        })
      ]);
      setGiftItemCount(itemsRes.data.length || 0);
      setGiftTierCount(tiersRes.data.length || 0);
    } catch (error) {
      console.error('Error fetching gift counts:', error);
      setGiftItemCount(0);
      setGiftTierCount(0);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="admin-dashboard">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Admin Dashboard</h1>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
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
            value={couponCount}
            icon={<Tag className="w-8 h-8 text-purple-700" />}
            link="/admin/coupons"
          />
          <StatCard
            title="Gift Items"
            value={giftItemCount}
            icon={<Package className="w-8 h-8 text-pink-700" />}
            link="/admin/gifts"
          />
          <StatCard
            title="Gift Tiers"
            value={giftTierCount}
            icon={<Tag className="w-8 h-8 text-orange-700" />}
            link="/admin/gifts?tab=tiers"
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
            <Link to="/admin/coupons">
              <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white">
                🎟️ Coupon Management
              </Button>
            </Link>
            <Link to="/admin/gifts">
              <Button className="w-full bg-pink-600 hover:bg-pink-700 text-white">
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
