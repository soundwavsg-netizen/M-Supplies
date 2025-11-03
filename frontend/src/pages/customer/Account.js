import React, { useState, useEffect } from 'react';
import { User, MapPin, Package, Plus, Edit, Trash2, Star } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { useFirebaseAuth } from '@/context/FirebaseAuthContext';
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
  const { userProfile, currentUser, idToken } = useFirebaseAuth();
  const [searchParams] = useSearchParams();
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
    
    // Check for onboard parameter
    if (searchParams.get('onboard') === 'address') {
      setActiveTab('addresses');
      // Auto-open add address modal after data loads
      setTimeout(() => {
        resetAddressForm();
        setIsAddressModalOpen(true);
      }, 500);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'addresses') {
      fetchAddresses();
    }
  }, [activeTab]);

  const fetchUserData = async () => {
    try {
      if (!idToken) return;
      const response = await axios.get(`${BACKEND_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${idToken}` }
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
      if (!idToken) return;
      const response = await axios.get(`${BACKEND_URL}/api/auth/me/addresses`, {
        headers: { Authorization: `Bearer ${idToken}` }
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
      if (!idToken) return;
      
      await axios.put(`${BACKEND_URL}/api/auth/me`, profileForm, {
        headers: { Authorization: `Bearer ${idToken}` }
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
      if (!idToken) return;
      
      if (editingAddress) {
        await axios.put(`${BACKEND_URL}/api/auth/me/addresses/${editingAddress.id}`, addressForm, {
          headers: { Authorization: `Bearer ${idToken}` }
        });
        toast.success('Address updated');
      } else {
        await axios.post(`${BACKEND_URL}/api/auth/me/addresses`, addressForm, {
          headers: { Authorization: `Bearer ${idToken}` }
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
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-semibold text-slate-900">Shipping Addresses</h2>
                <Dialog open={isAddressModalOpen} onOpenChange={setIsAddressModalOpen}>
                  <DialogTrigger asChild>
                    <Button 
                      onClick={resetAddressForm}
                      className="bg-teal-600 hover:bg-teal-700"
                      disabled={addresses.length >= 5}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Address
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>{editingAddress ? 'Edit' : 'Add New'} Address</DialogTitle>
                    </DialogHeader>
                    
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="fullName">Full Name *</Label>
                        <Input
                          id="fullName"
                          value={addressForm.fullName}
                          onChange={(e) => setAddressForm(prev => ({...prev, fullName: e.target.value}))}
                          placeholder="Your full name"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="phone">Phone *</Label>
                        <Input
                          id="phone"
                          value={addressForm.phone}
                          onChange={(e) => setAddressForm(prev => ({...prev, phone: e.target.value}))}
                          placeholder="+65 9123 4567"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="addressLine1">Address Line 1 *</Label>
                        <Input
                          id="addressLine1"
                          value={addressForm.addressLine1}
                          onChange={(e) => setAddressForm(prev => ({...prev, addressLine1: e.target.value}))}
                          placeholder="Street address"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="addressLine2">Address Line 2</Label>
                        <Input
                          id="addressLine2"
                          value={addressForm.addressLine2}
                          onChange={(e) => setAddressForm(prev => ({...prev, addressLine2: e.target.value}))}
                          placeholder="Apartment, suite, etc. (optional)"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="unit">Unit</Label>
                        <Input
                          id="unit"
                          value={addressForm.unit}
                          onChange={(e) => setAddressForm(prev => ({...prev, unit: e.target.value}))}
                          placeholder="Unit number (optional)"
                        />
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="postalCode">Postal Code *</Label>
                          <Input
                            id="postalCode"
                            value={addressForm.postalCode}
                            onChange={(e) => setAddressForm(prev => ({...prev, postalCode: e.target.value}))}
                            placeholder={addressForm.country === 'SG' ? '123456' : '12345'}
                            maxLength={addressForm.country === 'SG' ? 6 : 5}
                          />
                        </div>
                        
                        <div>
                          <Label htmlFor="country">Country *</Label>
                          <Select 
                            value={addressForm.country} 
                            onValueChange={(value) => setAddressForm(prev => ({
                              ...prev, 
                              country: value,
                              city: value === 'SG' ? 'Singapore' : 'Kuala Lumpur',
                              state: value === 'SG' ? 'Singapore' : 'Selangor'
                            }))}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="SG">Singapore</SelectItem>
                              <SelectItem value="MY">Malaysia</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="city">City *</Label>
                          <Input
                            id="city"
                            value={addressForm.city}
                            onChange={(e) => setAddressForm(prev => ({...prev, city: e.target.value}))}
                          />
                        </div>
                        
                        <div>
                          <Label htmlFor="state">State *</Label>
                          <Input
                            id="state"
                            value={addressForm.state}
                            onChange={(e) => setAddressForm(prev => ({...prev, state: e.target.value}))}
                          />
                        </div>
                      </div>
                      
                      <div className="flex gap-3 pt-4">
                        <Button 
                          onClick={handleCreateAddress}
                          disabled={!addressForm.fullName || !addressForm.phone || !addressForm.addressLine1 || !addressForm.postalCode}
                          className="flex-1 bg-teal-600 hover:bg-teal-700"
                        >
                          {editingAddress ? 'Update' : 'Add'} Address
                        </Button>
                        <Button 
                          variant="outline" 
                          onClick={() => setIsAddressModalOpen(false)}
                          className="flex-1"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>

              {/* Address List */}
              {addresses.length === 0 ? (
                <Card className="bg-white shadow-sm">
                  <CardContent className="text-center py-12">
                    <MapPin className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                    <h3 className="text-lg font-medium text-gray-500 mb-2">No saved address yet</h3>
                    <p className="text-gray-400 mb-6">Add one to speed up checkout.</p>
                    <Button 
                      onClick={() => {resetAddressForm(); setIsAddressModalOpen(true)}}
                      className="bg-teal-600 hover:bg-teal-700"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Your First Address
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {addresses.map((address) => (
                    <Card key={address.id} className={`bg-white shadow-sm transition-all hover:shadow-md ${address.isDefault ? 'ring-2 ring-teal-200 bg-teal-50' : ''}`}>
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start mb-3">
                          <h3 className="font-semibold text-slate-900">{address.fullName}</h3>
                          {address.isDefault && (
                            <Badge className="bg-teal-100 text-teal-700 border-teal-200">
                              <Star className="w-3 h-3 mr-1" />
                              Default
                            </Badge>
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-600 space-y-1">
                          <p className="font-medium">{address.addressLine1}</p>
                          {address.addressLine2 && <p>{address.addressLine2}</p>}
                          {address.unit && <p>Unit: {address.unit}</p>}
                          <p>{address.city}, {address.state} {address.postalCode}</p>
                          <p className="font-medium">{address.country === 'SG' ? 'Singapore' : 'Malaysia'}</p>
                          <p className="text-gray-500">{address.phone}</p>
                        </div>
                        
                        <div className="flex gap-1 mt-4">
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => openEditAddressModal(address)}
                            className="flex-1 text-xs"
                          >
                            <Edit className="w-3 h-3 mr-1" />
                            Edit
                          </Button>
                          
                          {!address.isDefault && (
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => handleSetDefaultAddress(address.id)}
                              className="flex-1 text-xs"
                            >
                              <Star className="w-3 h-3 mr-1" />
                              Set Default
                            </Button>
                          )}
                          
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => handleDeleteAddress(address.id)}
                            className="text-red-600 hover:text-red-700 text-xs"
                            disabled={addresses.length === 1}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
              
              {addresses.length >= 5 && (
                <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                  <p className="text-sm text-amber-700">
                    📌 You've reached the maximum of 5 saved addresses. Delete one to add a new address.
                  </p>
                </div>
              )}
            </div>
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
