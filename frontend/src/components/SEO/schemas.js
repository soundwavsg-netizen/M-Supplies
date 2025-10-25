// Contact page structured data
export const contactSchema = {
  "@context": "https://schema.org",
  "@type": "ContactPage",
  "url": "https://www.msupplies.sg/contact",
  "mainEntity": {
    "@type": "Organization",
    "name": "M Supplies (INT) Pte Ltd",
    "email": "msuppliessg@gmail.com",
    "contactPoint": {
      "@type": "ContactPoint",
      "email": "msuppliessg@gmail.com",
      "contactType": "customer service",
      "areaServed": ["SG", "MY"],
      "availableLanguage": "English"
    }
  }
};

// Organization structured data for M Supplies
export const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "M Supplies (INT) Pte Ltd",
  "url": "https://www.msupplies.sg",
  "logo": "https://www.msupplies.sg/assets/m-supplies-logo-transparent.png",
  "sameAs": [
    "https://www.instagram.com/mossomsg",
    "https://shopee.sg/msupplies",
    "https://shopee.sg/rainbowpalace"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "msuppliessg@gmail.com",
    "contactType": "customer service",
    "areaServed": ["SG", "MY"]
  },
  "address": {
    "@type": "PostalAddress",
    "addressCountry": "SG",
    "addressRegion": "Singapore"
  },
  "foundingDate": "2021",
  "description": "Premium polymailers, custom packaging, and branding solutions for online sellers and small businesses in Singapore and Malaysia"
};

// FAQ Page structured data
export const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What products do you sell?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We specialize in premium-quality polymailers (especially thick and colourful ones) and customised packaging materials for small businesses and online sellers."
      }
    },
    {
      "@type": "Question", 
      "name": "Do you offer customised designs or logos?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes! We provide custom printing services for polymailers and packaging—perfect for adding your brand logo or design. You can email us your requirements for a quote."
      }
    },
    {
      "@type": "Question",
      "name": "How can I place an order?",
      "acceptedAnswer": {
        "@type": "Answer", 
        "text": "You can order directly through our website or through our Shopee store. We've made it easy and secure for you to shop whichever way you prefer."
      }
    },
    {
      "@type": "Question",
      "name": "What's the delivery time?", 
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Orders are usually processed within 1–2 working days. Delivery typically takes 2–5 working days depending on your location."
      }
    },
    {
      "@type": "Question",
      "name": "Do you ship internationally?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Currently, we ship within Singapore and Malaysia. For bulk or overseas orders, please email us to discuss options."
      }
    },
    {
      "@type": "Question",
      "name": "How can I contact you?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "For any enquiries or custom requests, please email us at msuppliessg@gmail.com — we'll be happy to assist!"
      }
    }
  ]
};

// Product schema template (can be customized per product)
export const createProductSchema = (product = {}) => ({
  "@context": "https://schema.org/",
  "@type": "Product", 
  "name": product.name || "Premium Thick Polymailer",
  "image": product.images || ["https://www.msupplies.sg/assets/m-supplies-logo-transparent.png"],
  "description": product.description || "Durable, thick, and colourful polymailers designed for online sellers who want to impress their customers.",
  "brand": {
    "@type": "Brand",
    "name": "M Supplies"
  },
  "sku": product.sku || "MS-POLY-001",
  "offers": {
    "@type": "Offer",
    "url": product.url || "https://www.msupplies.sg/products",
    "priceCurrency": "SGD",
    "price": product.price || "7.99",
    "priceValidUntil": "2026-12-31",
    "availability": "https://schema.org/InStock"
  },
  "manufacturer": {
    "@type": "Organization",
    "name": "M Supplies (INT) Pte Ltd"
  }
});