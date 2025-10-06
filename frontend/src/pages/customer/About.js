import React from 'react';

const About = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto bg-white rounded-lg p-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-6">About PolyMailer</h1>
          <div className="prose prose-lg">
            <p className="text-gray-600 mb-4">
              PolyMailer is Singapore's trusted supplier of premium polymailer bags for e-commerce businesses.
            </p>
            <p className="text-gray-600 mb-4">
              We provide high-quality, waterproof, and tear-resistant polymailers in various sizes and colors,
              perfect for shipping your products safely and professionally.
            </p>
            <h2 className="text-2xl font-bold text-slate-900 mt-8 mb-4">Why Choose Us?</h2>
            <ul className="list-disc pl-6 space-y-2 text-gray-600">
              <li>Premium LDPE material with strong self-sealing adhesive</li>
              <li>Bulk discounts available</li>
              <li>Fast Singapore-wide delivery</li>
              <li>Competitive pricing</li>
              <li>Excellent customer service</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
