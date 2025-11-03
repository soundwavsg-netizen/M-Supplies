# 🔧 GitHub Cleanup Guide - Step by Step

## ⚠️ IMPORTANT: Just Pushing New Code Won't Fix It!

**Simply pushing new commits will NOT remove the exposed keys from GitHub.**

Why? Because Git keeps a complete history of all commits. Even though your current code no longer has hardcoded keys, anyone can:
- Browse old commits and see the exposed keys
- Use `git log` to view history
- Access previous versions of files

**You MUST either:**
1. **Generate NEW keys and revoke the old ones** (RECOMMENDED - Easier)
2. **Clean the git history** (More complex)

---

## ✅ RECOMMENDED METHOD: Generate New Keys

This is the **easiest and safest** approach. Old keys become useless once revoked.

### Step 1: Generate New Firebase Web API Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **msupplies-ecommerce**
3. Click the **gear icon** (Project Settings)
4. Go to **General** tab
5. Scroll down to **Your apps** section
6. You'll see your web app configuration

**Option A: Create a New Web App (Recommended)**
- Click **Add app** → Choose **Web** (</> icon)
- Give it a name: "M Supplies Web (New)"
- Click **Register app**
- Copy the new `firebaseConfig` object
- You'll get a NEW API key

**Option B: Regenerate Existing Key**
- In Google Cloud Console: https://console.cloud.google.com/
- Select project: **msupplies-ecommerce**
- Go to **APIs & Services** → **Credentials**
- Find your current API key
- Click **Delete** → Then **Create Credentials** → **API Key**

### Step 2: Generate New Firebase Service Account

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: **msupplies-ecommerce**
3. Click **Project Settings** → **Service Accounts** tab
4. Click **"Generate New Private Key"** button
5. Confirm by clicking **"Generate Key"**
6. A JSON file will be downloaded

### Step 3: Generate New SendGrid API Key

