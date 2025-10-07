# M Supplies - Multi-Channel E-commerce Platform

A production-ready e-commerce platform with centralized multi-channel inventory management, built with FastAPI (Python), React, and MongoDB.

## 🎯 Live Demo

**Application URL**: https://msupplies-shop.preview.emergentagent.com

**Test Accounts**:
- **Admin**: admin@polymailer.com / admin123 (use admin@msupplies.sg for new signups)
- **Customer**: customer@example.com / customer123

## ✨ Features Implemented

### ✅ Customer Features (MVP)
- Product catalog with search, filters, and categories
- Product variants (size, color, pack quantity) with tiered pricing
- Shopping cart with GST (9%) calculation
- User authentication (register/login with JWT)
- Checkout flow with shipping details
- Order history and tracking
- Responsive design with Tailwind CSS

### ✅ Admin Features (MVP)
- Admin dashboard with statistics
- **Centralized Multi-Channel Inventory Management**
  - Single source of truth per SKU
  - Real-time stock tracking (on_hand, allocated, available)
  - Safety stock and low-stock alerts
  - Channel buffers (website, Shopee, Lazada)
  - Immutable inventory ledger (audit trail)
  - Multi-channel order import (CSV/API)
  - Shopee webhook stub (ready for integration)
- Product management (view products and variants)
- Order management (view and update status)
- Coupon management (create and edit discount codes)
- User management (view customers)
- Business settings (brand name, GST, channel buffers)

## 🏗 Architecture

### Migration-Ready Design
The codebase follows a **layered architecture** for easy database migration:

```
API Routes (server.py)
    ↓
Service Layer (business logic - DB agnostic)
    ↓
Repository Layer (MongoDB access - swappable)
    ↓
MongoDB
```

This allows you to:
- Swap MongoDB for PostgreSQL by replacing repositories
- Test business logic independently
- Maintain clean separation of concerns

## 📁 Project Structure

```
/app/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, security, database
│   │   ├── schemas/        # Pydantic validation models
│   │   ├── repositories/   # Database access (MongoDB)
│   │   ├── services/       # Business logic
│   │   └── __init__.py
│   ├── server.py           # FastAPI app with all routes
│   ├── seed_data.py        # Database seeding script
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ui/          # Shadcn UI components
    │   │   └── layout/      # Header, Footer
    │   ├── pages/
    │   │   ├── customer/    # Public & customer pages
    │   │   └── admin/       # Admin dashboard
    │   ├── context/         # Auth & Cart state
    │   ├── lib/             # API client & utilities
    │   ├── App.js           # Routes & providers
    │   └── theme.config.js  # Design tokens
    ├── package.json
    └── .env
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB running locally
- Yarn package manager

### 1. Seed Database
```bash
cd /app/backend
python seed_data.py
```

This creates:
- 2 users (admin + customer)
- 2 product types with 38 variants
- 2 discount coupons

### 2. Start Services
```bash
sudo supervisorctl restart all
```

### 3. Access Application
- **Frontend**: https://yourdomain.com
- **API Docs**: https://yourdomain.com/docs
- **Health Check**: https://yourdomain.com/health

## 🎨 Theming & Customization

### Easy Theme Changes
Update colors in `/app/frontend/src/theme.config.js`:

```javascript
export const theme = {
  colors: {
    primary: '#0F766E',    // Teal (your brand color)
    accent: '#F97316',     // Orange (CTAs)
    // ... change any color
  }
}
```

### Component Library
- Built with **Shadcn UI** (in `/app/frontend/src/components/ui/`)
- Customizable, accessible components
- No vendor lock-in

## 🔑 Environment Variables

### Backend `.env`
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=polymailer_db

# JWT
JWT_SECRET=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe (placeholder - add your keys)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# SendGrid (placeholder)
SENDGRID_API_KEY=SG.xxxxx
SENDER_EMAIL=orders@polymailer.com

# GST
GST_PERCENT=9
DEFAULT_CURRENCY=SGD
```

### Frontend `.env`
```bash
REACT_APP_BACKEND_URL=https://yourdomain.com
```

## 📊 Database Schema

### Collections
- **users**: Customer & admin accounts
- **products**: Product information
- **variants**: Product variants (size, color, price tiers)
- **carts**: Shopping carts (session or user-based)
- **orders**: Order details with items and shipping
- **coupons**: Discount codes
- **audit_logs**: Admin action tracking (future)

