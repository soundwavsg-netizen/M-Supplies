import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '@/context/CartContext';
import { useAuth } from '@/context/AuthContext';
import { ordersAPI } from '@/lib/api';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Star, Plus } from 'lucide-react';
import axios from 'axios';
import CouponSection from '@/components/ui/CouponSection';
import GiftSelection from '@/components/ui/GiftSelection';
import GiftPromotion from '@/components/ui/GiftPromotion';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Checkout = () => {
  const { cart, appliedCoupon, discountAmount, availableGifts, nearbyGiftTiers, selectedGifts, selectGifts, finalTotal } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [userAddresses, setUserAddresses] = useState([]);
  const [selectedAddressId, setSelectedAddressId] = useState('');
  const [saveToProfile, setSaveToProfile] = useState(false);
  const [showAddressModal, setShowAddressModal] = useState(false);
  
  // Updated form data with Firebase-compatible field names
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    addressLine1: '',
    addressLine2: '',
    unit: '',
    postalCode: '',
    city: 'Singapore',
    state: 'Singapore',
    country: 'SG',
  });

  useEffect(() => {
    if (user) {
      fetchUserAddresses();
    }
  }, [user]);

  const fetchUserAddresses = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/users/me/addresses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const addresses = response.data;
      setUserAddresses(addresses);
      
      // Auto-select default address if available
      const defaultAddress = addresses.find(addr => addr.isDefault);
      if (defaultAddress) {
        setSelectedAddressId(defaultAddress.id);
        autofillFromAddress(defaultAddress);
      }
    } catch (error) {
      console.error('Error fetching user addresses:', error);
    }
  };

  const autofillFromAddress = (address) => {
    setFormData({
      fullName: address.fullName,
      phone: address.phone,
      addressLine1: address.addressLine1,
      addressLine2: address.addressLine2 || '',
      unit: address.unit || '',
      postalCode: address.postalCode,
      city: address.city,
      state: address.state,
      country: address.country,
    });
  };

  const handleAddressSelect = (addressId) => {
    setSelectedAddressId(addressId);
    if (addressId === 'new') {
  const handleAddressSelect = (addressId) => {
    setSelectedAddressId(addressId);
    if (addressId === 'new') {
      // Clear form for new address
      setFormData({
        fullName: user?.displayName || `${user?.first_name || ''} ${user?.last_name || ''}`.trim(),
        phone: user?.phone || '',
        addressLine1: '',
        addressLine2: '',
        unit: '',
        postalCode: '',
        city: 'Singapore',
        state: 'Singapore',
        country: 'SG',
      });
      setSaveToProfile(true); // Suggest saving new address
    } else {
      const selectedAddress = userAddresses.find(addr => addr.id === addressId);
      if (selectedAddress) {
        autofillFromAddress(selectedAddress);
        setSaveToProfile(false); // Don't need to save existing address
      }
    }
  };
      // Clear form for new address
      setFormData({
        fullName: user?.displayName || `${user?.first_name || ''} ${user?.last_name || ''}`.trim(),
        phone: user?.phone || '',
        addressLine1: '',
        addressLine2: '',
        unit: '',
        postalCode: '',
        city: 'Singapore',
        state: 'Singapore',
        country: 'SG',
      });
      setSaveToProfile(true); // Suggest saving new address
    } else {
      const selectedAddress = userAddresses.find(addr => addr.id === addressId);
      if (selectedAddress) {
        autofillFromAddress(selectedAddress);
        setSaveToProfile(false); // Don't need to save existing address
      }
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cart || cart.items.length === 0) {
      toast.error('Your cart is empty');
      return;
    }

    try {
      setLoading(true);
      
      // Prepare order data with shipping address snapshot
      const shippingAddress = {
        fullName: formData.fullName,
        phone: formData.phone,
        addressLine1: formData.addressLine1,
        addressLine2: formData.addressLine2,
        unit: formData.unit,
        postalCode: formData.postalCode,
        city: formData.city,
        state: formData.state,
        country: formData.country,
      };

      const orderData = {
        shipping_address: shippingAddress,
        payment_method: 'stripe'
      };
      
      // Add coupon information if applied
      if (appliedCoupon) {
        orderData.coupon_code = appliedCoupon.code;
        orderData.discount_amount = discountAmount;
      }
      
      // Add selected gifts if any
      if (selectedGifts.length > 0) {
        orderData.selected_gifts = selectedGifts;
      }
      
      // Create the order
      const response = await ordersAPI.create(orderData);
      const order = response.data;
      
      // Save address to profile if requested and user is logged in
      if (saveToProfile && user && selectedAddressId === 'new') {
        try {
          const token = localStorage.getItem('access_token');
          const addressData = {
            ...shippingAddress,
            isDefault: userAddresses.length === 0 // Set as default if first address
          };
          
          await axios.post(`${BACKEND_URL}/api/users/me/addresses`, addressData, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          toast.success('Address saved to your profile');
        } catch (error) {
          console.warn('Failed to save address to profile:', error);
          // Don't block order completion for address save failure
        }
      }
      
      // Update last used address in profile
      if (user && selectedAddressId && selectedAddressId !== 'new') {
        try {
          const token = localStorage.getItem('access_token');
          await axios.put(`${BACKEND_URL}/api/users/me`, {
            lastUsedAddressId: selectedAddressId
          }, {
            headers: { Authorization: `Bearer ${token}` }
          });
        } catch (error) {
          console.warn('Failed to update last used address:', error);
        }
      }
      
      toast.success('Order placed successfully!');
      navigate(`/order-success/${order.id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  if (!cart || cart.items.length === 0) {
    navigate('/cart');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="checkout-page">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Checkout</h1>

        <form onSubmit={handleSubmit}>
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Shipping Form */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">Shipping Information</h2>
                
                {/* Address Selector (if user has addresses) */}
                {user && userAddresses.length > 0 && (
                  <div className="mb-6">
                    <Label htmlFor="address-select">Select Shipping Address</Label>
                    <Select value={selectedAddressId} onValueChange={handleAddressSelect}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Choose an address" />
                      </SelectTrigger>
                      <SelectContent>
                        {userAddresses.map((address) => (
                          <SelectItem key={address.id} value={address.id}>
                            <div className="flex items-center gap-2">
                              {address.isDefault && <Star className="w-3 h-3 text-yellow-500" />}
                              <span>{address.fullName} - {address.addressLine1}, {address.city}</span>
                            </div>
                          </SelectItem>
                        ))}
                        <SelectItem value="new">
                          <div className="flex items-center gap-2">
                            <Plus className="w-3 h-3" />
                            <span>Use a new address</span>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="fullName">Full Name *</Label>
                    <Input
                      id="fullName"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleChange}
                      required
                      data-testid="full-name-input"
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone *</Label>
                    <Input
                      id="phone"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                      data-testid="phone-input"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="addressLine1">Address Line 1 *</Label>
                    <Input
                      id="addressLine1"
                      name="addressLine1"
                      value={formData.addressLine1}
                      onChange={handleChange}
                      required
                      data-testid="address-line-1-input"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="addressLine2">Address Line 2</Label>
                    <Input
                      id="addressLine2"
                      name="addressLine2"
                      value={formData.addressLine2}
                      onChange={handleChange}
                      data-testid="address-line-2-input"
                    />
                  </div>
                  <div>
                    <Label htmlFor="unit">Unit</Label>
                    <Input
                      id="unit"
                      name="unit"
                      value={formData.unit}
                      onChange={handleChange}
                      data-testid="unit-input"
                    />
                  </div>
                  <div>
                    <Label htmlFor="postalCode">Postal Code *</Label>
                    <Input
                      id="postalCode"
                      name="postalCode"
                      value={formData.postalCode}
                      onChange={handleChange}
                      required
                      data-testid="postal-code-input"
                      placeholder={formData.country === 'SG' ? '123456' : '12345'}
                      maxLength={formData.country === 'SG' ? 6 : 5}
                    />
                  </div>
                  <div>
                    <Label htmlFor="city">City *</Label>
                    <Input
                      id="city"
                      name="city"
                      value={formData.city}
                      onChange={handleChange}
                      required
                      data-testid="city-input"
                    />
                  </div>
                  <div>
                    <Label htmlFor="state">State *</Label>
                    <Input
                      id="state"
                      name="state"
                      value={formData.state}
                      onChange={handleChange}
                      required
                      data-testid="state-input"
                    />
                  </div>
                </div>
                
                {/* Save to Profile Checkbox */}
                {user && (selectedAddressId === 'new' || selectedAddressId === '') && (
                  <div className="mt-6 p-4 bg-teal-50 border border-teal-200 rounded-lg">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={saveToProfile}
                        onChange={(e) => setSaveToProfile(e.target.checked)}
                        className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
                      />
                      <span className="text-sm font-medium text-slate-900">
                        💾 Save this address to my profile
                      </span>
                    </label>
                    <p className="text-xs text-gray-600 mt-2 ml-6">
                      Save this address for faster checkout next time
                    </p>
                  </div>
                )}
              </div>

              {/* Gift Selection Section */}
              {availableGifts && availableGifts.length > 0 && (
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <GiftSelection 
                    availableGifts={availableGifts} 
                    onGiftSelect={selectGifts}
                  />
                </div>
              )}

              {/* Gift Promotion Section */}
              {(!availableGifts || availableGifts.length === 0) && nearbyGiftTiers && nearbyGiftTiers.length > 0 && (
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <GiftPromotion 
                    nearbyTiers={nearbyGiftTiers} 
                    currentTotal={cart.subtotal - discountAmount}
                  />
                </div>
              )}

              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">Payment Method</h2>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Note:</strong> Payment integration coming soon. Orders will be created as pending.
                  </p>
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg p-6 shadow-sm sticky top-20">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">Order Summary</h2>
                <div className="space-y-3 mb-4">
                  {cart.items.map((item) => (
                    <div key={item.variant_id} className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        {item.product_name} x{item.quantity}
                      </span>
                      <span className="font-medium">{formatPrice(item.line_total)}</span>
                    </div>
                  ))}
                </div>
                
                {/* Coupon Section */}
                <CouponSection showTitle={true} />
                
                <div className="border-t pt-3 space-y-2 mb-4">
                  <div className="flex justify-between text-gray-600">
                    <span>Subtotal</span>
                    <span>{formatPrice(cart.subtotal)}</span>
                  </div>
                  {appliedCoupon && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount ({appliedCoupon.code})</span>
                      <span>-{formatPrice(discountAmount)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-gray-600">
                    <span>Shipping</span>
                    <span>
                      {cart.shipping_fee > 0 ? formatPrice(cart.shipping_fee) : 'Free'}
                    </span>
                  </div>
                  {cart.total_weight_grams && (
                    <div className="text-xs text-gray-500 mb-2">
                      Weight: {Math.round(cart.total_weight_grams)}g • {cart.delivery_estimate}
                    </div>
                  )}
                  <div className="flex justify-between text-lg font-bold text-slate-900">
                    <span>Total</span>
                    <span data-testid="order-total">{formatPrice(finalTotal)}</span>
                  </div>
                </div>
                <Button
                  type="submit"
                  className="w-full bg-teal-700 hover:bg-teal-800"
                  size="lg"
                  disabled={loading}
                  data-testid="place-order-button"
                >
                  {loading ? 'Placing Order...' : 'Place Order'}
                </Button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Checkout;