1. Go to [SendGrid Dashboard](https://app.sendgrid.com/)
2. Login to your account
3. Navigate to **Settings** → **API Keys** (left sidebar)
4. Find your current key in the list
5. Click the **3 dots** → **Delete** (revoke old key)
6. Click **"Create API Key"** button (top right)
7. Name it: "M Supplies Production"
8. Choose **"Full Access"** (or minimum required: Mail Send, Email Activity)
9. Click **"Create & View"**
10. **COPY THE KEY NOW** (you won't see it again!)

### Step 4: Update Your Codebase

Now you need to update the environment files with new keys.

**For Emergent Environment:**

```bash
# Update frontend .env
nano /app/frontend/.env

# Update these lines with NEW values:
REACT_APP_FIREBASE_API_KEY=<YOUR_NEW_FIREBASE_API_KEY>
REACT_APP_FIREBASE_AUTH_DOMAIN=msupplies-ecommerce.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=msupplies-ecommerce
REACT_APP_FIREBASE_STORAGE_BUCKET=msupplies-ecommerce.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=<YOUR_NEW_SENDER_ID>
REACT_APP_FIREBASE_APP_ID=<YOUR_NEW_APP_ID>

# Save and exit (Ctrl+X, then Y, then Enter)
```

```bash
# Update backend .env
nano /app/backend/.env

# Update this line with NEW value:
SENDGRID_API_KEY=<YOUR_NEW_SENDGRID_API_KEY>

# Save and exit
```

```bash
# Replace Firebase service account credentials
nano /app/backend/firebase-credentials.json

# Delete all content and paste your new JSON file content
# Save and exit
```

```bash
# Restart services to apply new keys
sudo supervisorctl restart all
```

### Step 5: Test Everything Works

```bash
# Test frontend loads
curl -I https://msupplies-store.preview.emergentagent.com/

# Should return: HTTP/2 200
```

Try logging in on the website to verify Firebase Auth works with new keys.

### Step 6: Push to GitHub (Safe Now)

Once new keys are working, you can push to GitHub:

```bash
cd /app
git add .
git commit -m "Security: Update to use environment variables only (no hardcoded credentials)"
git push origin main
```

**Note:** The OLD keys are still in git history, but they're now REVOKED/USELESS, so it doesn't matter!

---

## 🔄 ALTERNATIVE METHOD: Clean Git History

If you want to completely remove the old keys from git history (optional, more complex):

### Option 1: Using GitHub's Secret Scanning (Easiest)

1. Go to your repository on GitHub
2. Click **Settings** → **Security** → **Code security and analysis**
3. Scroll to **Secret scanning alerts**
4. If GitHub detected the secrets, you'll see alerts
5. Click on each alert
6. Click **"Dismiss alert"** after you've rotated the keys
7. For private repos, GitHub may offer to auto-remove

### Option 2: Using `git filter-repo` (Recommended Tool)

This is the modern way to rewrite git history.

**Install git-filter-repo:**
```bash
# On Mac
brew install git-filter-repo

# On Ubuntu/Linux
pip3 install git-filter-repo

# Or download from: https://github.com/newren/git-filter-repo
```

**Clean the repository:**

```bash
# 1. Make a backup first!
cd /path/to/M-Supplies
cd ..
cp -r M-Supplies M-Supplies-backup

# 2. Navigate to your local repo
cd M-Supplies

# 3. Create a file with strings to replace
cat > /tmp/replacements.txt << 'EOF'
[REDACTED]==>REMOVED_FROM_HISTORY
[REDACTED]==>REMOVED_FROM_HISTORY
[REDACTED]==>REMOVED_FROM_HISTORY
EOF

# 4. Run the filter
git filter-repo --replace-text /tmp/replacements.txt

# 5. Force push to GitHub (DANGEROUS - warns collaborators first!)
git push origin --force --all
```

**⚠️ WARNING:** This will rewrite ALL commit history. If others have cloned your repo, they'll need to re-clone!

### Option 3: Using BFG Repo-Cleaner (Alternative)

BFG is faster than git-filter-repo for large repos:

```bash
# 1. Install BFG
brew install bfg  # Mac
# Or download from: https://rtyley.github.io/bfg-repo-cleaner/

# 2. Clone a fresh mirror
cd /tmp
git clone --mirror git@github.com:soundwavsg-netizen/M-Supplies.git

# 3. Create passwords file
cat > passwords.txt << 'EOF'
[REDACTED]
[REDACTED]
[REDACTED]
EOF

# 4. Run BFG to remove credentials
bfg --replace-text passwords.txt M-Supplies.git

# 5. Clean up
cd M-Supplies.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 6. Force push
git push --force
```

### Option 4: Nuclear Option - Delete and Re-create Repo

If the repo is relatively new and you don't mind losing git history:

```bash
# 1. Delete repository on GitHub (Settings → Delete this repository)

# 2. Create new empty repository with same name

# 3. In Emergent environment, remove git history
cd /app
rm -rf .git

# 4. Initialize fresh git
git init
git add .
git commit -m "Initial commit with secure configuration"

# 5. Push to new repo
git remote add origin git@github.com:soundwavsg-netizen/M-Supplies.git
git push -u origin main
```

---

## 📋 Final Verification Checklist

After cleanup, verify:

- [ ] Old API keys have been revoked/deleted in respective dashboards
- [ ] New API keys generated and saved securely
- [ ] `.env` files updated with new keys
- [ ] Application tested and working with new keys
- [ ] (If history cleaned) Git history verified clean:
  ```bash
  git log -p | grep -i "AIzaSyC"  # Should return nothing
  ```
- [ ] New commits pushed to GitHub
- [ ] GitHub security alerts dismissed/resolved
- [ ] `.env` files still in `.gitignore`
- [ ] No more warning emails from Google

---

## 🎯 Summary: What You Need to Do

### SIMPLE PATH (Recommended):
1. ✅ Generate new Firebase API key
2. ✅ Generate new Firebase service account
3. ✅ Generate new SendGrid API key
4. ✅ Update `/app/frontend/.env` with new Firebase keys
5. ✅ Update `/app/backend/.env` with new SendGrid key
6. ✅ Replace `/app/backend/firebase-credentials.json` with new file
7. ✅ Restart services: `sudo supervisorctl restart all`
8. ✅ Test application works
9. ✅ Push to GitHub - old keys are now useless!

### THOROUGH PATH (Optional):
- Do all steps above
- PLUS clean git history using one of the methods
- Force push to GitHub

---

## ❓ FAQ

**Q: Is just pushing new code enough?**
A: No! Old keys are still visible in commit history. You must either revoke old keys OR clean git history.

**Q: Which method should I use?**
A: **Generate new keys** (simplest). Only clean history if you want a perfectly clean audit trail.

**Q: Will cleaning history break anything?**
A: It won't break the app, but collaborators will need to re-clone the repo. Always backup first!

**Q: How do I know if it worked?**
A: After generating new keys, try using old keys - they should be rejected. Check your dashboards to confirm old keys are deleted.

**Q: What if I skip cleaning git history?**
A: It's okay IF you've revoked the old keys. They're visible but useless. For production security audit compliance, cleaning is better.

---

## 🆘 Need Help?

If you get stuck, tell me:
1. Which method you're trying
2. What error you're seeing
3. Where you got stuck

I can help troubleshoot!

---

*Guide created by Emergent AI Agent - December 2024*
