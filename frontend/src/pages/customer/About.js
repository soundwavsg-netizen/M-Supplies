import React from 'react';
import { ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import SmartChatWidget from '@/components/chat/SmartChatWidget';
import SEOHead from '@/components/SEO/SEOHead';
import { organizationSchema } from '@/components/SEO/schemas';

const About = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead
        title="M Supplies - Premium Polymailers & Custom Packaging Singapore"
        description="Founded 2021. Premium polymailers, custom packaging solutions for Singapore & Malaysia businesses. Rainbow Palace, M Supplies, Mossom SG Studio brands."
        keywords="M Supplies Singapore, premium polymailers, custom packaging, bubble wrap polymailers, online seller packaging, Singapore packaging, Malaysia shipping, Rainbow Palace, Mossom SG Studio"
        ogImage="https://www.msupplies.sg/assets/m-supplies-logo-transparent.png"
        structuredData={organizationSchema}
      />
      
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 1.2s ease-out forwards;
        }
      `}</style>
      
      {/* New Homepage Banner */}
      <section className="bg-gradient-to-r from-teal-50 via-orange-50 to-pink-50 py-16 lg:py-20">
        <div className="container mx-auto px-4">
          <div className="text-center animate-fade-in">
            <h1 className="text-4xl lg:text-6xl font-bold text-slate-900 mb-4 leading-tight">
              🌈 Premium Polymailers. Custom Packaging. Made with Care.
            </h1>
            <p className="text-xl lg:text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              Discover the colors, quality, and creativity that make M Supplies stand out from the crowd!
            </p>
          </div>
        </div>
      </section>

      {/* Hero Section with Banner */}
      <section className="bg-gradient-to-br from-teal-50 to-orange-50 py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <img
              src="https://images.unsplash.com/photo-1586864387634-1e3c3e1a8c6b?w=1200&q=80"
              alt="M Supplies packaging products"
              className="w-full h-64 object-cover rounded-2xl shadow-lg mb-8"
              onError={(e) => {e.target.style.display = 'none'}}
            />
            <h1 className="text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
              Welcome to M Supplies (INT) Pte Ltd
            </h1>
            <p className="text-xl text-gray-600">
              Premium packaging solutions since 2021
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl p-8 lg:p-12 shadow-sm">
              <div className="prose prose-lg max-w-none">
                <p className="text-gray-700 text-lg leading-relaxed mb-6">
                  Founded in 2021, M Supplies began as a small Shopee store with a simple mission: to provide premium-quality packaging materials that help small businesses and online sellers stand out. Over the years, we've grown into a multi-faceted company, combining quality, creativity, and customer care across different segments.
                </p>
                
                <p className="text-gray-700 text-lg leading-relaxed mb-8">
                  Our journey started online, and we're excited to now offer a seamless shopping experience through our official website, making it easier than ever for customers to explore and order our products.
                </p>

                <h2 className="text-3xl font-bold text-slate-900 mb-8">Our Business Segments</h2>
                
                {/* Business Segments */}
                <div className="grid lg:grid-cols-3 gap-8 not-prose">
                  {/* Rainbow Palace */}
                  <div className="bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl p-6 border border-pink-100">
                    <div className="text-3xl mb-3">🌈</div>
                    <h3 className="text-xl font-bold text-slate-900 mb-3">Rainbow Palace</h3>
                    <p className="text-gray-700 mb-4">
                      Our Shopee store specializing in vibrant, high-quality polymailers and other essential packaging materials. Perfect for businesses that want their shipments to leave a lasting impression.
                    </p>
                    <Button 
                      variant="outline" 
                      className="w-full border-pink-300 text-pink-700 hover:bg-pink-50"
                      onClick={() => window.open('https://shopee.sg/rainbowpalace', '_blank')}
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Visit our store
                    </Button>
                  </div>

                  {/* M Supplies Main */}
                  <div className="bg-gradient-to-br from-teal-50 to-blue-50 rounded-xl p-6 border border-teal-100">
                    <div className="text-3xl mb-3">📦</div>
                    <h3 className="text-xl font-bold text-slate-900 mb-3">M Supplies</h3>
                    <p className="text-gray-700 mb-4">
                      Our main brand offering thick polymailers, customised packaging, and branding solutions tailored for online sellers and small businesses. We focus on quality, durability, and style.
                    </p>
                    <Button 
                      variant="outline" 
                      className="w-full border-teal-300 text-teal-700 hover:bg-teal-50"
                      onClick={() => window.open('https://shopee.sg/msupplies', '_blank')}
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Visit our store
                    </Button>
                  </div>

                  {/* Mossom SG Studio */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
                    <div className="text-3xl mb-3">🌿</div>
                    <h3 className="text-xl font-bold text-slate-900 mb-3">Mossom SG Studio</h3>
                    <p className="text-gray-700 mb-4">
                      Our creative studio bringing bespoke floral arrangements and styling services to life. From personal gifts to event styling, we combine artistry and emotion to craft memorable experiences.
                    </p>
                    <Button 
                      variant="outline" 
                      className="w-full border-green-300 text-green-700 hover:bg-green-50"
                      onClick={() => window.open('https://instagram.com/mossomsg', '_blank')}
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      @mossomsg
                    </Button>
                  </div>
                </div>

                <div className="mt-12 p-8 bg-gradient-to-r from-teal-50 to-orange-50 rounded-xl border border-teal-100">
                  <h3 className="text-2xl font-bold text-slate-900 mb-4">Our Commitment</h3>
                  <p className="text-gray-700 text-lg leading-relaxed">
                    At M Supplies, we are committed to more than just products — we strive to provide a premium and excellent experience in every interaction. Whether it's helping your brand shine with quality packaging or creating unforgettable floral designs, we put care, attention, and creativity at the heart of everything we do.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <SmartChatWidget />
    </div>
  );
};

export default About;
