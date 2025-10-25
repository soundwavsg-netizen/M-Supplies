import React, { useState, useEffect } from 'react';
import { User, MapPin, Package, Plus, Edit, Trash2, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { formatPrice } from '@/lib/utils';
import SmartChatWidget from '@/components/chat/SmartChatWidget';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Account = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [addresses, setAddresses] = useState([]);
  
  // Profile form
  const [profileForm, setProfileForm] = useState({
    displayName: '',
    phone: ''
  });

  useEffect(() => {
    fetchUserData();
  }, []);

  useEffect(() => {
    if (activeTab === 'addresses') {
      fetchAddresses();
    }
  }, [activeTab]);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const userData = response.data;
      setUser(userData);
      setProfileForm({
        displayName: userData.displayName || `${userData.first_name || ''} ${userData.last_name || ''}`.trim(),
        phone: userData.phone || ''
      });
    } catch (error) {
      toast.error('Failed to load profile');
      console.error('Error fetching user data:', error);
    }
  };

  const fetchAddresses = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/users/me/addresses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAddresses(response.data);
    } catch (error) {
      console.error('Error fetching addresses:', error);
      setAddresses([]); // Set empty array on error
    }
  };

  const handleProfileUpdate = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      await axios.put(`${BACKEND_URL}/api/users/me`, profileForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Profile updated successfully.');
      await fetchUserData();
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ id, icon: Icon, label, isActive, onClick }) => (
    <Button
      variant={isActive ? 'default' : 'ghost'}
      onClick={onClick}
      className={`flex items-center gap-2 ${isActive ? 'bg-teal-600 text-white' : 'text-gray-600 hover:text-gray-900'}`}
    >
      <Icon className="w-4 h-4" />
      {label}
    </Button>
  );

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="account-page">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">My Account</h1>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Profile */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center space-x-3 mb-4">
              <User className="w-8 h-8 text-teal-700" />
              <h2 className="text-xl font-semibold text-slate-900">Profile</h2>
            </div>
            <div className="space-y-2 mb-4">
              <p className="text-sm text-gray-600">Name</p>
              <p className="font-medium text-slate-900">{user?.first_name} {user?.last_name}</p>
              
              <p className="text-sm text-gray-600 mt-3">Email</p>
              <p className="font-medium text-slate-900">{user?.email}</p>
              
              {user?.phone && (
                <>
                  <p className="text-sm text-gray-600 mt-3">Phone</p>
                  <p className="font-medium text-slate-900">{user?.phone}</p>
                </>
              )}
            </div>
            <Button variant="outline" className="w-full" disabled>
              Edit Profile (Coming Soon)
            </Button>
          </div>

          {/* Orders */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center space-x-3 mb-4">
              <Package className="w-8 h-8 text-teal-700" />
              <h2 className="text-xl font-semibold text-slate-900">Orders</h2>
            </div>
            <p className="text-gray-600 mb-4">View and track all your orders</p>
            <Link to="/orders">
              <Button className="w-full bg-teal-700 hover:bg-teal-800">View Orders</Button>
            </Link>
          </div>

          {/* Settings */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center space-x-3 mb-4">
              <Settings className="w-8 h-8 text-teal-700" />
              <h2 className="text-xl font-semibold text-slate-900">Settings</h2>
            </div>
            <p className="text-gray-600 mb-4">Manage your account settings</p>
            <Button variant="outline" className="w-full" disabled>
              Settings (Coming Soon)
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Account;
