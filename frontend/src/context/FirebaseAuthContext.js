import React, { createContext, useContext, useEffect, useState } from 'react';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  signInWithPopup,
  sendPasswordResetEmail,
  updateProfile
} from 'firebase/auth';
import { auth, googleProvider } from '../lib/firebase';
import api from '../lib/api';

const FirebaseAuthContext = createContext({});

export const useFirebaseAuth = () => {
  const context = useContext(FirebaseAuthContext);
  if (!context) {
    throw new Error('useFirebaseAuth must be used within FirebaseAuthProvider');
  }
  return context;
};

export const FirebaseAuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [idToken, setIdToken] = useState(null);

  // Fetch user profile from backend
  const fetchUserProfile = async (firebaseUser) => {
    try {
      const token = await firebaseUser.getIdToken();
      
      // Set token in API headers
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Get user profile from backend
      const response = await api.get('/auth/me');
      setUserProfile(response.data);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      setUserProfile(null);
    }
  };

  // Listen for auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      
      if (user) {
        // Get Firebase ID token
        const token = await user.getIdToken();
        setIdToken(token);
        
        // Fetch user profile from backend
        await fetchUserProfile(user);
      } else {
        setIdToken(null);
        setUserProfile(null);
        // Remove token from API headers
        delete api.defaults.headers.common['Authorization'];
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  // Register with email and password
  const signup = async (email, password, firstName, lastName, phone = '') => {
    try {
      // Register user in backend first (creates Firebase Auth user + Firestore doc)
      const response = await api.post('/auth/firebase/register', {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        phone: phone,
        role: 'customer'
      });

      // Sign in with email and password to get ID token
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // Update display name
      await updateProfile(userCredential.user, {
        displayName: `${firstName} ${lastName}`
      });

      return { success: true, user: userCredential.user };
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  // Login with email and password
  const login = async (email, password) => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return { success: true, user: userCredential.user };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // Login with Google
  const loginWithGoogle = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      
      // Check if user exists in backend
      const token = await result.user.getIdToken();
      
      try {
        // Try to get user profile
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const profileResponse = await api.get('/auth/me');
        setUserProfile(profileResponse.data);
      } catch (error) {
        // If user doesn't exist in backend, create them
        if (error.response?.status === 404) {
          const [firstName, ...lastNameParts] = (result.user.displayName || '').split(' ');
          const lastName = lastNameParts.join(' ');
          
          // Auto-assign admin role for specific emails
          const adminEmails = ['soundwavsg@gmail.com', 'msuppliessg@gmail.com'];
          const role = adminEmails.includes(result.user.email) ? 'admin' : 'customer';
          
          console.log(`Creating user with role: ${role} for email: ${result.user.email}`);
          
          await api.post('/auth/firebase/register', {
            email: result.user.email,
            password: Math.random().toString(36).slice(-8), // Random password (not used with OAuth)
            first_name: firstName || 'User',
            last_name: lastName || '',
            phone: result.user.phoneNumber || '',
            role: role
          });
          
          // Wait a moment for Firestore to sync
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Fetch the newly created profile
          const newProfileResponse = await api.get('/auth/me');
          setUserProfile(newProfileResponse.data);
          
          console.log('User profile:', newProfileResponse.data);
        } else {
          throw error;
        }
      }
      
      return { success: true, user: result.user };
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    }
  };

  // Logout
  const logout = async () => {
    try {
      await signOut(auth);
      setCurrentUser(null);
      setUserProfile(null);
      setIdToken(null);
      delete api.defaults.headers.common['Authorization'];
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  // Send password reset email
  const resetPassword = async (email) => {
    try {
      await sendPasswordResetEmail(auth, email);
      return { success: true };
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  };

  // Refresh ID token
  const refreshToken = async () => {
    if (currentUser) {
      const token = await currentUser.getIdToken(true);
      setIdToken(token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      return token;
    }
    return null;
  };

  const value = {
    currentUser,
    userProfile,
    user: userProfile, // Alias for compatibility
    idToken,
    loading,
    signup,
    register: signup, // Alias for compatibility
    login,
    loginWithGoogle,
    logout,
    resetPassword,
    refreshToken,
    isAuthenticated: !!currentUser,
    isAdmin: userProfile?.role === 'admin'
  };

  return (
    <FirebaseAuthContext.Provider value={value}>
      {!loading && children}
    </FirebaseAuthContext.Provider>
  );
};

export default FirebaseAuthContext;
