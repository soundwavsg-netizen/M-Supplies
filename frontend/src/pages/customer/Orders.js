import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ordersAPI } from '@/lib/api';
import { formatPrice, formatDate } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Package } from 'lucide-react';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await ordersAPI.list();
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      paid: 'bg-blue-100 text-blue-800',
      processing: 'bg-purple-100 text-purple-800',
      shipped: 'bg-teal-100 text-teal-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="orders-page">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">My Orders</h1>

        {orders.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center">
            <Package className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No orders yet</h2>
            <p className="text-gray-600 mb-6">Start shopping to create your first order</p>
            <Link
              to="/products"
              className="inline-block bg-teal-700 text-white px-6 py-2 rounded-lg hover:bg-teal-800 transition"
            >
              Browse Products
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg p-6 shadow-sm" data-testid={`order-${order.id}`}>
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      Order #{order.order_number}
                    </h3>
                    <p className="text-sm text-gray-600">{formatDate(order.created_at)}</p>
                  </div>
                  <Badge className={getStatusColor(order.status)}>
                    {order.status.toUpperCase()}
                  </Badge>
                </div>

                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Items</h4>
                    <ul className="space-y-1">
                      {order.items.slice(0, 3).map((item, idx) => (
                        <li key={idx} className="text-sm text-gray-600">
                          {item.product_name} x{item.quantity}
                        </li>
                      ))}
                      {order.items.length > 3 && (
                        <li className="text-sm text-gray-500">+{order.items.length - 3} more items</li>
                      )}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Total</h4>
                    <p className="text-2xl font-bold text-teal-700">{formatPrice(order.total)}</p>
                  </div>
                </div>

                {order.tracking_number && (
                  <div className="bg-teal-50 rounded-lg p-3">
                    <p className="text-sm font-medium text-teal-900">
                      Tracking: {order.tracking_number}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Orders;
