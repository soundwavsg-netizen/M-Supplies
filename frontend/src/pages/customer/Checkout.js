import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '@/context/CartContext';
import { useAuth } from '@/context/AuthContext';
import { ordersAPI } from '@/lib/api';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import CouponSection from '@/components/ui/CouponSection';
import GiftSelection from '@/components/ui/GiftSelection';

const Checkout = () => {
  const { cart, appliedCoupon, discountAmount, availableGifts, finalTotal } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [selectedGifts, setSelectedGifts] = useState([]);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    address_line1: '',
    address_line2: '',
    city: 'Singapore',
    state: 'Singapore',
    postal_code: '',
    country: 'Singapore',
  });

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
      const orderData = {
        shipping_address: formData,
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
      
      const response = await ordersAPI.create(orderData);
      
      const order = response.data;
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
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first_name">First Name *</Label>
                    <Input
                      id="first_name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      required
                      data-testid="first-name-input"
                    />
                  </div>
                  <div>
                    <Label htmlFor="last_name">Last Name *</Label>
                    <Input
                      id="last_name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      required
                      data-testid="last-name-input"
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      data-testid="email-input"
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
                    <Label htmlFor="address_line1">Address Line 1 *</Label>
                    <Input
                      id="address_line1"
                      name="address_line1"
                      value={formData.address_line1}
                      onChange={handleChange}
                      required
                      data-testid="address1-input"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="address_line2">Address Line 2</Label>
                    <Input
                      id="address_line2"
                      name="address_line2"
                      value={formData.address_line2}
                      onChange={handleChange}
                    />
                  </div>
                  <div>
                    <Label htmlFor="postal_code">Postal Code *</Label>
                    <Input
                      id="postal_code"
                      name="postal_code"
                      value={formData.postal_code}
                      onChange={handleChange}
                      required
                      data-testid="postal-code-input"
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
                      readOnly
                    />
                  </div>
                </div>
              </div>

              {/* Gift Selection Section */}
              {availableGifts && availableGifts.length > 0 && (
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <GiftSelection 
                    availableGifts={availableGifts} 
                    onGiftSelect={setSelectedGifts}
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
