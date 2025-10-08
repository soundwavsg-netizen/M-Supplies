import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { cartAPI } from '@/lib/api';
import { toast } from 'sonner';
import axios from 'axios';

const CartContext = createContext(null);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Coupon state management
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [availableGifts, setAvailableGifts] = useState([]);
  const [selectedGifts, setSelectedGifts] = useState([]);
  const [nearbyGiftTiers, setNearbyGiftTiers] = useState([]);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  // Automatic coupon revalidation when cart changes
  const revalidateCoupon = useCallback(async (updatedCart) => {
    if (!appliedCoupon || !updatedCart) {
      return;
    }

    try {
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
        coupon_code: appliedCoupon.code,
        order_subtotal: updatedCart.subtotal,
        user_id: userId
      };

      const response = await axios.post(`${BACKEND_URL}/api/promotions/validate`, validationData);
      
      if (response.data.valid) {
        // Update discount amount based on new cart total
        const newDiscountAmount = response.data.discount_amount;
        setDiscountAmount(newDiscountAmount);
        setAvailableGifts(response.data.available_gift_tiers || []);
        
        // Only show notification if discount changed significantly
        if (Math.abs(newDiscountAmount - discountAmount) > 0.01) {
          toast.info(`Discount updated: -${(newDiscountAmount).toFixed(2)}`);
        }
      } else {
        // Coupon no longer valid (e.g., below minimum order)
        removeCoupon();
        toast.warning(response.data.error_message || 'Coupon removed: cart no longer qualifies');
      }
    } catch (error) {
      console.error('Coupon revalidation error:', error);
      // If revalidation fails, remove coupon to be safe
      removeCoupon();
      toast.warning('Coupon removed due to validation error');
    }
  }, [appliedCoupon, discountAmount, BACKEND_URL]);

  const fetchCart = async () => {
    try {
      setLoading(true);
      const response = await cartAPI.get();
      const newCart = response.data;
      setCart(newCart);
      
      // Revalidate coupon if one is applied
      if (appliedCoupon && newCart) {
        await revalidateCoupon(newCart);
      }
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  // Check gift tier eligibility based on post-discount amount
  const checkGiftTierEligibility = useCallback(async (afterDiscountAmount) => {
    try {
      // Get available gift tiers for this amount
      const response = await axios.get(`${BACKEND_URL}/api/gift-tiers/available?order_amount=${afterDiscountAmount}`);
      const qualifyingTiers = response.data;
      
      setAvailableGifts(qualifyingTiers);
      
      // Also check nearby tiers (for promotional messages)
      const nearbyResponse = await axios.get(`${BACKEND_URL}/api/gift-tiers/nearby?order_amount=${afterDiscountAmount}`);
      setNearbyGiftTiers(nearbyResponse.data || []);
      
    } catch (error) {
      console.error('Error checking gift tier eligibility:', error);
      setAvailableGifts([]);
      setNearbyGiftTiers([]);
    }
  }, [BACKEND_URL]);

  // Watch for cart and discount changes to update gift eligibility
  useEffect(() => {
    if (cart && cart.subtotal !== undefined) {
      const afterDiscountAmount = cart.subtotal - discountAmount;
      checkGiftTierEligibility(afterDiscountAmount);
    }
  }, [cart?.subtotal, discountAmount, checkGiftTierEligibility]);

  useEffect(() => {
    fetchCart();
  }, []);

  const addToCart = async (variantId, quantity = 1) => {
    try {
      const response = await cartAPI.add({ variant_id: variantId, quantity });
      const newCart = response.data;
      setCart(newCart);
      
      // Revalidate coupon after adding item
      if (appliedCoupon && newCart) {
        await revalidateCoupon(newCart);
      }
      
      toast.success('Added to cart');
      return newCart;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add to cart');
      throw error;
    }
  };

  const updateCartItem = async (variantId, quantity) => {
    try {
      const response = await cartAPI.update(variantId, { quantity });
      const newCart = response.data;
      setCart(newCart);
      
      // Revalidate coupon after updating cart
      if (appliedCoupon && newCart) {
        await revalidateCoupon(newCart);
      }
      
      if (quantity === 0) {
        toast.success('Item removed from cart');
      }
      return newCart;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update cart');
      throw error;
    }
  };

  const clearCart = async () => {
    try {
      await cartAPI.clear();
      setCart({ ...cart, items: [], subtotal: 0, gst: 0, total: 0 });
      // Clear coupon state when cart is cleared
      removeCoupon();
      toast.success('Cart cleared');
    } catch (error) {
      toast.error('Failed to clear cart');
    }
  };

  // Coupon management functions
  const applyCoupon = (coupon, discount, gifts = []) => {
    setAppliedCoupon(coupon);
    setDiscountAmount(discount);
    setAvailableGifts(gifts);
  };

  const removeCoupon = useCallback(() => {
    setAppliedCoupon(null);
    setDiscountAmount(0);
    setAvailableGifts([]);
  }, []);

  // Calculate final total with discount and shipping
  const finalTotal = cart ? (cart.subtotal + (cart.shipping_fee || 0) - discountAmount) : 0;

  const cartItemCount = cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        cartItemCount,
        fetchCart,
        addToCart,
        updateCartItem,
        clearCart,
        // Coupon functionality
        appliedCoupon,
        discountAmount,
        availableGifts,
        finalTotal,
        applyCoupon,
        removeCoupon,
        revalidateCoupon,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};
