import React, { useState } from 'react';
import { Gift, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const GiftSelection = ({ availableGifts = [], onGiftSelect }) => {
  const [selectedGifts, setSelectedGifts] = useState([]);

  if (!availableGifts || availableGifts.length === 0) {
    return null;
  }

  const handleGiftToggle = (giftId, tierLimit) => {
    const currentTierSelections = selectedGifts.filter(id => 
      availableGifts.some(tier => 
        tier.gift_items?.some(item => item.id === id) && 
        tier.gift_items?.some(item => item.id === giftId)
      )
    );

    if (selectedGifts.includes(giftId)) {
      // Remove gift
      const newSelected = selectedGifts.filter(id => id !== giftId);
      setSelectedGifts(newSelected);
      onGiftSelect(newSelected);
    } else {
      // Add gift if under limit
      if (currentTierSelections.length < tierLimit) {
        const newSelected = [...selectedGifts, giftId];
        setSelectedGifts(newSelected);
        onGiftSelect(newSelected);
      }
    }
  };

  return (
    <div className="mb-6 p-4 bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg border border-pink-200">
      <div className="flex items-center gap-2 mb-4">
        <Gift className="w-5 h-5 text-pink-600" />
        <h3 className="font-semibold text-slate-900">🎉 Congratulations! You qualify for free gifts!</h3>
      </div>

      {availableGifts.map((tier) => (
        <div key={tier.id} className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-slate-800">{tier.name}</h4>
            <Badge variant="outline" className="text-xs">
              Select up to {tier.gift_limit} gift{tier.gift_limit > 1 ? 's' : ''}
            </Badge>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
            {tier.gift_items?.map((gift) => {
              const isSelected = selectedGifts.includes(gift.id);
              const currentTierSelections = selectedGifts.filter(id => 
                tier.gift_items?.some(item => item.id === id)
              );
              const canSelect = !isSelected && currentTierSelections.length < tier.gift_limit;

              return (
                <Card 
                  key={gift.id} 
                  className={`cursor-pointer transition-all ${
                    isSelected 
                      ? 'bg-pink-100 border-pink-300 shadow-md' 
                      : canSelect 
                        ? 'hover:shadow-md hover:border-pink-200' 
                        : 'opacity-50 cursor-not-allowed'
                  }`}
                  onClick={() => canSelect || isSelected ? handleGiftToggle(gift.id, tier.gift_limit) : null}
                >
                  <CardContent className="p-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h5 className="font-medium text-sm text-slate-900 mb-1">{gift.name}</h5>
                        <p className="text-xs text-gray-600 leading-relaxed">{gift.description}</p>
                        
                        {gift.image_url && (
                          <div className="mt-2">
                            <img 
                              src={gift.image_url} 
                              alt={gift.name}
                              className="w-full h-16 object-cover rounded"
                              onError={(e) => {e.target.style.display = 'none'}}
                            />
                          </div>
                        )}
                      </div>
                      
                      {isSelected && (
                        <div className="ml-2">
                          <div className="w-6 h-6 bg-pink-600 rounded-full flex items-center justify-center">
                            <Check className="w-4 h-4 text-white" />
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      ))}

      {selectedGifts.length > 0 && (
        <div className="mt-4 p-3 bg-white rounded border border-pink-200">
          <p className="text-sm text-slate-700">
            <span className="font-medium">Selected gifts ({selectedGifts.length}):</span> Your free gifts will be included with your order!
          </p>
        </div>
      )}
    </div>
  );
};

export default GiftSelection;