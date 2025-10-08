import React from 'react';
import { Gift, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatPrice } from '@/lib/utils';

const GiftPromotion = ({ nearbyTiers = [], currentTotal }) => {
  if (!nearbyTiers || nearbyTiers.length === 0) {
    return null;
  }

  const closestTier = nearbyTiers[0];

  return (
    <div className="mb-4 p-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
          <Gift className="w-5 h-5 text-amber-600" />
        </div>
        
        <div className="flex-1">
          <h3 className="font-semibold text-slate-900 mb-1">
            🎁 You're close to earning free gifts!
          </h3>
          
          <p className="text-sm text-slate-700 mb-3">
            Spend just <span className="font-semibold text-amber-700">{formatPrice(closestTier.amount_needed)} more</span> to unlock the <span className="font-semibold">{closestTier.tier_name}</span> and choose from <span className="font-semibold">{closestTier.gift_count} free gift{closestTier.gift_count > 1 ? 's' : ''}</span>!
          </p>
          
          <div className="mb-3">
            {/* Progress bar */}
            <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-amber-400 to-orange-500 h-full transition-all duration-500"
                style={{ 
                  width: `${Math.min(95, (currentTotal / closestTier.spending_threshold) * 100)}%` 
                }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>Current: {formatPrice(currentTotal)}</span>
              <span>Goal: {formatPrice(closestTier.spending_threshold)}</span>
            </div>
          </div>
          
          {/* Show multiple nearby tiers if available */}
          {nearbyTiers.length > 1 && (
            <div className="text-xs text-gray-600">
              <p>🌟 Even more rewards ahead:</p>
              {nearbyTiers.slice(1).map((tier, index) => (
                <p key={index} className="ml-4">
                  • {tier.tier_name}: Spend {formatPrice(tier.amount_needed)} more ({tier.gift_count} gifts)
                </p>
              ))}
            </div>
          )}
        </div>
        
        <TrendingUp className="w-5 h-5 text-amber-600 flex-shrink-0" />
      </div>
    </div>
  );
};

export default GiftPromotion;