import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ArrowLeft, Plus, X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ProductForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = !!id;
  
  const [loading, setLoading] = useState(false);
  const [product, setProduct] = useState({
    name: '',
    description: '',
    category: 'polymailers',
    specifications: {},
    seo_title: '',
    seo_description: '',
    seo_keywords: [],
    variants: []
  });
  
  const [newVariant, setNewVariant] = useState({
    type: 'normal',
    color: 'white',
    width_cm: '',
    height_cm: '',
    size_code: '',
    price: '',
    on_hand: '',
    safety_stock: 0
  });

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

  const addVariant = () => {
    if (!newVariant.width_cm || !newVariant.height_cm || !newVariant.price) {
      toast.error('Please fill all required variant fields');
      return;
    }

    const variant = {
      ...newVariant,
      variant_id: `var_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      sku: `${product.category.toUpperCase()}_${newVariant.type.toUpperCase()}_${newVariant.color.toUpperCase()}_${newVariant.size_code}`,
      width_cm: parseInt(newVariant.width_cm),
      height_cm: parseInt(newVariant.height_cm),
      price: parseFloat(newVariant.price),
      on_hand: parseInt(newVariant.on_hand) || 0,
      safety_stock: parseInt(newVariant.safety_stock) || 0
    };

    setProduct(prev => ({
      ...prev,
      variants: [...prev.variants, variant]
    }));

    // Reset form
    setNewVariant({
      type: 'normal',
      color: 'white',
      width_cm: '',
      height_cm: '',
      size_code: '',
      price: '',
      on_hand: '',
      safety_stock: 0
    });
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
      toast.error(error.response?.data?.detail || 'Failed to save product');
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
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="e.g., Premium Polymailers"
                  required
                />
              </div>
              <div>
                <Label>Category *</Label>
                <Select 
                  value={product.category} 
                  onValueChange={(value) => handleInputChange('category', value)}
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
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
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

                <div>
                  <Label>Price ($) *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={newVariant.price}
                    onChange={(e) => handleVariantChange('price', e.target.value)}
                    placeholder="0.00"
                  />
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
                <h3 className="font-medium text-slate-900">Current Variants</h3>
                {product.variants.map((variant, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1 grid grid-cols-1 md:grid-cols-6 gap-2 text-sm">
                      <span><strong>Type:</strong> {variant.type}</span>
                      <span><strong>Color:</strong> {variant.color}</span>
                      <span><strong>Size:</strong> {variant.width_cm}×{variant.height_cm} cm</span>
                      <span><strong>Price:</strong> ${variant.price}</span>
                      <span><strong>Stock:</strong> {variant.on_hand}</span>
                      <span><strong>SKU:</strong> {variant.sku}</span>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => removeVariant(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </Button>
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