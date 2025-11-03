import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Menu, X, LogOut } from 'lucide-react';
import { useFirebaseAuth } from '@/context/FirebaseAuthContext';
import { Button } from '@/components/ui/button';
import Logo from '@/components/ui/Logo';
import { theme } from '@/theme.config';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { userProfile, logout } = useFirebaseAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Logo variant="primary" size="xl" linkTo="/" showText={false} />

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {/* Show Products link for admin users */}
            {userProfile && userProfile.role !== 'customer' && (
              <Link
                to="/products"
                className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
                data-testid="products-nav-link"
              >
                Products
              </Link>
            )}
            <Link
              to="/"
              className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
            >
              Home
            </Link>
            <Link
              to="/faq"
              className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
            >
              FAQ
            </Link>
            <Link
              to="/contact"
              className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
            >
              Contact
            </Link>
          </nav>

          {/* Right Actions */}
          <div className="flex items-center space-x-4">
            {/* Cart - temporarily hidden */}
            {/* <Button
              variant="ghost"
              size="icon"
              className="relative"
              onClick={() => navigate('/cart')}
              data-testid="cart-button"
            >
              <ShoppingCart className="w-5 h-5" />
              {cartItemCount > 0 && (
                <span
                  className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center"
                  data-testid="cart-count"
                >
                  {cartItemCount}
                </span>
              )}
            </Button> */}

            {/* User Menu */}
            {userProfile ? (
              <div className="hidden md:flex items-center space-x-2">
                <Link to="/account">
                  <Button variant="ghost" size="sm" data-testid="account-link">
                    <User className="w-4 h-4 mr-2" />
                    Account
                  </Button>
                </Link>
                {userProfile.role !== 'customer' && (
                  <Link to="/admin">
                    <Button variant="outline" size="sm" data-testid="admin-link">
                      Admin
                    </Button>
                  </Link>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  data-testid="logout-button"
                >
                  <LogOut className="w-5 h-5" />
                </Button>
              </div>
            ) : (
              <Link to="/login">
                <Button size="sm" data-testid="login-button">
                  <User className="w-4 h-4 mr-2" />
                  Login
                </Button>
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-menu-button"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col space-y-4">
              {/* Show products for admin users */}
              {user && user.role !== 'customer' && (
                <Link
                  to="/products"
                  className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Products
                </Link>
              )}
              <Link
                to="/"
                className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                Home
              </Link>
              <Link
                to="/faq"
                className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                FAQ
              </Link>
              <Link
                to="/contact"
                className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                Contact
              </Link>
              {user && (
                <>
                  <Link
                    to="/orders"
                    className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    My Orders
                  </Link>
                  {user.role !== 'customer' && (
                    <Link
                      to="/admin"
                      className="text-gray-700 hover:text-teal-700 transition-colors font-medium"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Admin Panel
                    </Link>
                  )}
                  <button
                    onClick={() => {
                      handleLogout();
                      setMobileMenuOpen(false);
                    }}
                    className="text-left text-gray-700 hover:text-teal-700 transition-colors font-medium"
                  >
                    Logout
                  </button>
                </>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
