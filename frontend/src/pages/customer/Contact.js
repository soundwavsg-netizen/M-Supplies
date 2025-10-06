import React from 'react';
import { Mail, Phone, MapPin } from 'lucide-react';

const Contact = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto bg-white rounded-lg p-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-6">Contact Us</h1>
          <p className="text-gray-600 mb-8">
            Have questions? We're here to help. Reach out to us through any of the channels below.
          </p>
          
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <Mail className="w-6 h-6 text-teal-700 mt-1" />
              <div>
                <h3 className="font-semibold text-slate-900 mb-1">Email</h3>
                <p className="text-gray-600">orders@polymailer.com</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <Phone className="w-6 h-6 text-teal-700 mt-1" />
              <div>
                <h3 className="font-semibold text-slate-900 mb-1">Phone</h3>
                <p className="text-gray-600">+65 9123 4567</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <MapPin className="w-6 h-6 text-teal-700 mt-1" />
              <div>
                <h3 className="font-semibold text-slate-900 mb-1">Location</h3>
                <p className="text-gray-600">Singapore</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
