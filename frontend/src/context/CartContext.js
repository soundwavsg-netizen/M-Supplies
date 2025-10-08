import React, { createContext, useContext, useState, useEffect } from 'react';
import { cartAPI } from '@/lib/api';
import { toast } from 'sonner';

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

  const fetchCart = async () => {
    try {
      setLoading(true);
      const response = await cartAPI.get();
      setCart(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const addToCart = async (variantId, quantity = 1) => {
    try {
      const response = await cartAPI.add({ variant_id: variantId, quantity });
      setCart(response.data);
      toast.success('Added to cart');
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add to cart');
      throw error;
    }
  };

  const updateCartItem = async (variantId, quantity) => {
    try {
      const response = await cartAPI.update(variantId, { quantity });
      setCart(response.data);
      if (quantity === 0) {
        toast.success('Item removed from cart');
      }
      return response.data;
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
      setAppliedCoupon(null);
      setDiscountAmount(0);
      setAvailableGifts([]);
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

  const removeCoupon = () => {
    setAppliedCoupon(null);
    setDiscountAmount(0);
    setAvailableGifts([]);
  };

  // Calculate final total with discount
  const finalTotal = cart ? cart.total - discountAmount : 0;

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
      }}
    >
      {children}
    </CartContext.Provider>
  );
};
