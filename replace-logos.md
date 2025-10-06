# Logo Replacement Instructions

## When you have the actual M Supplies logo files:

1. **Replace the placeholder files** in `/app/frontend/public/assets/`:
   - Replace `placeholder-logo.svg` with your `m-supplies-logo-transparent.png`
   - Replace `placeholder-logo-white.svg` with your `m-supplies-logo-white.png`

2. **Update the Logo component** in `/app/frontend/src/components/ui/Logo.js`:
   - Change line 17: `'/assets/placeholder-logo-white.svg'` → `'/assets/m-supplies-logo-white.png'`
   - Change line 18: `'/assets/placeholder-logo.svg'` → `'/assets/m-supplies-logo-transparent.png'`

3. **File locations where the logo appears**:
   - **Header**: `/app/frontend/src/components/layout/Header.js` (line 26)
   - **Footer**: `/app/frontend/src/components/layout/Footer.js` (line 15)
   - **Admin pages**: Automatically inherits from header
   - **Email templates**: Need to be configured when email system is implemented
   - **Invoice templates**: Need to be configured when PDF generation is implemented

## Current Status:
- ✅ Logo component created and working
- ✅ Header logo implemented and clickable (links to home)
- ✅ Footer logo implemented with white variant
- ✅ Mobile responsive design
- ✅ Fallback text if images fail to load
- ✅ Basic favicon placeholder created
- 🔄 Waiting for actual logo files from Sean

## Logo Specifications:
- **Primary logo**: Transparent background for light backgrounds  
- **White logo**: For dark backgrounds (footer, dark headers)
- **Alt text**: "M Supplies"
- **Sizes**: Small (24px), Medium (32px), Large (48px)
- **Format**: PNG preferred (current placeholders are SVG)