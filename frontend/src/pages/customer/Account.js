import React, { useState, useEffect } from 'react';
import { User, MapPin, Package, Plus, Edit, Trash2, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { formatPrice } from '@/lib/utils';
import SmartChatWidget from '@/components/chat/SmartChatWidget';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Account = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50" data-testid="account-page">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">My Account</h1>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Profile */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center space-x-3 mb-4">
              <User className="w-8 h-8 text-teal-700" />
              <h2 className="text-xl font-semibold text-slate-900">Profile</h2>
            </div>
            <div className="space-y-2 mb-4">
              <p className="text-sm text-gray-600">Name</p>
              <p className="font-medium text-slate-900">{user?.first_name} {user?.last_name}</p>
              
              <p className="text-sm text-gray-600 mt-3">Email</p>
              <p className="font-medium text-slate-900">{user?.email}</p>
              
              {user?.phone && (
                <>
                  <p className="text-sm text-gray-600 mt-3">Phone</p>
                  <p className="font-medium text-slate-900">{user?.phone}</p>
                </>
              )}
            </div>
            <Button variant="outline" className="w-full" disabled>
              Edit Profile (Coming Soon)
            </Button>
          </div>

          {/* Orders */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center space-x-3 mb-4">
              <Package className="w-8 h-8 text-teal-700" />
              <h2 className="text-xl font-semibold text-slate-900">Orders</h2>
            </div>
            <p className="text-gray-600 mb-4">View and track all your orders</p>
            <Link to="/orders">
              <Button className="w-full bg-teal-700 hover:bg-teal-800">View Orders</Button>
            </Link>
          </div>

          {/* Settings */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center space-x-3 mb-4">
              <Settings className="w-8 h-8 text-teal-700" />
              <h2 className="text-xl font-semibold text-slate-900">Settings</h2>
            </div>
            <p className="text-gray-600 mb-4">Manage your account settings</p>
            <Button variant="outline" className="w-full" disabled>
              Settings (Coming Soon)
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Account;
