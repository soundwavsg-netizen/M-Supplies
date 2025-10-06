import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Upload, X, Plus, Trash2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ProductForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'Polymailers',
    images: [],
    seo_title: '',
    seo_description: '',
    is_active: true,
    featured: false
  });

  const [variants, setVariants] = useState([
    {
      sku: '',
      attributes: {
        size: '',
        thickness: '60 micron',
        color: ''
      },
      price_tiers: [
        { min_quantity: 1, price: 0 }
      ],
      on_hand: 0,
      safety_stock: 5,
      low_stock_threshold: 10
    }
  ]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleImageUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    try {
      setUploading(true);
      const token = localStorage.getItem('access_token');
      
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post(
          `${BACKEND_URL}/api/admin/upload/image`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            }
          }
        );
        
        setFormData(prev => ({
          ...prev,
          images: [...prev.images, `${BACKEND_URL}${response.data.url}`]
        }));
      }
      
      toast.success('Images uploaded successfully');
    } catch (error) {
      toast.error('Failed to upload images');
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const removeImage = (index) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const addVariant = () => {
    setVariants([
      ...variants,
      {
        sku: '',
        attributes: { size: '', thickness: '60 micron', color: '' },
        price_tiers: [{ min_quantity: 1, price: 0 }],
        on_hand: 0,
        safety_stock: 5,
        low_stock_threshold: 10
      }
    ]);
  };

  const removeVariant = (index) => {
    setVariants(variants.filter((_, i) => i !== index));
  };

  const updateVariant = (index, field, value) => {
    const updated = [...variants];
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      updated[index][parent][child] = value;
    } else {
      updated[index][field] = value;
    }
    setVariants(updated);
  };

  const addPriceTier = (variantIndex) => {
    const updated = [...variants];
    updated[variantIndex].price_tiers.push({ min_quantity: 1, price: 0 });
    setVariants(updated);
  };

  const updatePriceTier = (variantIndex, tierIndex, field, value) => {
    const updated = [...variants];
    updated[variantIndex].price_tiers[tierIndex][field] = parseFloat(value) || 0;
    setVariants(updated);
  };

  const removePriceTier = (variantIndex, tierIndex) => {
    const updated = [...variants];
    updated[variantIndex].price_tiers = updated[variantIndex].price_tiers.filter((_, i) => i !== tierIndex);
    setVariants(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (variants.length === 0 || !variants[0].sku) {
      toast.error('Please add at least one variant with SKU');
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const payload = {
        ...formData,
        variants: variants.map(v => ({
          ...v,
          on_hand: parseInt(v.on_hand) || 0,
          allocated: 0,
          safety_stock: parseInt(v.safety_stock) || 5,
          low_stock_threshold: parseInt(v.low_stock_threshold) || 10,
          channel_buffers: { website: 0, shopee: 2 }
        }))
      };

      await axios.post(
        `${BACKEND_URL}/api/admin/products`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Product created successfully!');
      navigate('/admin/products');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create product');
      console.error('Create error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className=\"min-h-screen bg-gray-50\" data-testid=\"product-form-page\">
      <div className=\"container mx-auto px-4 py-8 max-w-4xl\">
        <h1 className=\"text-3xl font-bold text-slate-900 mb-8\">Add New Product</h1>

        <form onSubmit={handleSubmit} className=\"space-y-6\">
          {/* Basic Info */}
          <div className=\"bg-white rounded-lg p-6 shadow-sm\">
            <h2 className=\"text-xl font-semibold text-slate-900 mb-4\">Basic Information</h2>
            <div className=\"space-y-4\">
              <div>
                <Label htmlFor=\"name\">Product Name *</Label>
                <Input
                  id=\"name\"
                  name=\"name\"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  data-testid=\"product-name\"
                />
              </div>

              <div>
                <Label htmlFor=\"description\">Description *</Label>
                <Textarea
                  id=\"description\"
                  name=\"description\"
                  value={formData.description}
                  onChange={handleChange}
                  rows={4}
                  required
                />
              </div>

              <div>
                <Label htmlFor=\"category\">Category</Label>
                <Input
                  id=\"category\"
                  name=\"category\"
                  value={formData.category}
                  onChange={handleChange}
                />
              </div>

              <div className=\"flex gap-4\">
                <label className=\"flex items-center space-x-2\">
                  <input
                    type=\"checkbox\"
                    name=\"is_active\"
                    checked={formData.is_active}
                    onChange={handleChange}
                    className=\"rounded\"
                  />
                  <span>Active</span>
                </label>
                <label className=\"flex items-center space-x-2\">
                  <input
                    type=\"checkbox\"
                    name=\"featured\"
                    checked={formData.featured}
                    onChange={handleChange}
                    className=\"rounded\"
                  />
                  <span>Featured</span>
                </label>
              </div>
            </div>
          </div>

          {/* Images */}
          <div className=\"bg-white rounded-lg p-6 shadow-sm\">
            <h2 className=\"text-xl font-semibold text-slate-900 mb-4\">Product Images</h2>
            
            <div className=\"grid grid-cols-2 md:grid-cols-4 gap-4 mb-4\">
              {formData.images.map((img, idx) => (
                <div key={idx} className=\"relative aspect-square rounded-lg overflow-hidden border-2 border-gray-200\">
                  <img src={img} alt=\"\" className=\"w-full h-full object-cover\" />
                  <button
                    type=\"button\"
                    onClick={() => removeImage(idx)}
                    className=\"absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600\"
                  >
                    <X className=\"w-4 h-4\" />
                  </button>
                </div>
              ))}
              
              <label className=\"aspect-square rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-teal-500 transition\">
                <Upload className=\"w-8 h-8 text-gray-400 mb-2\" />
                <span className=\"text-sm text-gray-600\">Upload Image</span>
                <input
                  type=\"file\"
                  accept=\"image/*\"
                  multiple
                  onChange={handleImageUpload}
                  className=\"hidden\"
                  disabled={uploading}
                />
              </label>
            </div>
            {uploading && <p className=\"text-sm text-gray-600\">Uploading...</p>}
          </div>

          {/* Variants */}
          <div className=\"bg-white rounded-lg p-6 shadow-sm\">
            <div className=\"flex items-center justify-between mb-4\">
              <h2 className=\"text-xl font-semibold text-slate-900\">Variants & Stock</h2>
              <Button type=\"button\" onClick={addVariant} variant=\"outline\" size=\"sm\">
                <Plus className=\"w-4 h-4 mr-2\" /> Add Variant
              </Button>
            </div>

            {variants.map((variant, vIdx) => (
              <div key={vIdx} className=\"border rounded-lg p-4 mb-4 relative\">
                {variants.length > 1 && (
                  <button
                    type=\"button\"
                    onClick={() => removeVariant(vIdx)}
                    className=\"absolute top-2 right-2 text-red-500 hover:text-red-700\"
                  >
                    <Trash2 className=\"w-5 h-5\" />
                  </button>
                )}

                <h3 className=\"font-semibold mb-3\">Variant {vIdx + 1}</h3>
                
                <div className=\"grid md:grid-cols-2 gap-4 mb-4\">
                  <div>
                    <Label>SKU *</Label>
                    <Input
                      value={variant.sku}
                      onChange={(e) => updateVariant(vIdx, 'sku', e.target.value)}
                      placeholder=\"PM-25X35-PINK-50\"
                      required
                    />
                  </div>
                  <div>
                    <Label>Size *</Label>
                    <Input
                      value={variant.attributes.size}
                      onChange={(e) => updateVariant(vIdx, 'attributes.size', e.target.value)}
                      placeholder=\"25cm x 35cm\"
                      required
                    />
                  </div>
                  <div>
                    <Label>Color *</Label>
                    <Input
                      value={variant.attributes.color}
                      onChange={(e) => updateVariant(vIdx, 'attributes.color', e.target.value)}
                      placeholder=\"Pink\"
                      required
                    />
                  </div>
                  <div>
                    <Label>Thickness</Label>
                    <Input
                      value={variant.attributes.thickness}
                      onChange={(e) => updateVariant(vIdx, 'attributes.thickness', e.target.value)}
                      placeholder=\"60 micron\"
                    />
                  </div>
                </div>

                <div className=\"grid md:grid-cols-3 gap-4 mb-4\">
                  <div>
                    <Label>On Hand Stock *</Label>
                    <Input
                      type=\"number\"
                      value={variant.on_hand}
                      onChange={(e) => updateVariant(vIdx, 'on_hand', e.target.value)}
                      min=\"0\"
                      required
                    />
                  </div>
                  <div>
                    <Label>Safety Stock</Label>
                    <Input
                      type=\"number\"
                      value={variant.safety_stock}
                      onChange={(e) => updateVariant(vIdx, 'safety_stock', e.target.value)}
                      min=\"0\"
                    />
                  </div>
                  <div>
                    <Label>Low Stock Alert</Label>
                    <Input
                      type=\"number\"
                      value={variant.low_stock_threshold}
                      onChange={(e) => updateVariant(vIdx, 'low_stock_threshold', e.target.value)}
                      min=\"0\"
                    />
                  </div>
                </div>

                <div>
                  <div className=\"flex items-center justify-between mb-2\">
                    <Label>Price Tiers *</Label>
                    <Button
                      type=\"button\"
                      onClick={() => addPriceTier(vIdx)}
                      variant=\"outline\"
                      size=\"sm\"
                    >
                      <Plus className=\"w-3 h-3 mr-1\" /> Add Tier
                    </Button>
                  </div>
                  
                  {variant.price_tiers.map((tier, tIdx) => (
                    <div key={tIdx} className=\"flex gap-2 mb-2\">
                      <div className=\"flex-1\">
                        <Input
                          type=\"number\"
                          value={tier.min_quantity}
                          onChange={(e) => updatePriceTier(vIdx, tIdx, 'min_quantity', e.target.value)}
                          placeholder=\"Min Qty\"
                          min=\"1\"
                        />
                      </div>
                      <div className=\"flex-1\">
                        <Input
                          type=\"number\"
                          step=\"0.01\"
                          value={tier.price}
                          onChange={(e) => updatePriceTier(vIdx, tIdx, 'price', e.target.value)}
                          placeholder=\"Price\"
                          min=\"0\"
                        />
                      </div>
                      {variant.price_tiers.length > 1 && (
                        <Button
                          type=\"button\"
                          onClick={() => removePriceTier(vIdx, tIdx)}
                          variant=\"ghost\"
                          size=\"sm\"
                        >
                          <X className=\"w-4 h-4\" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className=\"flex gap-4\">
            <Button
              type=\"submit\"
              className=\"bg-teal-700 hover:bg-teal-800\"
              disabled={loading}
              data-testid=\"submit-product\"
            >
              {loading ? 'Creating...' : 'Create Product'}
            </Button>
            <Button
              type=\"button\"
              variant=\"outline\"
              onClick={() => navigate('/admin/products')}
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
