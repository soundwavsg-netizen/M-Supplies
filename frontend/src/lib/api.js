import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add session ID for guest users
    const sessionId = getSessionId();
    config.headers['X-Session-Id'] = sessionId;
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// Generate or get session ID for guest users
function getSessionId() {
  let sessionId = sessionStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('session_id', sessionId);
  }
  return sessionId;
}

// Auth
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Products
export const productsAPI = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  getCategories: () => api.get('/categories'),
};

// Cart
export const cartAPI = {
  get: () => api.get('/cart'),
  add: (data) => api.post('/cart/add', data),
  update: (variantId, data) => api.put(`/cart/item/${variantId}`, data),
  clear: () => api.delete('/cart'),
};

// Orders
export const ordersAPI = {
  create: (data) => api.post('/orders', data),
  list: () => api.get('/orders'),
  get: (id) => api.get(`/orders/${id}`),
};

// Payment
export const paymentAPI = {
  createIntent: (orderId) => api.post('/payment/create-intent', null, { params: { order_id: orderId } }),
  getConfig: () => api.get('/payment/config'),
};

// Admin - Products
export const adminProductsAPI = {
  create: (data) => api.post('/admin/products', data),
  update: (id, data) => api.put(`/admin/products/${id}`, data),
  delete: (id) => api.delete(`/admin/products/${id}`),
};

// Admin - Orders
export const adminOrdersAPI = {
  list: (params) => api.get('/admin/orders', { params }),
  updateStatus: (id, data) => api.put(`/admin/orders/${id}/status`, data),
};

// Admin - Coupons
export const adminCouponsAPI = {
  list: (params) => api.get('/admin/coupons', { params }),
  create: (data) => api.post('/admin/coupons', data),
  update: (id, data) => api.put(`/admin/coupons/${id}`, data),
};

// Admin - Users
export const adminUsersAPI = {
  list: (params) => api.get('/admin/users', { params }),
  update: (id, data) => api.put(`/admin/users/${id}`, data),
};

// Admin - Upload
export const adminUploadAPI = {
  images: (formData) => api.post('/admin/upload/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

// Admin - Settings
export const adminSettingsAPI = {
  get: () => api.get('/admin/settings'),
  update: (data) => api.put('/admin/settings', data),
};

export default api;
