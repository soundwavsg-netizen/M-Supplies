# 🔑 Google Cloud Keys - What to Delete

## Quick Answer:

**DELETE: API Keys** ✅ (This is the exposed Firebase key)

**KEEP: OAuth 2.0 Client IDs** ⚠️ (Can optionally regenerate for extra security)

---

## 📋 Detailed Explanation

### 1️⃣ **API Keys** (DELETE & REGENERATE THIS)

**What is it?**
- This is your Firebase Web API key
- The one that was exposed: `[REDACTED]`
- Used by your frontend to connect to Firebase services (Auth, Firestore)

**Where is it used?**
- In `/app/frontend/.env` as `REACT_APP_FIREBASE_API_KEY`
- In the Firebase config in your frontend code

**What to do:**
```
✅ DELETE the existing API key
✅ CREATE a new API key
✅ UPDATE /app/frontend/.env with the new key
✅ RESTART frontend
```

**How to delete:**
1. In Google Cloud Console → **APIs & Services** → **Credentials**
2. Under **API Keys** section, find your key
3. Click the **trash/delete icon** on the right
4. Confirm deletion

**How to create new:**
1. Click **"+ CREATE CREDENTIALS"** at the top
2. Select **"API key"**
3. A new key will be generated
4. Click **"RESTRICT KEY"** (important for security!)
5. Under **API restrictions**, select **"Restrict key"**
6. Enable these APIs:
   - Identity Toolkit API
   - Cloud Firestore API
   - Firebase Authentication API
7. Under **Application restrictions**, select **"HTTP referrers"**
8. Add your domains:
   ```
   https://msupplies-store.preview.emergentagent.com/*
   https://www.msupplies.sg/*
   https://msupplies.sg/*
   http://localhost:3000/*  (for local development)
   ```
9. Click **"SAVE"**
10. Copy the new API key

---

### 2️⃣ **OAuth 2.0 Client IDs** (OPTIONAL - Usually Safe to Keep)

**What is it?**
- Used specifically for Google Sign-In (the "Sign in with Google" button)
- Consists of:
  - Client ID (public, safe to expose)
  - Client Secret (should be kept secret, but usually only needed for server-side OAuth)

**Where is it used?**
- For Google OAuth login functionality
- Client ID can be public (it's supposed to be in your frontend)

**Is it exposed/dangerous?**
- Client IDs are designed to be public, so less dangerous
- Client Secrets (if any) should be kept private

**What to do:**

**Option A: Keep It (Recommended for now)**
- OAuth 2.0 Client IDs are meant to be somewhat public
- They're restricted by domain anyway
- Unless you see unusual activity, you can keep them

**Option B: Regenerate (Extra Security)**
If you want to be thorough:

1. In Google Cloud Console → **APIs & Services** → **Credentials**
2. Under **OAuth 2.0 Client IDs** section
3. Click on your existing client ID
4. Note down the **Authorized JavaScript origins** and **Authorized redirect URIs**
5. Go back and click **DELETE** on the old client ID
6. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
7. Choose **"Web application"**
8. Add your origins and redirect URIs:
   ```
   Authorized JavaScript origins:
   - https://msupplies-store.preview.emergentagent.com
   - https://www.msupplies.sg
   - http://localhost:3000
   
   Authorized redirect URIs:
   - https://msupplies-store.preview.emergentagent.com/__/auth/handler
   - https://www.msupplies.sg/__/auth/handler
   - http://localhost:3000/__/auth/handler
   ```
9. Click **"CREATE"**
10. Copy the new Client ID and Client Secret (if shown)

**Note:** For Firebase Auth Google Sign-In, you usually don't need to manually configure OAuth client IDs - Firebase handles this automatically!

---

## 🎯 Step-by-Step: What You Should Do Right Now

### Step 1: Delete & Create New API Key

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select project: **msupplies-ecommerce**
3. Find the **API Keys** section
4. Click **delete icon** (🗑️) next to your current API key
5. Click **"+ CREATE CREDENTIALS"** → **"API key"**
6. Copy the new key immediately
7. Click **"RESTRICT KEY"**
8. Name it: "M Supplies Web API Key"
9. Set restrictions:
   - Application restrictions: **HTTP referrers**
   - Add: `https://msupplies-store.preview.emergentagent.com/*`
   - API restrictions: **Restrict key**
   - Select: Identity Toolkit API, Cloud Firestore API
10. Click **"SAVE"**

### Step 2: Update Your Environment

Tell me the new API key, and I'll update it for you!

Or you can do it yourself:
```bash
nano /app/frontend/.env
# Update this line:
REACT_APP_FIREBASE_API_KEY=<YOUR_NEW_API_KEY_HERE>
# Save (Ctrl+X, Y, Enter)

sudo supervisorctl restart frontend
```

### Step 3: Verify It Works

I'll test the login page for you to make sure Firebase Auth is working.

---

## ⚠️ About Your "Firebase Project Gone" Issue

Based on my check:
- ✅ Your backend is still connected to Firebase (logs show: "Firebase initialized successfully with project: msupplies-ecommerce")
- ✅ Your app is loading correctly
- ✅ Login page is accessible

**Possible reasons you don't see it:**

1. **Wrong Google Account**
   - Are you logged into the correct Google account?
   - Try: https://console.firebase.google.com/ and check which account is shown in top-right

2. **Project Hidden/Archived**
   - Firebase doesn't actually "delete" projects - they get archived
   - Look for an "Archived" or "Deleted" section in Firebase Console

3. **Permission Issue**
   - Someone may have removed your access
   - Check if you're the owner or just a member

4. **Different Organization**
   - Project might be under a different organization
   - Click the project dropdown to see all available projects

**To verify:**
- Go to: https://console.firebase.google.com/
- Click the project dropdown at the top
- Look for "msupplies-ecommerce" in the list
- If not there, check for "Show deleted projects" option

**The good news:**
Your app is still working! The Firebase project is definitely still active (backend is connected successfully). You just need to find it in the console.

---

## 🆘 Need Help?

Once you find your Firebase project:
1. Delete the old API key
2. Generate a new one
3. Send me the new key (via this chat)
4. I'll update your environment and restart services

Or tell me what you see in the Firebase Console and I can guide you further!
