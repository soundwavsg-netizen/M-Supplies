import React, { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import SmartChatWidget from '@/components/chat/SmartChatWidget';
import SEOHead from '@/components/SEO/SEOHead';
import { faqSchema, organizationSchema } from '@/components/SEO/schemas';

const FAQ = () => {
  const [openItem, setOpenItem] = useState(null);

  const faqData = [
    {
      id: 1,
      question: "What products do you sell?",
      answer: "We specialize in premium-quality polymailers (especially thick and colourful ones) and customised packaging materials for small businesses and online sellers."
    },
    {
      id: 2,
      question: "Do you offer customised designs or logos?",
      answer: "Yes! We provide custom printing services for polymailers and packaging—perfect for adding your brand logo or design. You can email us your requirements for a quote."
    },
    {
      id: 3,
      question: "How can I place an order?",
      answer: "You can order directly through our website or through our Shopee store. We've made it easy and secure for you to shop whichever way you prefer."
    },
    {
      id: 4,
      question: "What's the delivery time?",
      answer: "Orders are usually processed within 1–2 working days. Delivery typically takes 2–5 working days depending on your location."
    },
    {
      id: 5,
      question: "Do you ship internationally?",
      answer: "Currently, we ship within Singapore and Malaysia. For bulk or overseas orders, please email us to discuss options."
    },
    {
      id: 6,
      question: "How can I contact you?",
      answer: "For any enquiries or custom requests, please email us at msuppliessg@gmail.com — we'll be happy to assist!"
    }
  ];

  const toggleItem = (id) => {
    setOpenItem(openItem === id ? null : id);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead
        title="FAQ - M Supplies Polymailers & Packaging Questions"
        description="Frequently asked questions about M Supplies polymailers, custom packaging, delivery times, international shipping to Singapore & Malaysia."
        keywords="M Supplies FAQ, polymailer questions, packaging delivery, Singapore shipping, Malaysia shipping, custom packaging FAQ, M Supplies support"
        ogImage="https://www.msupplies.sg/assets/m-supplies-logo-transparent.png"
        structuredData={faqSchema}
      />
      
      {/* Header Section */}
      <section className="bg-gradient-to-br from-teal-50 to-blue-50 py-16">
        <div className="container mx-auto px-4 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-100 rounded-full mb-6">
            <HelpCircle className="w-8 h-8 text-teal-700" />
          </div>
          <h1 className="text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
            Frequently Asked Questions
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Find answers to common questions about our products, services, and ordering process
          </p>
        </div>
      </section>

      {/* FAQ Content */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <div className="space-y-4">
              {faqData.map((item) => (
                <div key={item.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                  <Button
                    variant="ghost"
                    className="w-full p-6 text-left hover:bg-gray-50 justify-between items-center"
                    onClick={() => toggleItem(item.id)}
                  >
                    <span className="font-semibold text-slate-900 text-lg pr-4">
                      {item.question}
                    </span>
                    {openItem === item.id ? (
                      <ChevronUp className="w-5 h-5 text-teal-600 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-teal-600 flex-shrink-0" />
                    )}
                  </Button>
                  
                  {openItem === item.id && (
                    <div className="px-6 pb-6">
                      <div className="pt-4 border-t border-gray-100">
                        <p className="text-gray-700 leading-relaxed">
                          {item.answer}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Still Have Questions Section */}
            <div className="mt-16 text-center">
              <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
                <h3 className="text-2xl font-bold text-slate-900 mb-4">
                  Still have questions?
                </h3>
                <p className="text-gray-600 mb-6">
                  Can't find what you're looking for? We're here to help!
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button 
                    onClick={() => window.location.href = '/contact'}
                    className="bg-teal-600 hover:bg-teal-700"
                  >
                    Contact Us
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => window.location.href = 'mailto:msuppliessg@gmail.com'}
                  >
                    Email Us Directly
                  </Button>
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

export default FAQ;