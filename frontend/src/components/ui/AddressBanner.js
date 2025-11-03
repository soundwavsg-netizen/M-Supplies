import React, { useState, useEffect } from 'react';
import { MapPin, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useFirebaseAuth } from '@/context/FirebaseAuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AddressBanner = () => {
  const { userProfile } = useFirebaseAuth();
  const navigate = useNavigate();
  const [showBanner, setShowBanner] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      checkUserHasDefaultAddress();
    }
  }, [user]);

  const checkUserHasDefaultAddress = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/users/me/addresses/default`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // If we get here, user has a default address
      setShowBanner(false);
    } catch (error) {
      // 404 means no default address found
      if (error.response?.status === 404) {
        // Check if banner was dismissed this session
        const dismissed = sessionStorage.getItem('address-banner-dismissed');
        if (!dismissed) {
          setShowBanner(true);
        }
      }
    }
  };

  const handleAddAddress = () => {
    setIsLoading(true);
    navigate('/account?onboard=address');
  };

  const dismissBanner = () => {
    setShowBanner(false);
    sessionStorage.setItem('address-banner-dismissed', 'true');
  };

  if (!showBanner || !user) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-teal-50 to-blue-50 border border-teal-200">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MapPin className="w-5 h-5 text-teal-600 flex-shrink-0" />
            <div>
              <p className="text-slate-900 font-medium">
                Add your default delivery address to speed up checkout.
              </p>
              <p className="text-sm text-gray-600">
                Save time on future orders by adding your shipping details now.
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              onClick={handleAddAddress}
              disabled={isLoading}
              className="bg-teal-600 hover:bg-teal-700 text-white"
              size="sm"
            >
              {isLoading ? 'Loading...' : 'Add Address'}
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={dismissBanner}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddressBanner;