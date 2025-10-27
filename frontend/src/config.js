// API configuration
const getApiBaseUrl = () => {
  // Use environment variable if available
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // In production (static files served from Flask), use relative URLs
  if (process.env.NODE_ENV === 'production') {
    return '/api';
  }
  
  // Default to localhost for development
  return 'http://localhost:5000/api';
};

export const API_BASE_URL = getApiBaseUrl();
export const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';

