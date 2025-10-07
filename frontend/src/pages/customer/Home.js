import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Package, Truck, Shield, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { theme } from '@/theme.config';
import SmartChatWidget from '@/components/chat/SmartChatWidget';

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-teal-50 via-white to-orange-50 py-20 lg:py-32 overflow-hidden" data-testid="hero-section">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="inline-block">
                <span className="bg-teal-100 text-teal-800 px-4 py-2 rounded-full text-sm font-medium">
                  Premium Quality Polymailers
                </span>
              </div>
              <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
                Ship with Confidence
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed">
                Durable, waterproof polymailers in vibrant colors. Bulk discounts available. Fast Singapore delivery.
              </p>
              <div className="flex flex-wrap gap-4">
                <Link to="/products">
                  <Button size="lg" className="bg-teal-700 hover:bg-teal-800 text-white" data-testid="shop-now-button">
                    Shop Now
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link to="/about">
                  <Button size="lg" variant="outline">
                    Learn More
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-teal-100 to-orange-100 p-8 shadow-2xl">
                <img
                  src="https://images.unsplash.com/photo-1586864387634-1e3c3e1a8c6b?w=800&q=80"
                  alt="Polymailer bags"
                  className="w-full h-full object-cover rounded-xl"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Why Choose Us?</h2>
            <p className="text-xl text-gray-600">Quality products, exceptional service</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<Package className="w-8 h-8 text-teal-700" />}
              title="Premium Quality"
              description="Made from durable LDPE material with strong sealing"
            />
            <FeatureCard
              icon={<Truck className="w-8 h-8 text-teal-700" />}
              title="Fast Delivery"
              description="Quick shipping across Singapore"
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8 text-teal-700" />}
              title="Waterproof"
              description="Keeps contents safe from moisture"
            />
            <FeatureCard
              icon={<Sparkles className="w-8 h-8 text-teal-700" />}
              title="Bulk Discounts"
              description="Save more when you buy more"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-teal-700 to-teal-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Get Started?</h2>
          <p className="text-xl mb-8 text-teal-100 max-w-2xl mx-auto">
            Browse our collection of premium polymailers and find the perfect fit for your business.
          </p>
          <Link to="/products">
            <Button size="lg" className="bg-white text-teal-700 hover:bg-gray-100" data-testid="browse-products-button">
              Browse Products
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
        </div>
      </section>
      <SmartChatWidget />
    </div>
  );
};

const FeatureCard = ({ icon, title, description }) => {
  return (
    <div className="bg-slate-50 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="bg-white w-16 h-16 rounded-lg flex items-center justify-center mb-4 shadow-sm">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
};

export default Home;
