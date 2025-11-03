import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Gift, Award, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { formatPrice } from '@/lib/utils';
import axios from 'axios';
import { useAuthenticatedAPI } from '@/hooks/useAuthenticatedAPI';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const GiftManagement = () => {
  const { idToken } = useAuthenticatedAPI();
  const [giftItems, setGiftItems] = useState([]);
  const [giftTiers, setGiftTiers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTab, setSelectedTab] = useState('items'); // 'items' or 'tiers'

  // Gift Item Form State
  const [giftItemForm, setGiftItemForm] = useState({
    name: '',
    description: '',
    image_url: '',
    stock_quantity: 0
  });

  // Gift Tier Form State  
  const [giftTierForm, setGiftTierForm] = useState({
    name: '',
    spending_threshold: 0,
    gift_limit: 1,
    gift_item_ids: []
  });

  const [isItemModalOpen, setIsItemModalOpen] = useState(false);
  const [isTierModalOpen, setIsTierModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [editingTier, setEditingTier] = useState(null);

  useEffect(() => {
    if (idToken) {
      fetchAllData();
    }
  }, [idToken]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const token = idToken;
      const headers = { Authorization: `Bearer ${token}` };

      const [itemsResponse, tiersResponse] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/admin/gift-items`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/gift-tiers`, { headers })
      ]);

      setGiftItems(itemsResponse.data);
      setGiftTiers(tiersResponse.data);
    } catch (error) {
      toast.error('Failed to load gift data');
      console.error('Error fetching gift data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGiftItem = async () => {
    try {
      const token = idToken;
      const headers = { Authorization: `Bearer ${token}` };

      if (editingItem) {
        await axios.put(`${BACKEND_URL}/api/admin/gift-items/${editingItem.id}`, giftItemForm, { headers });
        toast.success('Gift item updated successfully');
      } else {
        await axios.post(`${BACKEND_URL}/api/admin/gift-items`, giftItemForm, { headers });
        toast.success('Gift item created successfully');
      }

      resetItemForm();
      setIsItemModalOpen(false);
      await fetchAllData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save gift item');
    }
  };

  const handleCreateGiftTier = async () => {
    try {
      const token = idToken;
      const headers = { Authorization: `Bearer ${token}` };

      if (editingTier) {
        await axios.put(`${BACKEND_URL}/api/admin/gift-tiers/${editingTier.id}`, giftTierForm, { headers });
        toast.success('Gift tier updated successfully');
      } else {
        await axios.post(`${BACKEND_URL}/api/admin/gift-tiers`, giftTierForm, { headers });
        toast.success('Gift tier created successfully');
      }

      resetTierForm();
      setIsTierModalOpen(false);
      await fetchAllData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save gift tier');
    }
  };

  const handleDeleteGiftItem = async (itemId) => {
    if (!window.confirm('Are you sure you want to delete this gift item?')) return;

    try {
      const token = idToken;
      await axios.delete(`${BACKEND_URL}/api/admin/gift-items/${itemId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Gift item deleted');
      await fetchAllData();
    } catch (error) {
      toast.error('Failed to delete gift item');
    }
  };

  const handleDeleteGiftTier = async (tierId) => {
    if (!window.confirm('Are you sure you want to delete this gift tier?')) return;

    try {
      const token = idToken;
      await axios.delete(`${BACKEND_URL}/api/admin/gift-tiers/${tierId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Gift tier deleted');
      await fetchAllData();
    } catch (error) {
      toast.error('Failed to delete gift tier');
    }
  };

  const resetItemForm = () => {
    setGiftItemForm({
      name: '',
      description: '',
      image_url: '',
      stock_quantity: 0
    });
    setEditingItem(null);
  };

  const resetTierForm = () => {
    setGiftTierForm({
      name: '',
      spending_threshold: 0,
      gift_limit: 1,
      gift_item_ids: []
    });
    setEditingTier(null);
  };

  const openEditItemModal = (item) => {
    setGiftItemForm({
      name: item.name,
      description: item.description,
      image_url: item.image_url || '',
      stock_quantity: item.stock_quantity
    });
    setEditingItem(item);
    setIsItemModalOpen(true);
  };

  const openEditTierModal = (tier) => {
    setGiftTierForm({
      name: tier.name,
      spending_threshold: tier.spending_threshold,
      gift_limit: tier.gift_limit,
      gift_item_ids: tier.gift_items?.map(item => item.id) || []
    });
    setEditingTier(tier);
    setIsTierModalOpen(true);
  };

  const handleGiftItemSelection = (itemId, isSelected) => {
    if (isSelected) {
      setGiftTierForm(prev => ({
        ...prev,
        gift_item_ids: [...prev.gift_item_ids, itemId]
      }));
    } else {
      setGiftTierForm(prev => ({
        ...prev,
        gift_item_ids: prev.gift_item_ids.filter(id => id !== itemId)
      }));
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
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Gift Management</h1>
          <p className="text-gray-600">Manage gift items and spending tier rewards for your customers</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-8 bg-gray-100 p-1 rounded-lg w-fit">
          <Button
            variant={selectedTab === 'items' ? 'default' : 'ghost'}
            onClick={() => setSelectedTab('items')}
            className="flex items-center gap-2"
          >
            <Gift className="w-4 h-4" />
            Gift Items ({giftItems.length})
          </Button>
          <Button
            variant={selectedTab === 'tiers' ? 'default' : 'ghost'}
            onClick={() => setSelectedTab('tiers')}
            className="flex items-center gap-2"
          >
            <Award className="w-4 h-4" />
            Gift Tiers ({giftTiers.length})
          </Button>
        </div>

        {/* Gift Items Tab */}
        {selectedTab === 'items' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-slate-900">Gift Items</h2>
              <Dialog open={isItemModalOpen} onOpenChange={setIsItemModalOpen}>
                <DialogTrigger asChild>
                  <Button onClick={resetItemForm} className="bg-teal-600 hover:bg-teal-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Gift Item
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>{editingItem ? 'Edit' : 'Create'} Gift Item</DialogTitle>
                  </DialogHeader>
                  
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="gift-name">Gift Name *</Label>
                      <Input
                        id="gift-name"
                        value={giftItemForm.name}
                        onChange={(e) => setGiftItemForm(prev => ({...prev, name: e.target.value}))}
                        placeholder="e.g., Premium Stickers Pack"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="gift-description">Description *</Label>
                      <Textarea
                        id="gift-description"
                        value={giftItemForm.description}
                        onChange={(e) => setGiftItemForm(prev => ({...prev, description: e.target.value}))}
                        placeholder="Describe the gift item..."
                        rows={3}
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="gift-image">Image URL</Label>
                      <Input
                        id="gift-image"
                        type="url"
                        value={giftItemForm.image_url}
                        onChange={(e) => setGiftItemForm(prev => ({...prev, image_url: e.target.value}))}
                        placeholder="https://example.com/image.jpg"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="gift-stock">Stock Quantity *</Label>
                      <Input
                        id="gift-stock"
                        type="number"
                        min="0"
                        value={giftItemForm.stock_quantity}
                        onChange={(e) => setGiftItemForm(prev => ({...prev, stock_quantity: parseInt(e.target.value) || 0}))}
                      />
                    </div>
                    
                    <div className="flex gap-3">
                      <Button 
                        onClick={handleCreateGiftItem}
                        disabled={!giftItemForm.name || !giftItemForm.description}
                        className="flex-1"
                      >
                        {editingItem ? 'Update' : 'Create'} Gift Item
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => setIsItemModalOpen(false)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            {/* Gift Items Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {giftItems.map((item) => (
                <Card key={item.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-lg">{item.name}</CardTitle>
                      <Badge variant={item.is_active ? "default" : "secondary"}>
                        {item.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 text-sm mb-3">{item.description}</p>
                    
                    {item.image_url && (
                      <div className="mb-3">
                        <img 
                          src={item.image_url} 
                          alt={item.name}
                          className="w-full h-32 object-cover rounded-lg"
                          onError={(e) => {e.target.style.display = 'none'}}
                        />
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                      <span>Stock: {item.stock_quantity}</span>
                      <span>ID: {item.id.substring(0, 8)}...</span>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => openEditItemModal(item)}
                        className="flex-1"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => handleDeleteGiftItem(item.id)}
                        className="text-red-600 hover:text-red-700 hover:border-red-200"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {giftItems.length === 0 && (
                <div className="col-span-full text-center py-12">
                  <Package className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-500 mb-2">No Gift Items</h3>
                  <p className="text-gray-400 mb-4">Create your first gift item to start offering customer rewards</p>
                  <Button onClick={() => {resetItemForm(); setIsItemModalOpen(true)}} className="bg-teal-600 hover:bg-teal-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Gift Item
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Gift Tiers Tab */}
        {selectedTab === 'tiers' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-slate-900">Gift Tiers</h2>
              <Dialog open={isTierModalOpen} onOpenChange={setIsTierModalOpen}>
                <DialogTrigger asChild>
                  <Button onClick={resetTierForm} className="bg-teal-600 hover:bg-teal-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Gift Tier
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-lg">
                  <DialogHeader>
                    <DialogTitle>{editingTier ? 'Edit' : 'Create'} Gift Tier</DialogTitle>
                  </DialogHeader>
                  
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="tier-name">Tier Name *</Label>
                      <Input
                        id="tier-name"
                        value={giftTierForm.name}
                        onChange={(e) => setGiftTierForm(prev => ({...prev, name: e.target.value}))}
                        placeholder="e.g., Bronze Tier, Gold Tier"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="tier-threshold">Spending Threshold * (SGD)</Label>
                      <Input
                        id="tier-threshold"
                        type="number"
                        min="0"
                        step="0.01"
                        value={giftTierForm.spending_threshold}
                        onChange={(e) => setGiftTierForm(prev => ({...prev, spending_threshold: parseFloat(e.target.value) || 0}))}
                        placeholder="50.00"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="tier-limit">Gift Selection Limit *</Label>
                      <Input
                        id="tier-limit"
                        type="number"
                        min="1"
                        value={giftTierForm.gift_limit}
                        onChange={(e) => setGiftTierForm(prev => ({...prev, gift_limit: parseInt(e.target.value) || 1}))}
                      />
                    </div>
                    
                    <div>
                      <Label>Available Gift Items</Label>
                      <div className="border rounded-lg p-3 max-h-40 overflow-y-auto">
                        {giftItems.map((item) => (
                          <div key={item.id} className="flex items-center space-x-2 py-2">
                            <input
                              type="checkbox"
                              checked={giftTierForm.gift_item_ids.includes(item.id)}
                              onChange={(e) => handleGiftItemSelection(item.id, e.target.checked)}
                              className="rounded"
                            />
                            <span className="text-sm">{item.name}</span>
                            <Badge variant="outline" className="ml-auto text-xs">
                              Stock: {item.stock_quantity}
                            </Badge>
                          </div>
                        ))}
                        
                        {giftItems.length === 0 && (
                          <p className="text-sm text-gray-500 text-center py-2">
                            No gift items available. Create gift items first.
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-3">
                      <Button 
                        onClick={handleCreateGiftTier}
                        disabled={!giftTierForm.name || giftTierForm.spending_threshold <= 0}
                        className="flex-1"
                      >
                        {editingTier ? 'Update' : 'Create'} Gift Tier
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => setIsTierModalOpen(false)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            {/* Gift Tiers List */}
            <div className="space-y-4">
              {giftTiers.map((tier) => (
                <Card key={tier.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-xl">{tier.name}</CardTitle>
                        <p className="text-gray-600 mt-1">
                          Spend {formatPrice(tier.spending_threshold)} or more • Select up to {tier.gift_limit} gift{tier.gift_limit > 1 ? 's' : ''}
                        </p>
                      </div>
                      <Badge variant={tier.is_active ? "default" : "secondary"}>
                        {tier.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Available Gifts ({tier.gift_items?.length || 0}):</h4>
                      <div className="flex flex-wrap gap-2">
                        {tier.gift_items?.map((gift) => (
                          <Badge key={gift.id} variant="outline" className="text-xs">
                            {gift.name}
                          </Badge>
                        )) || (
                          <span className="text-sm text-gray-500">No gifts assigned</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => openEditTierModal(tier)}
                        className="flex-1"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Edit Tier
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => handleDeleteGiftTier(tier.id)}
                        className="text-red-600 hover:text-red-700 hover:border-red-200"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {giftTiers.length === 0 && (
                <div className="text-center py-12">
                  <Award className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-500 mb-2">No Gift Tiers</h3>
                  <p className="text-gray-400 mb-4">Create spending tiers to reward your best customers with free gifts</p>
                  <Button onClick={() => {resetTierForm(); setIsTierModalOpen(true)}} className="bg-teal-600 hover:bg-teal-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Gift Tier
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GiftManagement;