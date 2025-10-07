import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ArrowLeft, Plus, X, Upload, Image, Trash2 } from 'lucide-react';
import { adminProductsAPI, productsAPI, adminUploadAPI, adminSettingsAPI } from '@/lib/api';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ProductForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = !!id;
  
  const [loading, setLoading] = useState(false);
  const [imageUploading, setImageUploading] = useState(false);
  const [product, setProduct] = useState({
    name: '',
    description: '',
    category: 'polymailers',
    color: 'white', // Color is now at product level
    type: 'normal', // Type is also at product level
    specifications: {},
    seo_title: '',
    seo_description: '',
    seo_keywords: [],
    images: [],
    variants: []
  });

  // Dynamic options management - Initialize with safe defaults
  const [availableColors, setAvailableColors] = useState(['white', 'black', 'clear']);
  const [availableTypes, setAvailableTypes] = useState(['normal', 'bubble wrap']);
  const [availableCategories, setAvailableCategories] = useState(['polymailers', 'accessories']);
  const [availablePackSizes, setAvailablePackSizes] = useState([25, 50, 100, 500, 1000]);
  const [availablePieceQuantities, setAvailablePieceQuantities] = useState([1, 5, 10, 25, 50, 100]);
  const [showAddColor, setShowAddColor] = useState(false);
  const [showAddType, setShowAddType] = useState(false);
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [newColorName, setNewColorName] = useState('');
  const [newTypeName, setNewTypeName] = useState('');
  const [newCategoryName, setNewCategoryName] = useState('');
  
  const [newVariant, setNewVariant] = useState({
    width_cm: '',
    height_cm: '',
    size_code: '',
    pack_size: 50, // Default pack size
    price_tiers: [
      { min_quantity: 25, price: '' },
      { min_quantity: 50, price: '' },
      { min_quantity: 100, price: '' }
    ],
    on_hand: '',
    safety_stock: 0
  });

  // Get pricing tiers based on product name/category
  const getPricingTiers = () => {
    const isAccessory = product.category === 'accessories';
    const isPremiumPolymailer = product.name.toLowerCase().includes('premium') && product.category === 'polymailers';
    
    if (isAccessory) {
      return [{ min_quantity: 1, price: '' }]; // Accessories sold individually
    } else if (isPremiumPolymailer) {
      return [
        { min_quantity: 50, price: '' },
        { min_quantity: 100, price: '' }
      ]; // Premium polymailers: 50 and 100 pcs only
    } else {
      return [
        { min_quantity: 25, price: '' },
        { min_quantity: 50, price: '' },
        { min_quantity: 100, price: '' }
      ]; // Regular polymailers: 25, 50, 100 pcs
    }
  };

  useEffect(() => {
    fetchSettings();
    if (isEdit) {
      fetchProduct();
    }
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.get(id);
      setProduct(response.data);
    } catch (err) {
      console.error('Failed to load product:', err);
      toast.error('Failed to load product');
      navigate('/admin/products');
    } finally {
      setLoading(false);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await adminSettingsAPI.get();
      const settings = response.data;
      
      // Set available colors, types, and categories from settings
      if (settings.available_colors && Array.isArray(settings.available_colors)) {
        setAvailableColors(settings.available_colors.filter(c => typeof c === 'string'));
      }
      if (settings.available_types && Array.isArray(settings.available_types)) {
        setAvailableTypes(settings.available_types.filter(t => typeof t === 'string'));
      }
      if (settings.available_categories && Array.isArray(settings.available_categories)) {
        setAvailableCategories(settings.available_categories.filter(cat => typeof cat === 'string'));
      }
      if (settings.available_pack_sizes && Array.isArray(settings.available_pack_sizes)) {
        setAvailablePackSizes(settings.available_pack_sizes.filter(size => typeof size === 'number'));
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
      // Don't show error toast for settings as it's not critical
      // Set default values if settings fail to load
      setAvailableColors(['white', 'black', 'clear']);
      setAvailableTypes(['normal', 'premium', 'bubble wrap']);
      setAvailableCategories(['polymailers', 'accessories']);
      setAvailablePackSizes([25, 50, 100, 500, 1000]);
    }
  };

  const updateSettings = async (colors, types, categories) => {
    try {
      // Get current settings first
      const response = await adminSettingsAPI.get();
      const currentSettings = response.data;
      
      // Update with new colors, types, and categories
      const updatedSettings = {
        ...currentSettings,
        available_colors: colors,
        available_types: types,
        available_categories: categories
      };
      
      await adminSettingsAPI.update(updatedSettings);
    } catch (err) {
      console.error('Failed to update settings:', err);
      toast.error('Failed to save changes');
    }
  };

  const handleInputChange = (field, value) => {
    setProduct(prev => ({ ...prev, [field]: value }));
  };

  const handleVariantChange = (field, value) => {
    setNewVariant(prev => ({ ...prev, [field]: value }));
    
    // Auto-generate size_code when width/height changes
    if (field === 'width_cm' || field === 'height_cm') {
      const width = field === 'width_cm' ? value : newVariant.width_cm;
      const height = field === 'height_cm' ? value : newVariant.height_cm;
      if (width && height) {
        setNewVariant(prev => ({ ...prev, size_code: `${width}x${height}` }));
      }
    }
  };

  // Update pricing tiers when product name or category changes
  const handleProductChange = (field, value) => {
    setProduct(prev => ({ ...prev, [field]: value }));
    
    // Reset variant pricing tiers based on product type
    if (field === 'name' || field === 'category') {
      const newProduct = { ...product, [field]: value };
      const isAccessory = newProduct.category === 'accessories';
      const isPremiumPolymailer = newProduct.name.toLowerCase().includes('premium') && newProduct.category === 'polymailers';
      
      let newPriceTiers;
      if (isAccessory) {
        newPriceTiers = [{ min_quantity: 1, price: '' }];
      } else if (isPremiumPolymailer) {
        newPriceTiers = [
          { min_quantity: 50, price: '' },
          { min_quantity: 100, price: '' }
        ];
      } else {
        newPriceTiers = [
          { min_quantity: 25, price: '' },
          { min_quantity: 50, price: '' },
          { min_quantity: 100, price: '' }
        ];
      }
      
      setNewVariant(prev => ({ ...prev, price_tiers: newPriceTiers }));
    }
  };

  const handlePriceTierChange = (tierIndex, price) => {
    setNewVariant(prev => ({
      ...prev,
      price_tiers: prev.price_tiers.map((tier, index) => 
        index === tierIndex ? { ...tier, price: price } : tier
      )
    }));
  };

  // Image upload handlers
  const handleImageUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    try {
      setImageUploading(true);
      
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      
      const response = await adminUploadAPI.images(formData);
      
      const newImageUrls = response.data.urls;
      setProduct(prev => ({
        ...prev,
        images: [...prev.images, ...newImageUrls]
      }));
      
      toast.success(`${newImageUrls.length} image(s) uploaded successfully`);
    } catch (err) {
      toast.error('Failed to upload images');
    } finally {
      setImageUploading(false);
    }
  };

  const removeImage = (index) => {
    setProduct(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const addVariant = () => {
    if (!newVariant.width_cm || !newVariant.height_cm) {
      toast.error('Please fill width and height fields');
      return;
    }
    
    // Check if at least the first price tier has a price
    if (!newVariant.price_tiers[0].price) {
      toast.error('Please set at least the base price (25 pcs)');
      return;
    }

    // Filter out empty price tiers and convert to numbers
    const validPriceTiers = newVariant.price_tiers
      .filter(tier => tier.price && tier.price !== '')
      .map(tier => ({
        min_quantity: parseInt(tier.min_quantity),
        price: parseFloat(tier.price)
      }));

    if (validPriceTiers.length === 0) {
      toast.error('Please set at least one price tier');
      return;
    }

    const variant = {
      ...newVariant,
      variant_id: `var_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      sku: `${product.category.toUpperCase()}_${product.type.toUpperCase()}_${product.color.toUpperCase()}_${newVariant.size_code}`,
      width_cm: parseInt(newVariant.width_cm),
      height_cm: parseInt(newVariant.height_cm),
      price_tiers: validPriceTiers,
      on_hand: parseInt(newVariant.on_hand) || 0,
      safety_stock: parseInt(newVariant.safety_stock) || 0
    };

    setProduct(prev => ({
      ...prev,
      variants: [...prev.variants, variant]
    }));

    // Reset form (no color/type since they're at product level)
    const newPriceTiers = getPricingTiers();
    setNewVariant({
      width_cm: '',
      height_cm: '',
      size_code: '',
      price_tiers: newPriceTiers,
      on_hand: '',
      safety_stock: 0
    });
  };

  const updateVariant = (index, field, value) => {
    setProduct(prev => ({
      ...prev,
      variants: prev.variants.map((variant, i) => {
        if (i === index) {
          if (field === 'price') {
            // Update price in price_tiers structure
            const updatedVariant = { ...variant };
            if (!updatedVariant.price_tiers) {
              updatedVariant.price_tiers = [{ min_quantity: 1, price: value }];
            } else {
              updatedVariant.price_tiers = updatedVariant.price_tiers.map((tier, tierIndex) => 
                tierIndex === 0 ? { ...tier, price: value } : tier
              );
            }
            return updatedVariant;
          } else if (['type', 'color', 'width_cm', 'height_cm'].includes(field)) {
            // Update attributes
            const updatedVariant = { ...variant };
            if (!updatedVariant.attributes) {
              updatedVariant.attributes = {};
            }
            updatedVariant.attributes = { ...updatedVariant.attributes, [field]: value };
            
            // Also update size_code if width or height changes
            if (field === 'width_cm' || field === 'height_cm') {
              const width = field === 'width_cm' ? value : updatedVariant.attributes.width_cm;
              const height = field === 'height_cm' ? value : updatedVariant.attributes.height_cm;
              if (width && height) {
                updatedVariant.attributes.size_code = `${width}x${height}`;
              }
            }
            
            return updatedVariant;
          } else {
            // Update direct properties (like on_hand, safety_stock)
            return { ...variant, [field]: value };
          }
        }
        return variant;
      })
    }));
  };

  // Color and Type management functions
  const addNewColor = async () => {
    if (!newColorName.trim()) {
      toast.error('Please enter a color name');
      return;
    }
    
    const colorName = newColorName.trim().toLowerCase();
    if (availableColors.includes(colorName)) {
      toast.error('Color already exists');
      return;
    }
    
    const newColors = [...availableColors, colorName];
    setAvailableColors(newColors);
    setProduct(prev => ({ ...prev, color: colorName }));
    setNewColorName('');
    setShowAddColor(false);
    
    // Save to backend
    await updateSettings(newColors, availableTypes, availableCategories);
    toast.success(`Color "${colorName}" added successfully`);
  };

  const deleteColor = async (colorToDelete) => {
    if (colorToDelete === product.color) {
      toast.error('Cannot delete the currently selected color');
      return;
    }
    
    if (!window.confirm(`Are you sure you want to delete color "${colorToDelete}"?`)) {
      return;
    }
    
    const newColors = availableColors.filter(color => color !== colorToDelete);
    setAvailableColors(newColors);
    
    // Save to backend
    await updateSettings(newColors, availableTypes, availableCategories);
    toast.success(`Color "${colorToDelete}" deleted`);
  };

  const addNewType = async () => {
    if (!newTypeName.trim()) {
      toast.error('Please enter a type name');
      return;
    }
    
    const typeName = newTypeName.trim().toLowerCase();
    if (availableTypes.includes(typeName)) {
      toast.error('Type already exists');
      return;
    }
    
    const newTypes = [...availableTypes, typeName];
    setAvailableTypes(newTypes);
    setProduct(prev => ({ ...prev, type: typeName }));
    setNewTypeName('');
    setShowAddType(false);
    
    // Save to backend
    await updateSettings(availableColors, newTypes, availableCategories);
    toast.success(`Type "${typeName}" added successfully`);
  };

  const deleteType = async (typeToDelete) => {
    if (typeToDelete === product.type) {
      toast.error('Cannot delete the currently selected type');
      return;
    }
    
    if (!window.confirm(`Are you sure you want to delete type "${typeToDelete}"?`)) {
      return;
    }
    
    const newTypes = availableTypes.filter(type => type !== typeToDelete);
    setAvailableTypes(newTypes);
    
    // Save to backend
    await updateSettings(availableColors, newTypes, availableCategories);
    toast.success(`Type "${typeToDelete}" deleted`);
  };

  const addNewCategory = async () => {
    if (!newCategoryName.trim()) {
      toast.error('Please enter a category name');
      return;
    }
    
    const categoryName = newCategoryName.trim().toLowerCase();
    if (availableCategories.includes(categoryName)) {
      toast.error('Category already exists');
      return;
    }
    
    const newCategories = [...availableCategories, categoryName];
    setAvailableCategories(newCategories);
    setProduct(prev => ({ ...prev, category: categoryName }));
    setNewCategoryName('');
    setShowAddCategory(false);
    
    // Save to backend
    await updateSettings(availableColors, availableTypes, newCategories);
    toast.success(`Category "${categoryName}" added successfully`);
  };

  const deleteCategory = async (categoryToDelete) => {
    if (categoryToDelete === product.category) {
      toast.error('Cannot delete the currently selected category');
      return;
    }
    
    if (!window.confirm(`Are you sure you want to delete category "${categoryToDelete}"?`)) {
      return;
    }
    
    const newCategories = availableCategories.filter(category => category !== categoryToDelete);
    setAvailableCategories(newCategories);
    
    // Save to backend
    await updateSettings(availableColors, availableTypes, newCategories);
    toast.success(`Category "${categoryToDelete}" deleted`);
  };

  // Fixed variant deletion function
  const deleteVariant = (index, variant) => {
    console.log('Delete variant called with:', { index, variant }); // Debug log
    
    try {
      const width = variant.attributes?.width_cm || variant.width_cm || 'Unknown';
      const height = variant.attributes?.height_cm || variant.height_cm || 'Unknown';
      const dimensions = `${width}×${height}cm`;
      const sku = variant.sku || 'Unknown SKU';
      const variantName = `${product.color} ${product.type} ${dimensions}`;
      
      console.log('Attempting to delete variant:', variantName); // Debug log
      
      const confirmMessage = `Are you sure you want to delete variant "${variantName}" (SKU: ${sku})?\n\nThis action cannot be undone.`;
      
      if (!window.confirm(confirmMessage)) {
        console.log('User cancelled deletion'); // Debug log
        return;
      }

      console.log('User confirmed deletion, removing variant at index:', index); // Debug log

      setProduct(prev => {
        const newVariants = prev.variants.filter((_, i) => i !== index);
        console.log('Variants before:', prev.variants.length, 'Variants after:', newVariants.length);
        return {
          ...prev,
          variants: newVariants
        };
      });
      
      toast.success(`Variant "${dimensions}" removed successfully`);
      console.log('Variant deletion completed'); // Debug log
      
    } catch (error) {
      console.error('Error in deleteVariant:', error);
      toast.error('Failed to delete variant');
    }
  };

  const removeVariant = (index) => {
    setProduct(prev => ({
      ...prev,
      variants: prev.variants.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (product.variants.length === 0) {
      toast.error('Please add at least one variant');
      return;
    }

    try {
      setLoading(true);
      
      const payload = {
        ...product,
        seo_keywords: Array.isArray(product.seo_keywords) 
          ? product.seo_keywords 
          : product.seo_keywords.split(',').map(k => k.trim()).filter(k => k)
      };

      if (isEdit) {
        await adminProductsAPI.update(id, payload);
        toast.success('Product updated successfully');
      } else {
        await adminProductsAPI.create(payload);
        toast.success('Product created successfully');
      }
      
      navigate('/admin/products');
    } catch (err) {
      console.error('Product save error:', err);
      toast.error(err.response?.data?.detail || 'Failed to save product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="flex items-center mb-6">
          <Button 
            variant="outline" 
            onClick={() => navigate('/admin/products')}
            className="mr-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Products
          </Button>
          <h1 className="text-3xl font-bold text-slate-900">
            {isEdit ? 'Edit Product' : 'Create New Product'}
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Product Name *</Label>
                <Input
                  value={product.name}
                  onChange={(e) => handleProductChange('name', e.target.value)}
                  placeholder="e.g., Premium Polymailer - White"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">Include color in product name (e.g., "Premium Polymailer - White")</p>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Category *</Label>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAddCategory(true)}
                    className="h-8 px-2 text-xs"
                  >
                    <Plus className="w-3 h-3 mr-1" />
                    Add Category
                  </Button>
                </div>
                
                {showAddCategory ? (
                  <div className="flex gap-2 mb-2">
                    <Input
                      placeholder="Enter new category name"
                      value={newCategoryName}
                      onChange={(e) => setNewCategoryName(e.target.value)}
                      className="flex-1"
                    />
                    <Button type="button" variant="default" onClick={addNewCategory} size="sm">Add</Button>
                    <Button type="button" variant="outline" onClick={() => setShowAddCategory(false)} size="sm">Cancel</Button>
                  </div>
                ) : null}
                
                <Select 
                  value={product.category} 
                  onValueChange={(value) => handleProductChange('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.isArray(availableCategories) && availableCategories.map(category => {
                      const categoryStr = typeof category === 'string' ? category : String(category || '');
                      if (!categoryStr) return null;
                      return (
                        <SelectItem key={categoryStr} value={categoryStr}>
                          <span className="capitalize">{categoryStr.replace(/([a-z])([A-Z])/g, '$1 $2')}</span>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
                
                {/* Category Management */}
                {Array.isArray(availableCategories) && availableCategories.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="text-xs text-gray-500">Manage categories:</span>
                    {availableCategories.map(category => {
                      const categoryStr = typeof category === 'string' ? category : String(category || '');
                      if (!categoryStr) return null;
                      return (
                        <div key={categoryStr} className="flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs">
                          <span className="capitalize">{categoryStr.replace(/([a-z])([A-Z])/g, '$1 $2')}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteCategory(categoryStr)}
                            className="h-4 w-4 p-0 text-red-500 hover:text-red-700"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Color *</Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowAddColor(true)}
                    className="text-teal-600 hover:text-teal-700"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Color
                  </Button>
                </div>
                
                {showAddColor ? (
                  <div className="flex gap-2 mb-2">
                    <Input
                      value={newColorName}
                      onChange={(e) => setNewColorName(e.target.value)}
                      placeholder="Enter color name"
                      onKeyPress={(e) => e.key === 'Enter' && addNewColor()}
                    />
                    <Button type="button" onClick={addNewColor} size="sm">Add</Button>
                    <Button type="button" variant="outline" onClick={() => setShowAddColor(false)} size="sm">Cancel</Button>
                  </div>
                ) : null}
                
                <Select 
                  value={product.color} 
                  onValueChange={(value) => handleProductChange('color', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.isArray(availableColors) && availableColors.map(color => {
                      const colorStr = typeof color === 'string' ? color : String(color || '');
                      if (!colorStr) return null;
                      return (
                        <SelectItem key={colorStr} value={colorStr} className="capitalize">
                          {colorStr}
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
                
                {/* Color Management */}
                {Array.isArray(availableColors) && availableColors.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="text-xs text-gray-500">Manage colors:</span>
                    {availableColors.map(color => {
                      const colorStr = typeof color === 'string' ? color : String(color || '');
                      if (!colorStr) return null;
                      return (
                        <div key={colorStr} className="flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs">
                          <span className="capitalize">{colorStr}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteColor(colorStr)}
                            className="h-4 w-4 p-0 text-red-500 hover:text-red-700"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Type *</Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowAddType(true)}
                    className="text-teal-600 hover:text-teal-700"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Type
                  </Button>
                </div>
                
                {showAddType ? (
                  <div className="flex gap-2 mb-2">
                    <Input
                      value={newTypeName}
                      onChange={(e) => setNewTypeName(e.target.value)}
                      placeholder="Enter type name"
                      onKeyPress={(e) => e.key === 'Enter' && addNewType()}
                    />
                    <Button type="button" onClick={addNewType} size="sm">Add</Button>
                    <Button type="button" variant="outline" onClick={() => setShowAddType(false)} size="sm">Cancel</Button>
                  </div>
                ) : null}
                
                <Select 
                  value={product.type} 
                  onValueChange={(value) => {
                    handleProductChange('type', value);
                    // Business rule: bubble wrap only in white
                    if (value === 'bubble wrap') {
                      handleProductChange('color', 'white');
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.isArray(availableTypes) && availableTypes.map(type => {
                      const typeStr = typeof type === 'string' ? type : String(type || '');
                      if (!typeStr) return null;
                      return (
                        <SelectItem key={typeStr} value={typeStr} className="capitalize">
                          {typeStr}
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
                {product.type === 'bubble wrap' && (
                  <p className="text-xs text-amber-600 mt-1">⚠️ Bubble wrap only available in white</p>
                )}
                
                {/* Type Management */}
                {Array.isArray(availableTypes) && availableTypes.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="text-xs text-gray-500">Manage types:</span>
                    {availableTypes.map(type => {
                      const typeStr = typeof type === 'string' ? type : String(type || '');
                      if (!typeStr) return null;
                      return (
                        <div key={typeStr} className="flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs">
                          <span className="capitalize">{typeStr}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteType(typeStr)}
                            className="h-4 w-4 p-0 text-red-500 hover:text-red-700"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
            <div className="mt-4">
              <Label>Description</Label>
              <Textarea
                value={product.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Product description..."
                rows={3}
              />
            </div>
          </div>

          {/* Product Images */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Product Images</h2>
            
            {/* Image Upload */}
            <div className="mb-4">
              <Label>Upload Images</Label>
              <div className="mt-2">
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="w-8 h-8 mb-4 text-gray-500" />
                    <p className="mb-2 text-sm text-gray-500">
                      <span className="font-semibold">Click to upload</span> product images
                    </p>
                    <p className="text-xs text-gray-500">PNG, JPG up to 10MB each</p>
                  </div>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                    disabled={imageUploading}
                    className="hidden"
                  />
                </label>
              </div>
              {imageUploading && (
                <p className="text-sm text-blue-600 mt-2">Uploading images...</p>
              )}
            </div>

            {/* Current Images */}
            {product.images.length > 0 && (
              <div>
                <Label>Current Images ({product.images.length})</Label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                  {product.images.map((imageUrl, index) => (
                    <div key={index} className="relative group">
                      <img
                        src={imageUrl}
                        alt={`Product image ${index + 1}`}
                        className="w-full h-24 object-cover rounded border"
                      />
                      <button
                        type="button"
                        onClick={() => removeImage(index)}
                        className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* SEO */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">SEO</h2>
            <div className="space-y-4">
              <div>
                <Label>SEO Title</Label>
                <Input
                  value={product.seo_title}
                  onChange={(e) => handleInputChange('seo_title', e.target.value)}
                  placeholder="SEO title for search engines"
                />
              </div>
              <div>
                <Label>SEO Description</Label>
                <Textarea
                  value={product.seo_description}
                  onChange={(e) => handleInputChange('seo_description', e.target.value)}
                  placeholder="SEO description for search engines"
                  rows={2}
                />
              </div>
              <div>
                <Label>SEO Keywords</Label>
                <Input
                  value={Array.isArray(product.seo_keywords) ? product.seo_keywords.join(', ') : product.seo_keywords}
                  onChange={(e) => handleInputChange('seo_keywords', e.target.value)}
                  placeholder="keyword1, keyword2, keyword3"
                />
              </div>
            </div>
          </div>

          {/* Variants */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Product Variants</h2>
            
            {/* Add New Variant */}
            <div className="border rounded-lg p-4 mb-4 bg-gray-50">
              <h3 className="font-medium text-slate-900 mb-3">Add New Variant</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <Label>Width (cm) *</Label>
                  <Input
                    type="number"
                    value={newVariant.width_cm}
                    onChange={(e) => handleVariantChange('width_cm', e.target.value)}
                    placeholder="25"
                  />
                </div>

                <div>
                  <Label>Height (cm) *</Label>
                  <Input
                    type="number"
                    value={newVariant.height_cm}
                    onChange={(e) => handleVariantChange('height_cm', e.target.value)}
                    placeholder="35"
                  />
                </div>

                <div>
                  <Label>Size Code</Label>
                  <Input
                    value={newVariant.size_code}
                    onChange={(e) => handleVariantChange('size_code', e.target.value)}
                    placeholder="Auto-generated"
                    readOnly
                  />
                </div>

                <div>
                  <Label>Pack Size (pcs) *</Label>
                  <Select 
                    value={newVariant.pack_size?.toString()} 
                    onValueChange={(value) => handleVariantChange('pack_size', parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {availablePackSizes.map(size => (
                        <SelectItem key={size} value={size.toString()}>
                          {size} pieces per pack
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="md:col-span-2">
                  <Label>Pricing Tiers *</Label>
                  <div className={`grid gap-2 mt-2 ${newVariant.price_tiers.length === 1 ? 'grid-cols-1' : newVariant.price_tiers.length === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
                    {newVariant.price_tiers.map((tier, index) => (
                      <div key={tier.min_quantity}>
                        <Label className="text-xs text-gray-600">
                          {tier.min_quantity === 1 ? 'Each ($)' : `${tier.min_quantity} pcs ($)`}
                        </Label>
                        <Input
                          type="number"
                          step="0.01"
                          value={tier.price}
                          onChange={(e) => handlePriceTierChange(index, e.target.value)}
                          placeholder="0.00"
                        />
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {product.category === 'accessories' 
                      ? 'Accessories sold individually' 
                      : product.name.toLowerCase().includes('premium')
                        ? 'Premium polymailers: Minimum 50 pcs with volume discount at 100+ pcs'
                        : 'Regular polymailers: Minimum 25 pcs with volume discounts'
                    }
                  </p>
                </div>

                <div>
                  <Label>Initial Stock (packs)</Label>
                  <Input
                    type="number"
                    value={newVariant.on_hand}
                    onChange={(e) => handleVariantChange('on_hand', e.target.value)}
                    placeholder="0"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Number of packs in stock (each pack = {newVariant.pack_size || 50} pieces)
                  </p>
                </div>

                <div>
                  <Label>Safety Stock</Label>
                  <Input
                    type="number"
                    value={newVariant.safety_stock}
                    onChange={(e) => handleVariantChange('safety_stock', e.target.value)}
                    placeholder="0"
                  />
                </div>
              </div>
              
              <Button 
                type="button" 
                onClick={addVariant}
                className="mt-4 bg-teal-700 hover:bg-teal-800"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Variant
              </Button>
            </div>

            {/* Existing Variants */}
            {product.variants.length > 0 && (
              <div className="space-y-2">
                <h3 className="font-medium text-slate-900">Current Variants - Click to Edit</h3>
                {product.variants.map((variant, index) => (
                  <div key={variant.id || index} className="p-4 border rounded-lg bg-white">
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                      <div>
                        <Label className="text-xs text-gray-600">Width (cm)</Label>
                        <Input
                          type="number"
                          value={variant.attributes?.width_cm || variant.width_cm || ''}
                          onChange={(e) => updateVariant(index, 'width_cm', parseInt(e.target.value))}
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-gray-600">Height (cm)</Label>
                        <Input
                          type="number"
                          value={variant.attributes?.height_cm || variant.height_cm || ''}
                          onChange={(e) => updateVariant(index, 'height_cm', parseInt(e.target.value))}
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-gray-600">Pack Size</Label>
                        <Select 
                          value={(variant.pack_size || 50).toString()} 
                          onValueChange={(value) => updateVariant(index, 'pack_size', parseInt(value))}
                        >
                          <SelectTrigger className="text-sm">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {availablePackSizes.map(size => (
                              <SelectItem key={size} value={size.toString()}>
                                {size} pcs
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label className="text-xs text-gray-600">Price ($)</Label>
                        <Input
                          type="number"
                          step="0.01"
                          value={variant.price_tiers?.[0]?.price || variant.price || ''}
                          onChange={(e) => updateVariant(index, 'price', parseFloat(e.target.value))}
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-gray-600">Stock (packs)</Label>
                        <div className="flex gap-1">
                          <Input
                            type="number"
                            value={variant.on_hand || ''}
                            onChange={(e) => updateVariant(index, 'on_hand', parseInt(e.target.value))}
                            className="text-sm"
                            placeholder="Packs"
                            title={`Total pieces: ${(variant.on_hand || 0) * (variant.pack_size || 50)}`}
                          />
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => deleteVariant(index, variant)}
                            className="text-red-600 hover:text-red-700 px-2"
                            title="Delete this variant"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      <strong>SKU:</strong> {variant.sku} | <strong>Product Color:</strong> {product.color} | <strong>Type:</strong> {product.type}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <Button 
              type="submit" 
              className="bg-teal-700 hover:bg-teal-800"
              disabled={loading}
            >
              {loading ? 'Saving...' : (isEdit ? 'Update Product' : 'Create Product')}
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => navigate('/admin/products')}
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductForm;