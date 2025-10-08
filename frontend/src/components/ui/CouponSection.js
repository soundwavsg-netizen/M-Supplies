import React, { useState } from 'react';
import { Tag, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { formatPrice } from '@/lib/utils';
import { useCart } from '@/context/CartContext';
import axios from 'axios';

const CouponSection = ({ showTitle = true }) => {
  const { cart, appliedCoupon, discountAmount, applyCoupon, removeCoupon } = useCart();
  const [couponCode, setCouponCode] = useState('');
  const [couponLoading, setCouponLoading] = useState(false);
  
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
        applyCoupon(response.data.applied_coupon, response.data.discount_amount, response.data.available_gift_tiers || []);
        toast.success(`Coupon applied! You saved ${formatPrice(response.data.discount_amount)}`);
        setCouponCode(''); // Clear input after successful application
        
        if (response.data.available_gift_tiers?.length > 0) {
          toast.success(`You qualify for free gifts! Select them at checkout.`);
        }
      } else {
        toast.error(response.data.error_message || 'Invalid coupon code');
      }
    } catch (error) {
      console.error('Coupon validation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to validate coupon');
    } finally {
      setCouponLoading(false);
    }
  };

  const handleRemoveCoupon = () => {
    removeCoupon();
    setCouponCode('');
    toast.info('Coupon removed');
  };

  return (
    <div className="mb-6 p-4 bg-gray-50 rounded-lg">
      {showTitle && (
        <div className="flex items-center gap-2 mb-3">
          <Tag className="w-4 h-4 text-teal-600" />
          <span className="font-medium text-gray-700">Promo Code</span>
        </div>
      )}
      
      {!appliedCoupon ? (
        <div className="flex gap-2">
          <Input
            placeholder="Enter coupon code"
            value={couponCode}
            onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
            onKeyPress={(e) => e.key === 'Enter' && validateCoupon()}
            className="flex-1"
            disabled={couponLoading}
          />
          <Button 
            onClick={validateCoupon}
            disabled={couponLoading || !couponCode.trim()}
            className="bg-teal-600 hover:bg-teal-700 text-white px-6"
          >
            {couponLoading ? 'Applying...' : 'Apply'}
          </Button>
        </div>
      ) : (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-600" />
            <div>
              <Badge variant="secondary" className="bg-green-100 text-green-800 mb-1">
                {appliedCoupon.code}
              </Badge>
              <p className="text-sm text-green-700">
                Discount: -{formatPrice(discountAmount)}
              </p>
            </div>
          </div>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleRemoveCoupon}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default CouponSection;