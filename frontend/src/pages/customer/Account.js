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

  // Address form
  const [addressForm, setAddressForm] = useState({
    fullName: '',
    phone: '',
    addressLine1: '',
    addressLine2: '',
    unit: '',
    postalCode: '',
    city: 'Singapore',
    state: 'Singapore',
    country: 'SG'
  });

  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);

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

  const handleCreateAddress = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (editingAddress) {
        await axios.put(`${BACKEND_URL}/api/users/me/addresses/${editingAddress.id}`, addressForm, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Address updated');
      } else {
        await axios.post(`${BACKEND_URL}/api/users/me/addresses`, addressForm, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Address saved');
      }
      
      resetAddressForm();
      setIsAddressModalOpen(false);
      await fetchAddresses();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save address');
    }
  };

  const handleDeleteAddress = async (addressId) => {
    if (!window.confirm('Are you sure you want to delete this address?')) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`${BACKEND_URL}/api/users/me/addresses/${addressId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Address removed');
      await fetchAddresses();
    } catch (error) {
      toast.error('Failed to delete address');
    }
  };

  const handleSetDefaultAddress = async (addressId) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${BACKEND_URL}/api/users/me/addresses/${addressId}/set-default`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Default updated');
      await fetchAddresses();
    } catch (error) {
      toast.error('Failed to set default address');
    }
  };

  const resetAddressForm = () => {
    setAddressForm({
      fullName: '',
      phone: '',
      addressLine1: '',
      addressLine2: '',
      unit: '',
      postalCode: '',
      city: 'Singapore',
      state: 'Singapore',
      country: 'SG'
    });
    setEditingAddress(null);
  };

  const openEditAddressModal = (address) => {
    setAddressForm({
      fullName: address.fullName,
      phone: address.phone,
      addressLine1: address.addressLine1,
      addressLine2: address.addressLine2 || '',
      unit: address.unit || '',
      postalCode: address.postalCode,
      city: address.city,
      state: address.state,
      country: address.country
    });
    setEditingAddress(address);
    setIsAddressModalOpen(true);
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
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-slate-900 mb-8">My Account</h1>
          
          {/* Tab Navigation */}
          <div className="flex space-x-1 mb-8 bg-white p-1 rounded-lg shadow-sm w-fit">
            <TabButton
              id="profile"
              icon={User}
              label="Profile"
              isActive={activeTab === 'profile'}
              onClick={() => setActiveTab('profile')}
            />
            <TabButton
              id="addresses"
              icon={MapPin}
              label="Addresses"
              isActive={activeTab === 'addresses'}
              onClick={() => setActiveTab('addresses')}
            />
            <TabButton
              id="orders"
              icon={Package}
              label="Orders"
              isActive={activeTab === 'orders'}
              onClick={() => setActiveTab('orders')}
            />
          </div>

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <Card className="bg-white shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5 text-teal-600" />
                  Profile Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="displayName">Display Name *</Label>
                    <Input
                      id="displayName"
                      value={profileForm.displayName}
                      onChange={(e) => setProfileForm(prev => ({...prev, displayName: e.target.value}))}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      value={user.email}
                      disabled
                      className="bg-gray-50"
                    />
                    <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                  </div>
                  
                  <div>
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      value={profileForm.phone}
                      onChange={(e) => setProfileForm(prev => ({...prev, phone: e.target.value}))}
                      placeholder="+65 9123 4567"
                    />
                  </div>
                  
                  <div className="flex items-end">
                    <Button 
                      onClick={handleProfileUpdate}
                      disabled={loading || !profileForm.displayName}
                      className="bg-teal-600 hover:bg-teal-700"
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Addresses Tab */}
          {activeTab === 'addresses' && (
            <Card className="bg-white shadow-sm">
              <CardContent className="text-center py-12">
                <MapPin className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-500 mb-2">Address Management</h3>
                <p className="text-gray-400">Address management coming soon</p>
              </CardContent>
            </Card>
          )}

          {/* Orders Tab */}
          {activeTab === 'orders' && (
            <Card className="bg-white shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package className="w-5 h-5 text-teal-600" />
                  Order History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Package className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-500 mb-2">No orders yet</h3>
                  <p className="text-gray-400">Your order history will appear here</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
      
      <SmartChatWidget />
    </div>
  );
};

export default Account;
