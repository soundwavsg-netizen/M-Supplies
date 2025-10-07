import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus, ShoppingBag, Tag, X, Check } from 'lucide-react';
import { useCart } from '@/context/CartContext';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import axios from 'axios';

const Cart = () => {
  const { cart, loading, updateCartItem, clearCart } = useCart();
  const navigate = useNavigate();
  
  // Coupon state
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [couponLoading, setCouponLoading] = useState(false);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [availableGifts, setAvailableGifts] = useState([]);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const validateCoupon = async () => {
    if (!couponCode.trim()) {
      toast.error('Please enter a coupon code');
      return;
    }

    try {
      setCouponLoading(true);
      
      // Get user ID if logged in
      const token = localStorage.getItem('access_token');
      let userId = null;
      if (token) {
        try {
          const userResponse = await axios.get(`${BACKEND_URL}/api/users/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          userId = userResponse.data.id;
        } catch (error) {
          // User not logged in, continue without userId
        }
      }

      const validationData = {
        coupon_code: couponCode.toUpperCase(),
        order_subtotal: cart.subtotal,
        user_id: userId
      };

      const response = await axios.post(`${BACKEND_URL}/api/promotions/validate`, validationData);
      
      if (response.data.valid) {
        setAppliedCoupon(response.data.applied_coupon);
        setDiscountAmount(response.data.discount_amount);
        setAvailableGifts(response.data.available_gift_tiers || []);
        toast.success(`Coupon applied! You saved ${formatPrice(response.data.discount_amount)}`);
        
        if (response.data.available_gift_tiers?.length > 0) {
          toast.success(`You qualify for free gifts! Select them at checkout.`);
        }
      } else {
        toast.error(response.data.error_message || 'Invalid coupon code');
        removeCoupon();
      }
    } catch (error) {
      console.error('Coupon validation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to validate coupon');
      removeCoupon();
    } finally {
      setCouponLoading(false);
    }
  };

  const removeCoupon = () => {
    setAppliedCoupon(null);
    setDiscountAmount(0);
    setAvailableGifts([]);
    setCouponCode('');
  };

  // Calculate final total with discount
  const finalTotal = cart.total - discountAmount;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700"></div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center" data-testid="empty-cart">
        <div className="text-center">
          <ShoppingBag className="w-24 h-24 mx-auto text-gray-300 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
          <p className="text-gray-600 mb-6">Start shopping to add items to your cart</p>
          <Link to="/products">
            <Button>Browse Products</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="cart-page">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Shopping Cart</h1>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart.items.map((item) => (
              <div key={item.variant_id} className="bg-white rounded-lg p-6 shadow-sm" data-testid={`cart-item-${item.variant_id}`}>
                <div className="flex gap-4">
                  <div className="w-24 h-24 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                    <img
                      src={item.product_image || 'https://via.placeholder.com/100'}
                      alt={item.product_name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 mb-1">{item.product_name}</h3>
                    <p className="text-sm text-gray-600 mb-2">
                      {item.attributes.size} - {item.attributes.color}
                    </p>
                    <p className="text-sm text-gray-500">SKU: {item.sku}</p>
                  </div>
                  <div className="text-right space-y-2">
                    <p className="text-lg font-bold text-teal-700">{formatPrice(item.line_total)}</p>
                    <p className="text-sm text-gray-500">{formatPrice(item.price)} each</p>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-4 pt-4 border-t">
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => updateCartItem(item.variant_id, item.quantity - 1)}
                      disabled={item.quantity <= 1}
                      data-testid={`decrease-qty-${item.variant_id}`}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                    <span className="w-12 text-center font-medium" data-testid={`quantity-${item.variant_id}`}>{item.quantity}</span>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => updateCartItem(item.variant_id, item.quantity + 1)}
                      data-testid={`increase-qty-${item.variant_id}`}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => updateCartItem(item.variant_id, 0)}
                    className="text-red-600 hover:text-red-700"
                    data-testid={`remove-${item.variant_id}`}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg p-6 shadow-sm sticky top-20">
              <h2 className="text-xl font-bold text-slate-900 mb-4">Order Summary</h2>
              <div className="space-y-3 mb-4">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span data-testid="subtotal">{formatPrice(cart.subtotal)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>GST (9%)</span>
                  <span data-testid="gst">{formatPrice(cart.gst)}</span>
                </div>
                <div className="border-t pt-3 flex justify-between text-lg font-bold text-slate-900">
                  <span>Total</span>
                  <span data-testid="total">{formatPrice(cart.total)}</span>
                </div>
              </div>
              <Button
                className="w-full bg-teal-700 hover:bg-teal-800 mb-3"
                size="lg"
                onClick={() => navigate('/checkout')}
                data-testid="checkout-button"
              >
                Proceed to Checkout
              </Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => navigate('/products')}
              >
                Continue Shopping
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
