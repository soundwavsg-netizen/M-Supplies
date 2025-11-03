import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Percent, Plus, Edit2, Trash2, Tag, Users } from 'lucide-react';
import axios from 'axios';
import { useAuthenticatedAPI } from '@/hooks/useAuthenticatedAPI';

const Promotions = () => {
  const { idToken } = useAuthenticatedAPI();
  const [coupons, setCoupons] = useState([]);
  const [giftItems, setGiftItems] = useState([]);
  const [giftTiers, setGiftTiers] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  
  // Modal states
  const [showCouponModal, setShowCouponModal] = useState(false);
  const [showGiftModal, setShowGiftModal] = useState(false);
  const [showTierModal, setShowTierModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (idToken) {
      fetchAllData();
    }
  }, [idToken]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${idToken}` };

      const [couponsRes, giftsRes, tiersRes, statsRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/admin/coupons`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/gift-items`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/gift-tiers`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/promotions/stats`, { headers })
      ]);

      setCoupons(couponsRes.data || []);
      setGiftItems(giftsRes.data || []);
      setGiftTiers(tiersRes.data || []);
      setStats(statsRes.data || {});
    } catch (error) {
      // Only show error if it's not a 401 (handled by redirect) and not empty data
      if (error.response?.status !== 401) {
        toast.error('Failed to load promotions data');
      }
      console.error('Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  // ==================== COUPON MANAGEMENT ====================

  const CouponForm = ({ coupon, onClose, onSave }) => {
    const [formData, setFormData] = useState({
      code: coupon?.code || '',
      type: coupon?.type || 'percent',
      value: coupon?.value || '',
      min_order_amount: coupon?.min_order_amount || '',
      valid_from: coupon?.valid_from ? coupon.valid_from.split('T')[0] : new Date().toISOString().split('T')[0],
      valid_to: coupon?.valid_to ? coupon.valid_to.split('T')[0] : new Date(Date.now() + 365*24*60*60*1000).toISOString().split('T')[0], // Default to 1 year from now
      is_active: coupon?.is_active ?? true
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      // Frontend validation
      if (!formData.code.trim()) {
        toast.error('Coupon code is required');
        return;
      }
      
      if (!formData.value || parseFloat(formData.value) <= 0) {
        toast.error('Discount value must be greater than 0');
        return;
      }
      
      if (formData.type === 'percent' && parseFloat(formData.value) > 100) {
        toast.error('Percentage discount cannot exceed 100%');
        return;
      }
      
      if (!formData.valid_from) {
        toast.error('Valid from date is required');
        return;
      }
      
      if (!formData.valid_to) {
        toast.error('Valid to date is required');
        return;
      }
      
      try {
        const token = idToken;
        const payload = {
          code: formData.code.toUpperCase(),
          type: formData.type,
          value: parseFloat(formData.value),
          min_order_amount: formData.min_order_amount ? parseFloat(formData.min_order_amount) : 0,
          valid_from: new Date(formData.valid_from).toISOString(),
          valid_to: new Date(formData.valid_to).toISOString(),
          is_active: formData.is_active
        };

        if (coupon) {
          await axios.put(`${BACKEND_URL}/api/admin/coupons/${coupon.id}`, payload, {
            headers: { Authorization: `Bearer ${token}` }
          });
          toast.success('Coupon updated successfully');
        } else {
          await axios.post(`${BACKEND_URL}/api/admin/coupons`, payload, {
            headers: { Authorization: `Bearer ${token}` }
          });
          toast.success('Coupon created successfully');
        }

        onSave();
        onClose();
        fetchAllData();
      } catch (error) {
        console.error('Coupon save error:', error);
        
        // Handle different error response formats
        let errorMessage = 'Failed to save coupon';
        
        if (error.response?.data) {
          const errorData = error.response.data;
          
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // Handle validation errors array
            errorMessage = errorData.detail.map(err => err.msg || err).join(', ');
          } else if (errorData.message) {
            errorMessage = errorData.message;
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        toast.error(errorMessage);
      }
    };

    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="code">Coupon Code *</Label>
          <Input
            id="code"
            value={formData.code}
            onChange={(e) => setFormData(prev => ({ ...prev, code: e.target.value.toUpperCase() }))}
            placeholder="VIP10, SAVE15, etc."
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="type">Discount Type *</Label>
            <Select value={formData.type} onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="percent">Percentage (%)</SelectItem>
                <SelectItem value="fixed">Fixed Amount ($)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="value">
              {formData.type === 'percent' ? 'Percentage (%)' : 'Amount ($)'} *
            </Label>
            <Input
              id="value"
              type="number"
              step="0.01"
              value={formData.value}
              onChange={(e) => setFormData(prev => ({ ...prev, value: e.target.value }))}
              placeholder={formData.type === 'percent' ? '10' : '5.00'}
              required
            />
          </div>
        </div>

        <div>
          <Label htmlFor="min_order_amount">Minimum Order Amount ($)</Label>
          <Input
            id="min_order_amount"
            type="number"
            step="0.01"
            value={formData.min_order_amount}
            onChange={(e) => setFormData(prev => ({ ...prev, min_order_amount: e.target.value }))}
            placeholder="0.00"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="valid_from">Valid From Date *</Label>
            <Input
              id="valid_from"
              type="date"
              value={formData.valid_from}
              onChange={(e) => setFormData(prev => ({ ...prev, valid_from: e.target.value }))}
              required
            />
          </div>
          <div>
            <Label htmlFor="valid_to">Valid To Date *</Label>
            <Input
              id="valid_to"
              type="date"
              value={formData.valid_to}
              onChange={(e) => setFormData(prev => ({ ...prev, valid_to: e.target.value }))}
              required
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_active"
            checked={formData.is_active}
            onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
          />
          <Label htmlFor="is_active">Active</Label>
        </div>

        <div className="flex gap-3">
          <Button type="submit" className="flex-1">
            {coupon ? 'Update Coupon' : 'Create Coupon'}
          </Button>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </form>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Tag className="w-12 h-12 text-teal-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading promotions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-8">Coupon Management</h1>

      {/* Stats Grid */}
      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Coupons</CardTitle>
                <Tag className="h-4 w-4 text-teal-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_coupons || 0}</div>
                <p className="text-xs text-muted-foreground">All coupons created</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Coupons</CardTitle>
                <Percent className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.active_coupons || 0}</div>
                <p className="text-xs text-muted-foreground">Currently available</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
                <Users className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_coupon_usage || 0}</div>
                <p className="text-xs text-muted-foreground">Times used</p>
              </CardContent>
            </Card>
          </div>

          {/* Coupons List */}
          <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Discount Coupons</CardTitle>
                    <CardDescription>Manage VIP codes, percentage discounts, and fixed amount coupons</CardDescription>
                  </div>
                  <Dialog open={showCouponModal} onOpenChange={setShowCouponModal}>
                    <DialogTrigger asChild>
                      <Button onClick={() => setEditingItem(null)}>
                        <Plus className="w-4 h-4 mr-2" />
                        Add Coupon
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>{editingItem ? 'Edit Coupon' : 'Create New Coupon'}</DialogTitle>
                        <DialogDescription>
                          Create discount codes for VIP customers, promotional campaigns, and special events.
                        </DialogDescription>
                      </DialogHeader>
                      <CouponForm 
                        coupon={editingItem} 
                        onClose={() => setShowCouponModal(false)}
                        onSave={() => setEditingItem(null)}
                      />
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {coupons.map((coupon) => (
                    <div key={coupon.id} className="flex items-center justify-between p-4 border rounded-lg bg-white">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <Badge variant={coupon.is_active ? 'default' : 'secondary'}>
                            {coupon.code}
                          </Badge>
                          <span className="font-medium">
                            {coupon.type === 'percent' ? `${coupon.value}% off` : `$${coupon.value} off`}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {coupon.min_order_amount > 0 && `Min order $${coupon.min_order_amount} • `}
                          Valid from {new Date(coupon.valid_from).toLocaleDateString()}
                          {coupon.valid_to && ` to ${new Date(coupon.valid_to).toLocaleDateString()}`}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => {
                            setEditingItem(coupon);
                            setShowCouponModal(true);
                          }}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          className="text-red-600 hover:text-red-700"
                          onClick={async () => {
                            if (window.confirm('Delete this coupon?')) {
                              try {
                                const token = idToken;
                                await axios.delete(`${BACKEND_URL}/api/admin/coupons/${coupon.id}`, {
                                  headers: { Authorization: `Bearer ${token}` }
                                });
                                toast.success('Coupon deleted');
                                fetchAllData();
                              } catch (error) {
                                console.error('Delete error:', error);
                                const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to delete coupon';
                                toast.error(typeof errorMessage === 'string' ? errorMessage : 'Failed to delete coupon');
                              }
                            }
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {coupons.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Percent className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No discount coupons created yet</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
        </>
      )}
      </div>
    </div>
  );
};

export default Promotions;