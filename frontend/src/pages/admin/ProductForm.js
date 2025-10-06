import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ArrowLeft, Plus, X, Upload, Image } from 'lucide-react';

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
  
  const [newVariant, setNewVariant] = useState({
    width_cm: '',
    height_cm: '',
    size_code: '',
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
    if (isEdit) {
      fetchProduct();
    }
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `${BACKEND_URL}/api/products/${id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProduct(response.data);
    } catch (err) {
      toast.error('Failed to load product');
      navigate('/admin/products');
    } finally {
      setLoading(false);
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
      const token = localStorage.getItem('access_token');
      
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      
      const response = await axios.post(
        `${BACKEND_URL}/api/admin/upload/images`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
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

  const deleteVariant = (index, variant) => {
    const variantName = `${variant.attributes?.type || variant.type} ${variant.attributes?.color || variant.color} ${variant.attributes?.size_code || variant.size_code}`;
    
    if (!window.confirm(`Are you sure you want to delete variant "${variantName}" (SKU: ${variant.sku})? This action cannot be undone.`)) {
      return;
    }

    setProduct(prev => ({
      ...prev,
      variants: prev.variants.filter((_, i) => i !== index)
    }));
    
    toast.success(`Variant "${variantName}" removed successfully`);
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
      const token = localStorage.getItem('access_token');
      
      const payload = {
        ...product,
        seo_keywords: Array.isArray(product.seo_keywords) 
          ? product.seo_keywords 
          : product.seo_keywords.split(',').map(k => k.trim()).filter(k => k)
      };

      if (isEdit) {
        await axios.put(
          `${BACKEND_URL}/api/admin/products/${id}`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Product updated successfully');
      } else {
        await axios.post(
          `${BACKEND_URL}/api/admin/products`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Product created successfully');
      }
      
      navigate('/admin/products');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save product');
    } finally {
      setLoading(false);
    }
  };

  const colorOptions = ['white', 'pastel pink', 'champagne pink', 'milktea'];

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
                  placeholder="e.g., Premium Polymailers"
                  required
                />
              </div>
              <div>
                <Label>Category *</Label>
                <Select 
                  value={product.category} 
                  onValueChange={(value) => handleProductChange('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="polymailers">Polymailers</SelectItem>
                    <SelectItem value="accessories">Accessories</SelectItem>
                  </SelectContent>
                </Select>
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
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <Label>Type *</Label>
                  <Select 
                    value={newVariant.type} 
                    onValueChange={(value) => {
                      handleVariantChange('type', value);
                      // If bubble wrap is selected, set color to white
                      if (value === 'bubble wrap') {
                        handleVariantChange('color', 'white');
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="bubble wrap">Bubble Wrap</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label>Color *</Label>
                  <Select 
                    value={newVariant.color} 
                    onValueChange={(value) => handleVariantChange('color', value)}
                    disabled={newVariant.type === 'bubble wrap'}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {colorOptions.map(color => (
                        <SelectItem 
                          key={color} 
                          value={color}
                          disabled={newVariant.type === 'bubble wrap' && color !== 'white'}
                        >
                          {color}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {newVariant.type === 'bubble wrap' && (
                    <p className="text-xs text-gray-500 mt-1">Bubble wrap only available in white</p>
                  )}
                </div>

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

                <div className="md:col-span-3">
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
                  <Label>Initial Stock</Label>
                  <Input
                    type="number"
                    value={newVariant.on_hand}
                    onChange={(e) => handleVariantChange('on_hand', e.target.value)}
                    placeholder="0"
                  />
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
                    <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4">
                      <div>
                        <Label className="text-xs text-gray-600">Type</Label>
                        <Input
                          value={variant.attributes?.type || variant.type || ''}
                          onChange={(e) => updateVariant(index, 'type', e.target.value)}
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-gray-600">Color</Label>
                        <Input
                          value={variant.attributes?.color || variant.color || ''}
                          onChange={(e) => updateVariant(index, 'color', e.target.value)}
                          className="text-sm"
                        />
                      </div>
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
                        <Label className="text-xs text-gray-600">Stock</Label>
                        <div className="flex gap-1">
                          <Input
                            type="number"
                            value={variant.on_hand || ''}
                            onChange={(e) => updateVariant(index, 'on_hand', parseInt(e.target.value))}
                            className="text-sm"
                            placeholder="Stock"
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
                      <strong>SKU:</strong> {variant.sku}
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