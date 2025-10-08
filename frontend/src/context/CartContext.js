  // Watch for cart changes and revalidate coupon
  useEffect(() => {
    if (appliedCoupon && cart && cart.subtotal !== undefined) {
      revalidateCoupon(cart);
    }
  }, [cart?.subtotal, revalidateCoupon]); // Re-run when cart subtotal changes