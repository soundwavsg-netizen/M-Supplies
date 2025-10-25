import React, { useState } from 'react';
import { Mail, Send, MapPin, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import SmartChatWidget from '@/components/chat/SmartChatWidget';
import SEOHead from '@/components/SEO/SEOHead';
import { organizationSchema, contactSchema } from '@/components/SEO/schemas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.message) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setIsSubmitting(true);
      
      // Send to backend API
      const response = await fetch(`${BACKEND_URL}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message || 'Thanks for reaching out! We\'ll reply soon.');
        setFormData({ name: '', email: '', message: '' });
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to send message. Please try again.');
      }
      
    } catch (error) {
      console.error('Contact form error:', error);
      toast.error('Failed to send message. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead
        title="Contact M Supplies - Custom Packaging Enquiries Singapore"
        description="Contact M Supplies for custom packaging solutions, bulk orders, and enquiries. Email msuppliessg@gmail.com. Serving Singapore & Malaysia."
        keywords="contact M Supplies, custom packaging enquiry, bulk packaging orders, Singapore packaging supplier, Malaysia shipping, packaging consultation"
        ogImage="https://www.msupplies.sg/assets/m-supplies-logo-transparent.png"
        structuredData={organizationSchema}
      />
      
      {/* Header Section */}
      <section className="bg-gradient-to-br from-teal-50 to-blue-50 py-16">
        <div className="container mx-auto px-4 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-100 rounded-full mb-6">
            <Mail className="w-8 h-8 text-teal-700" />
          </div>
          <h1 className="text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
            Get in Touch
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Have a question or need a custom packaging quote?
          </p>
        </div>
      </section>

      {/* Content Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12">
              
              {/* Contact Information */}
              <div className="space-y-8">
                <Card className="bg-white shadow-sm">
                  <CardContent className="p-8">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6">Contact Information</h2>
                    
                    <div className="space-y-6">
                      <div className="flex items-start space-x-4">
                        <Mail className="w-6 h-6 text-teal-700 mt-1 flex-shrink-0" />
                        <div>
                          <h3 className="font-semibold text-slate-900 mb-1">Email Us</h3>
                          <p className="text-gray-600 mb-2">msuppliessg@gmail.com</p>
                          <p className="text-sm text-gray-500">We'll get back to you as soon as possible — we love hearing from you!</p>
                        </div>
                      </div>
                      
                      <div className="flex items-start space-x-4">
                        <MapPin className="w-6 h-6 text-teal-700 mt-1 flex-shrink-0" />
                        <div>
                          <h3 className="font-semibold text-slate-900 mb-1">Location</h3>
                          <p className="text-gray-600">Singapore</p>
                          <p className="text-sm text-gray-500">Serving Singapore and Malaysia</p>
                        </div>
                      </div>
                      
                      <div className="flex items-start space-x-4">
                        <Clock className="w-6 h-6 text-teal-700 mt-1 flex-shrink-0" />
                        <div>
                          <h3 className="font-semibold text-slate-900 mb-1">Response Time</h3>
                          <p className="text-gray-600">Usually within 24 hours</p>
                          <p className="text-sm text-gray-500">We respond to all enquiries promptly</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Map Placeholder */}
                <Card className="bg-white shadow-sm">
                  <CardContent className="p-8">
                    <h3 className="font-semibold text-slate-900 mb-4">Our Location</h3>
                    <div className="bg-gray-100 rounded-lg h-48 flex items-center justify-center">
                      <div className="text-center">
                        <MapPin className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-500">Singapore</p>
                        <p className="text-sm text-gray-400">Map integration coming soon</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Contact Form */}
              <div>
                <Card className="bg-white shadow-sm">
                  <CardContent className="p-8">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6">Send us a Message</h2>
                    
                    <form onSubmit={handleSubmit} className="space-y-6">
                      <div>
                        <Label htmlFor="name">Name *</Label>
                        <Input
                          id="name"
                          name="name"
                          value={formData.name}
                          onChange={handleChange}
                          placeholder="Your full name"
                          required
                          className="mt-1"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="email">Email *</Label>
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleChange}
                          placeholder="your.email@example.com"
                          required
                          className="mt-1"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="message">Message *</Label>
                        <Textarea
                          id="message"
                          name="message"
                          value={formData.message}
                          onChange={handleChange}
                          placeholder="Tell us about your packaging needs, custom requirements, or any questions you have..."
                          rows={5}
                          required
                          className="mt-1"
                        />
                      </div>
                      
                      <Button 
                        type="submit" 
                        disabled={isSubmitting}
                        className="w-full bg-teal-600 hover:bg-teal-700"
                      >
                        {isSubmitting ? 'Sending...' : (
                          <>
                            <Send className="w-4 h-4 mr-2" />
                            Send Message
                          </>
                        )}
                      </Button>
                    </form>
                    
                    <div className="mt-6 p-4 bg-teal-50 border border-teal-200 rounded-lg">
                      <p className="text-sm text-teal-800">
                        <strong>Quick response guaranteed!</strong> We typically respond to all enquiries within 24 hours.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </section>

      <SmartChatWidget />
    </div>
  );
};

export default Contact;
