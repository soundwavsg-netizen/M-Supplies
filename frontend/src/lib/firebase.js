/**
 * Firebase Configuration for M Supplies Frontend
 * 
 * TO GET YOUR FIREBASE CONFIG:
 * 1. Go to Firebase Console: https://console.firebase.google.com/
 * 2. Select your project: msupplies-ecommerce
 * 3. Click the gear icon (Project Settings)
 * 4. Scroll down to "Your apps" section
 * 5. Click on the web app (</>) or create a new web app
 * 6. Copy the firebaseConfig object and replace the values below
 */

import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// Firebase configuration
// TODO: Update these values from Firebase Console → Project Settings → Your apps
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyDummyKeyForDevelopment123456789",
  authDomain: "msupplies-ecommerce.firebaseapp.com",
  projectId: "msupplies-ecommerce",
  storageBucket: "msupplies-ecommerce.appspot.com",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "123456789012",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:123456789012:web:abc123def456"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

// Google OAuth Provider
export const googleProvider = new GoogleAuthProvider();

// Configure Google Provider
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

export default app;
