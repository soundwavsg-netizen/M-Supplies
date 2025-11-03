import { useFirebaseAuth } from '@/context/FirebaseAuthContext';
import axios from 'axios';

/**
 * Custom hook for making authenticated API calls in admin pages
 * Uses Firebase ID token for authentication
 */
export const useAuthenticatedAPI = () => {
  const { idToken } = useFirebaseAuth();
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const makeAuthenticatedRequest = async (method, url, data = null) => {
    if (!idToken) {
      throw new Error('Not authenticated');
    }

    const config = {
      method,
      url: `${BACKEND_URL}${url}`,
      headers: {
        'Authorization': `Bearer ${idToken}`,
        'Content-Type': 'application/json',
      },
    };

    if (data) {
      config.data = data;
    }

    return axios(config);
  };

  return {
    get: (url) => makeAuthenticatedRequest('GET', url),
    post: (url, data) => makeAuthenticatedRequest('POST', url, data),
    put: (url, data) => makeAuthenticatedRequest('PUT', url, data),
    delete: (url) => makeAuthenticatedRequest('DELETE', url),
    idToken,
  };
};
