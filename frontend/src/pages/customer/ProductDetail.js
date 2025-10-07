import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ShoppingCart, Check, Truck, Shield } from 'lucide-react';
import { productsAPI } from '@/lib/api';
import { useCart } from '@/context/CartContext';
import { formatPrice } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.get(id);
      const productData = response.data;
      setProduct(productData);
      if (productData.variants?.length > 0) {
        setSelectedVariant(productData.variants[0]);
      }
    } catch (error) {
      console.error('Error fetching product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!selectedVariant) return;
    try {
      setAdding(true);
      await addToCart(selectedVariant.id, quantity);
      navigate('/cart');
    } catch (error) {
      console.error('Error adding to cart:', error);
    } finally {
      setAdding(false);
    }
  };

  const getPrice = () => {
    if (!selectedVariant) return 0;
    const tier = selectedVariant.price_tiers.find(t => quantity >= t.min_quantity) || 
                 selectedVariant.price_tiers[selectedVariant.price_tiers.length - 1];
    return tier.price * quantity;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-700"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Product not found</h2>
          <Button onClick={() => navigate('/products')}>Back to Products</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="product-detail-page">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          <div className="grid md:grid-cols-2 gap-8 p-8">
            {/* Images */}
            <div>
              <div className="aspect-square rounded-xl overflow-hidden bg-gray-100 mb-4">
                <img
                  src={product.images[selectedImage] || 'https://via.placeholder.com/600'}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              </div>
              {product.images.length > 1 && (
                <div className="grid grid-cols-4 gap-2">
                  {product.images.map((img, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedImage(idx)}
                      className={`aspect-square rounded-lg overflow-hidden border-2 ${
                        selectedImage === idx ? 'border-teal-700' : 'border-transparent'
                      }`}
                    >
                      <img src={img} alt="" className="w-full h-full object-cover" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="space-y-6">
              <div>
                <Badge>{product.category}</Badge>
                <h1 className="text-3xl font-bold text-slate-900 mt-3" data-testid="product-name">{product.name}</h1>
                <p className="text-gray-600 mt-3 leading-relaxed">{product.description}</p>
              </div>

              {/* Specifications */}
              {product.specifications && Object.keys(product.specifications).length > 0 && (
                <div className="bg-slate-50 rounded-lg p-4">
                  <h3 className="font-semibold text-slate-900 mb-3">Specifications</h3>
                  <dl className="grid grid-cols-2 gap-3">
                    {Object.entries(product.specifications).map(([key, value]) => (
                      <div key={key}>
                        <dt className="text-sm text-gray-600 capitalize">{key.replace('_', ' ')}</dt>
                        <dd className="text-sm font-medium text-slate-900">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}

              {/* Variant Selection */}
              {product.variants && product.variants.length > 0 && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Variant
                    </label>
                    <Select
                      value={selectedVariant?.id}
                      onValueChange={(val) => {
                        const variant = product.variants.find(v => v.id === val);
                        setSelectedVariant(variant);
                      }}
                    >
                      <SelectTrigger data-testid="variant-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {product.variants.map((variant) => {
                          const size = variant.attributes?.size_code || `${variant.attributes?.width_cm}x${variant.attributes?.height_cm}cm`;
                          const packSize = variant.attributes?.pack_size || variant.pack_size || 50;
                          const isOutOfStock = (variant.on_hand || variant.stock_qty || 0) === 0;
                          
                          return (
                            <SelectItem key={variant.id} value={variant.id}>
                              {size} - {packSize} {product.type === 'bubble wrap' ? 'pieces' : 'pcs/pack'}
                              {isOutOfStock && ' (Out of Stock)'}
                            </SelectItem>
                          );
                        })}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Quantity */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quantity
                    </label>
                    <Select value={quantity.toString()} onValueChange={(val) => setQuantity(parseInt(val))}>
                      <SelectTrigger data-testid="quantity-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {[1, 2, 3, 5, 10, 20].map((qty) => (
                          <SelectItem key={qty} value={qty.toString()}>
                            {qty}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              {/* Price */}
              <div className="border-t border-b py-4">
                <div className="flex items-baseline justify-between">
                  <span className="text-gray-600">Total Price:</span>
                  <span className="text-3xl font-bold text-teal-700" data-testid="total-price">
                    {formatPrice(getPrice())}
                  </span>
                </div>
                {selectedVariant && selectedVariant.price_tiers.length > 1 && (
                  <p className="text-sm text-gray-500 mt-2">Bulk discounts available</p>
                )}
              </div>

              {/* Add to Cart */}
              <Button
                size="lg"
                className="w-full bg-teal-700 hover:bg-teal-800"
                onClick={handleAddToCart}
                disabled={!selectedVariant || (selectedVariant.on_hand || selectedVariant.stock_qty || 0) === 0 || adding}
                data-testid="add-to-cart-button"
              >
                {adding ? (
                  'Adding...'
                ) : selectedVariant?.stock_qty === 0 ? (
                  'Out of Stock'
                ) : (
                  <>
                    <ShoppingCart className="mr-2 w-5 h-5" />
                    Add to Cart
                  </>
                )}
              </Button>

              {/* Features */}
              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Truck className="w-5 h-5 text-teal-700" />
                  <span>Fast Delivery</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Shield className="w-5 h-5 text-teal-700" />
                  <span>Quality Guaranteed</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
