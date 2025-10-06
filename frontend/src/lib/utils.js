import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatPrice(price, currency = 'SGD') {
  return new Intl.NumberFormat('en-SG', {
    style: 'currency',
    currency: currency,
  }).format(price);
}

export function formatDate(date) {
  return new Intl.DateTimeFormat('en-SG', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
}

export function getUser() {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
}

export function setAuth(access_token, user) {
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('user', JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
}

export function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

export function isAdmin() {
  const user = getUser();
  return user && ['owner', 'manager', 'support'].includes(user.role);
}
