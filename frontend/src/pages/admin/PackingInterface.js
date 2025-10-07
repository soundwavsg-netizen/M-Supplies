import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Search, Plus, Minus, Package, AlertTriangle, RotateCcw } from 'lucide-react';
import { adminInventoryAPI } from '@/lib/api';

const PackingInterface = () => {
  const [inventory, setInventory] = useState([]);
  const [filteredInventory, setFilteredInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [colorFilter, setColorFilter] = useState('all');
  const [sizeFilter, setSizeFilter] = useState('all');
  const [recentChanges, setRecentChanges] = useState(new Set());
  
  // Available filters
  const [categories, setCategories] = useState([]);
  const [colors, setColors] = useState([]);
  const [sizes, setSizes] = useState([]);

  useEffect(() => {
    fetchInventory();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [inventory, selectedCategory, searchTerm, colorFilter, sizeFilter]);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const response = await adminInventoryAPI.list();
      setInventory(response.data);
      
      // Extract filter options
      const uniqueCategories = [...new Set(response.data.map(item => item.product_name.split(' - ')[0]))];
      const uniqueColors = [...new Set(response.data.map(item => {
        const color = item.sku.split('_')[2] || 'Unknown';
        return color.replace(/([A-Z])/g, ' $1').trim().toLowerCase();
      }))];
      const uniqueSizes = [...new Set(response.data.map(item => {
        const sizePart = item.sku.split('_')[3] || 'Unknown';
        return sizePart;
      }))];
      
      setCategories(uniqueCategories);
      setColors(uniqueColors);
      setSizes(uniqueSizes);
      
    } catch (error) {
      toast.error('Failed to load inventory');
      console.error('Inventory fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...inventory];
    
    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(item => 
        item.product_name.toLowerCase().includes(selectedCategory.toLowerCase())
      );
    }
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.sku.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Color filter
    if (colorFilter !== 'all') {
      filtered = filtered.filter(item => {
        const color = item.sku.split('_')[2] || '';
        return color.toLowerCase().includes(colorFilter.toLowerCase());
      });
    }
    
    // Size filter
    if (sizeFilter !== 'all') {
      filtered = filtered.filter(item => {
        const size = item.sku.split('_')[3] || '';
        return size.includes(sizeFilter);
      });
    }
    
    setFilteredInventory(filtered);
  };

  const adjustStock = async (variantId, change, currentStock) => {
    const newStock = Math.max(0, currentStock + change);
    
    try {
      const adjustmentData = {
        variant_id: variantId,
        adjustment_type: 'set',
        on_hand_value: newStock,
        reason: 'manual_adjustment',
        notes: `Packing adjustment: ${change > 0 ? '+' : ''}${change} (Packing Interface)`
      };

      await adminInventoryAPI.adjust(adjustmentData);
      
      // Update local state
      setInventory(prev => 
        prev.map(item => 
          item.variant_id === variantId 
            ? { ...item, on_hand: newStock, available: Math.max(0, newStock - item.allocated - item.safety_stock) }
            : item
        )
      );
      
      // Add to recent changes for highlighting
      setRecentChanges(prev => new Set([...prev, variantId]));
      setTimeout(() => {
        setRecentChanges(prev => {
          const newSet = new Set(prev);
          newSet.delete(variantId);
          return newSet;
        });
      }, 2000);
      
      // Show feedback toast
      const action = change > 0 ? 'increased' : 'decreased';
      toast.success(`Stock ${action}: ${Math.abs(change)} unit${Math.abs(change) !== 1 ? 's' : ''}`, {
        duration: 1500
      });
      
    } catch (error) {
      toast.error('Failed to update stock');
      console.error('Stock adjustment error:', error);
    }
  };

  const getCardColor = (item) => {
    if (recentChanges.has(item.variant_id)) {
      return 'ring-2 ring-green-400 bg-green-50';
    }
    if (item.on_hand <= item.safety_stock) {
      return 'ring-2 ring-red-400 bg-red-50';
    }
    if (item.on_hand <= item.safety_stock + 5) {
      return 'ring-2 ring-yellow-400 bg-yellow-50';
    }
    return 'ring-1 ring-gray-200 bg-white hover:ring-gray-300';
  };

  const formatProductInfo = (item) => {
    const skuParts = item.sku.split('_');
    const rawColor = skuParts[2] || '';
    const size = skuParts[3] || '';
    const packSize = skuParts[4] || '';
    
    // Consistent color formatting: handle camelCase and convert to proper case
    const color = rawColor
      .replace(/([A-Z])/g, ' $1')  // Add space before capital letters
      .trim()                       // Remove extra spaces
      .toLowerCase()                // Convert to lowercase
      .split(' ')                   // Split into words
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))  // Capitalize each word
      .join(' ');                   // Join back together
    
    return {
      color: color,
      size: size.replace('x', ' × '),
      packSize: packSize || '0'  // Ensure pack size is always shown
    };
  };

  const clearAllFilters = () => {
    setSelectedCategory('all');
    setSearchTerm('');
    setColorFilter('all');
    setSizeFilter('all');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Package className="w-12 h-12 text-teal-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading packing interface...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-full mx-auto px-4 py-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Package className="w-8 h-8 text-teal-600" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Real-Time Packing Interface</h1>
              <p className="text-sm text-gray-600">Quick inventory adjustments • {filteredInventory.length} items</p>
            </div>
          </div>
          <Button 
            variant="outline" 
            onClick={fetchInventory}
            className="flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Refresh
          </Button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg p-4 mb-6 shadow-sm">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            {/* Search */}
            <div className="md:col-span-2 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search products or SKU..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Category Filter */}
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger>
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map(cat => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {/* Color Filter */}
            <Select value={colorFilter} onValueChange={setColorFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Color" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Colors</SelectItem>
                {colors.map(color => (
                  <SelectItem key={color} value={color} className="capitalize">{color}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {/* Size Filter */}
            <Select value={sizeFilter} onValueChange={setSizeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Size" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sizes</SelectItem>
                {sizes.map(size => (
                  <SelectItem key={size} value={size}>{size.replace('x', ' × ')}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {/* Clear Filters */}
            <Button 
              variant="outline" 
              onClick={clearAllFilters}
              className="flex items-center gap-2"
            >
              Clear All
            </Button>
          </div>
        </div>

        {/* Inventory Grid - 6x6 layout for iPad landscape */}
        <div className="grid grid-cols-6 gap-3">
          {filteredInventory.slice(0, 36).map((item) => {
            const productInfo = formatProductInfo(item);
            const isLowStock = item.on_hand <= item.safety_stock;
            const isWarningStock = item.on_hand <= item.safety_stock + 5 && !isLowStock;
            
            return (
              <div
                key={item.variant_id}
                className={`relative rounded-lg p-3 transition-all duration-200 ${getCardColor(item)}`}
                style={{
                  backgroundImage: item.product_image ? `url(${item.product_image})` : 'none',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  backgroundRepeat: 'no-repeat'
                }}
              >
                {/* Overlay for readability */}
                <div className="absolute inset-0 bg-white bg-opacity-90 rounded-lg"></div>
                
                {/* Content */}
                <div className="relative z-10">
                  {/* Stock Status Badges */}
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex gap-1">
                      {isLowStock && (
                        <Badge variant="destructive" className="text-xs px-1">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Low
                        </Badge>
                      )}
                      {isWarningStock && (
                        <Badge variant="secondary" className="text-xs px-1 bg-yellow-100 text-yellow-800">
                          Warning
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {/* Product Info */}
                  <div className="text-center mb-3">
                    <p className="text-sm font-semibold text-gray-900 leading-tight">{productInfo.color}</p>
                    <p className="text-xs text-gray-600">{productInfo.size}</p>
                    {productInfo.packSize && productInfo.packSize !== '0' && (
                      <p className="text-xs text-gray-500">{productInfo.packSize} pcs</p>
                    )}
                  </div>
                  
                  {/* Stock Display */}
                  <div className="text-center mb-3">
                    <div className="text-lg font-bold text-gray-900">{item.available}</div>
                    <div className="text-xs text-gray-500">available</div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => adjustStock(item.variant_id, -1, item.on_hand)}
                      disabled={item.on_hand <= 0}
                      className="flex-1 h-8 p-0 hover:bg-red-50 hover:border-red-300"
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline" 
                      size="sm"
                      onClick={() => adjustStock(item.variant_id, 1, item.on_hand)}
                      className="flex-1 h-8 p-0 hover:bg-green-50 hover:border-green-300"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Load More Indicator */}
        {filteredInventory.length > 36 && (
          <div className="text-center mt-6 p-4 bg-white rounded-lg">
            <p className="text-gray-600">
              Showing first 36 of {filteredInventory.length} items. 
              Use filters to find specific products.
            </p>
          </div>
        )}
        
        {/* No Results */}
        {filteredInventory.length === 0 && (
          <div className="text-center py-12">
            <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your filters or search terms</p>
            <Button onClick={clearAllFilters}>Clear All Filters</Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PackingInterface;