### Key Design Decisions
- UUID-based IDs (not MongoDB ObjectId) for easier DB migration
- Denormalized order items (snapshot at purchase time)
- Price tiers for bulk discounts
- Separate cart for guests (session-based) and users

## 🔐 Security

✅ Implemented:
- Password hashing (bcrypt)
- JWT access + refresh tokens
- HTTPOnly cookies
- Role-based access control (RBAC)
- CORS configuration
- Input validation (Pydantic)

⏳ To Add (Phase 1.1):
- Rate limiting on auth endpoints
- CSRF protection for forms
- HTTPS enforcement
- Session timeout handling

## 📋 API Routes

### Public
- `GET /api/products` - List products
- `GET /api/products/{id}` - Product details
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Authenticated
- `GET /api/cart` - Get cart
- `POST /api/cart/add` - Add to cart
- `POST /api/orders` - Create order
- `GET /api/orders` - User's orders

### Admin Only
- `POST /api/admin/products` - Create product
- `GET /api/admin/orders` - All orders
- `POST /api/admin/coupons` - Create coupon
- `GET /api/admin/users` - List users

Full API docs: https://yourdomain.com/docs

## 🧪 Testing

### Manual Test Flow
1. Browse products → ✅ Working
2. Add to cart → ✅ Working (GST calculated)
3. Register/Login → ✅ Working
4. Checkout → ✅ Working (order created)
5. View orders → ✅ Working
6. Admin login → ✅ Working
7. Admin dashboard → ✅ Working

### Test Data
```
Products: 2 types, 38 variants
Coupons: WELCOME10 (10% off $50+), BULK20 (20% off $200+)
Users: admin@polymailer.com, customer@example.com
```

## 📦 What's Next? (Phase 1.1)

**Priority Features**:
- [ ] Stripe payment integration (placeholder ready)
- [ ] Email notifications (SendGrid/Postmark)
- [ ] Google OAuth login
- [ ] PDF invoice generation
- [ ] Advanced admin CRUD (full product editor)
- [ ] Carrier integrations (Ninja Van, J&T, Qxpress)
- [ ] Image uploads to S3/R2
- [ ] Purchase orders & stock receiving

**Nice to Have**:
- [ ] Abandoned cart recovery
- [ ] Wishlist
- [ ] Customer reviews
- [ ] Multi-currency display
- [ ] B2B tiered pricing by customer group

## 🐛 Known Limitations (MVP)

- **Payment**: Orders created as "pending" (Stripe not integrated yet)
- **Emails**: No transactional emails (SendGrid placeholders ready)
- **Images**: Using Unsplash placeholders
- **Admin**: View-only for most features (no full CRUD yet)
- **PDF**: No invoice generation (future)

## 🚢 Deployment

### Current Setup (Emergent Platform)
- Supervisor manages backend + frontend
- MongoDB runs locally
- Services auto-restart on code changes

### For Production (Your Own Server)
1. **Dockerize** (Dockerfile provided - see `/app/infrastructure/`)
2. **Environment Variables**: Set all `.env` values
3. **Database**: Use MongoDB Atlas or self-hosted
4. **Domain**: Point your domain to the server
5. **SSL**: Use Caddy or Nginx with Let's Encrypt
6. **Stripe**: Add your live API keys
7. **SendGrid**: Configure email templates

## 📝 Migration Guide (MongoDB → PostgreSQL)

When ready to migrate:

1. **Create PostgreSQL repositories**:
   - Copy `/app/backend/app/repositories/`
   - Replace MongoDB queries with SQL/ORM (SQLAlchemy)
   - Keep same interface/methods

2. **Update database.py**:
   - Replace Motor with SQLAlchemy
   - Update connection logic

3. **Services remain unchanged** (DB-agnostic by design!)

4. **Update schemas** if needed (Pydantic works with both)

## 🤝 Contributing

This is a template project. To customize:

1. Fork/clone the repository
2. Update branding in `theme.config.js`
3. Modify product schemas for your use case
4. Add your Stripe/SendGrid keys
5. Deploy to your infrastructure

## 📧 Support

For questions or issues:
- Email: orders@polymailer.com
- Documentation: This README
- API Docs: https://yourdomain.com/docs

---

**Built with Emergent.sh** | FastAPI + React + MongoDB
