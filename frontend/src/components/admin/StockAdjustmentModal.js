import React, { useState } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const StockAdjustmentModal = ({ variant, onClose, onSuccess }) => {
  const [adjustmentType, setAdjustmentType] = useState('change');
  const [stockType, setStockType] = useState('on_hand'); // New: on_hand or allocated
  const [value, setValue] = useState(0);
  const [reason, setReason] = useState('manual_adjustment');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!notes.trim()) {
      toast.error('Please provide notes for this adjustment');
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const payload = {
        variant_id: variant.variant_id,
        adjustment_type: adjustmentType,
        reason,
        notes: notes.trim()
      };

      if (adjustmentType === 'set') {
        payload.on_hand_value = parseInt(value);
      } else {
        payload.on_hand_change = parseInt(value);
      }

      await axios.post(
        `${BACKEND_URL}/api/admin/inventory/adjust`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Stock adjusted successfully');
      onSuccess();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to adjust stock');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="stock-adjustment-modal">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-slate-900">Adjust Stock</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-4 p-3 bg-gray-50 rounded">
          <p className="text-sm text-gray-600">SKU: <span className="font-medium text-slate-900">{variant.sku}</span></p>
          <p className="text-sm text-gray-600">Current Stock: <span className="font-medium text-teal-700">{variant.on_hand}</span></p>
          <p className="text-sm text-gray-600">Available: <span className="font-medium text-teal-700">{variant.available}</span></p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Adjustment Type</Label>
            <Select value={adjustmentType} onValueChange={setAdjustmentType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="change">Change (Add/Remove)</SelectItem>
                <SelectItem value="set">Set Exact Value</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>{adjustmentType === 'set' ? 'New Stock Level' : 'Change Amount'}</Label>
            <Input
              type="number"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={adjustmentType === 'set' ? 'e.g., 100' : 'e.g., +50 or -10'}
              required
            />
            {adjustmentType === 'change' && (
              <p className="text-xs text-gray-500 mt-1">
                Use positive numbers to add, negative to remove
              </p>
            )}
          </div>

          <div>
            <Label>Reason</Label>
            <Select value={reason} onValueChange={setReason}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="manual_adjustment">Manual Adjustment</SelectItem>
                <SelectItem value="purchase_received">Purchase Received</SelectItem>
                <SelectItem value="customer_return">Customer Return</SelectItem>
                <SelectItem value="damaged">Damaged</SelectItem>
                <SelectItem value="lost">Lost</SelectItem>
                <SelectItem value="found">Found</SelectItem>
                <SelectItem value="recount">Recount</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Notes *</Label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Explain the reason for this adjustment..."
              rows={3}
              required
            />
          </div>

          <div className="flex gap-2 pt-2">
            <Button
              type="submit"
              className="flex-1 bg-teal-700 hover:bg-teal-800"
              disabled={loading}
              data-testid="submit-adjustment"
            >
              {loading ? 'Adjusting...' : 'Adjust Stock'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
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

export default StockAdjustmentModal;
