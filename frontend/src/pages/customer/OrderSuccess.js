import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle, Package } from 'lucide-react';
import { ordersAPI } from '@/lib/api';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const OrderSuccess = () => {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId) {
      fetchOrder();
    }
  }, [orderId]);

  const fetchOrder = async () => {
    try {
      const response = await ordersAPI.get(orderId);
      setOrder(response.data);
    } catch (error) {
      console.error('Error fetching order:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center" data-testid="order-success-page">
      <div className="max-w-2xl w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Order Placed Successfully!</h1>
          <p className="text-gray-600 mb-8">
            Thank you for your order. We'll send you an email confirmation shortly.
          </p>

          {order && (
            <div className="bg-gray-50 rounded-lg p-6 mb-8 text-left">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">
                Order #{order.order_number}
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Amount</span>
                  <span className="font-semibold text-teal-700" data-testid="order-total">
                    {formatPrice(order.total)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status</span>
                  <span className="font-medium text-blue-600">{order.status.toUpperCase()}</span>
                </div>
                <div className="border-t pt-3">
                  <p className="text-sm text-gray-600 mb-2">Shipping to:</p>
                  <p className="text-sm text-gray-900">
                    {order.shipping_address.first_name} {order.shipping_address.last_name}<br />
                    {order.shipping_address.address_line1}<br />
                    {order.shipping_address.city}, {order.shipping_address.postal_code}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/orders">
              <Button size="lg" className="bg-teal-700 hover:bg-teal-800">
                <Package className="mr-2 w-5 h-5" />
                View My Orders
              </Button>
            </Link>
            <Link to="/products">
              <Button size="lg" variant="outline">
                Continue Shopping
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderSuccess;
