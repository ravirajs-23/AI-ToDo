import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = 'http://localhost:5000/api';

  useEffect(() => {
    // Check if user is already logged in
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        withCredentials: true
      });
      
      if (response.data.success) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.log('No active session');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (googleToken) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        token: googleToken
      }, {
        withCredentials: true
      });

      if (response.data.success) {
        setUser(response.data.user);
        return { success: true };
      } else {
        console.log('Login failed:', response.data.message);
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const loginWithEmail = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login-email`, {
        email,
        password
      }, {
        withCredentials: true
      });

      if (response.data.success) {
        setUser(response.data.user);
        return { success: true };
      } else {
        console.log('Login failed:', response.data.message);
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const register = async (email, password, name) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        email,
        password,
        name
      }, {
        withCredentials: true
      });

      if (response.data.success) {
        setUser(response.data.user);
        return { success: true };
      } else {
        console.log('Registration failed:', response.data.message);
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        message: error.response?.data?.message || 'Registration failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/auth/logout`, {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    loginWithEmail,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

