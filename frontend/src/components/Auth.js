import React, { useState } from 'react';
import GoogleLogin from './GoogleLogin';
import EmailLogin from './EmailLogin';
import EmailRegister from './EmailRegister';

const Auth = () => {
  const [authMode, setAuthMode] = useState('google'); // 'google', 'email-login', 'email-register'

  const renderAuthComponent = () => {
    switch (authMode) {
      case 'email-login':
        return (
          <EmailLogin
            onSwitchToRegister={() => setAuthMode('email-register')}
            onSwitchToGoogle={() => setAuthMode('google')}
          />
        );
      case 'email-register':
        return (
          <EmailRegister
            onSwitchToLogin={() => setAuthMode('email-login')}
            onSwitchToGoogle={() => setAuthMode('google')}
          />
        );
      case 'google':
      default:
        return (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full">
              {/* Header Section */}
              <div className="text-center mb-8">
                <div className="mx-auto h-16 w-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                </div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  AI To-Do Manager
                </h1>
                <p className="text-gray-600 text-lg">
                  Organize your tasks with intelligent assistance
                </p>
              </div>

              {/* Main Card */}
              <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <div className="text-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    Welcome back!
                  </h2>
                  <p className="text-gray-500">
                    Choose your preferred sign-in method
                  </p>
                </div>

                {/* Google Sign-in */}
                <div className="mb-6">
                  <GoogleLogin />
                </div>

                {/* Divider */}
                <div className="relative mb-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-white text-gray-500 font-medium">or</span>
                  </div>
                </div>

                {/* Email Options */}
                <div className="space-y-3">
                  <button
                    onClick={() => setAuthMode('email-login')}
                    className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-xl text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 group"
                  >
                    <svg className="w-5 h-5 mr-3 text-gray-400 group-hover:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Sign in with Email
                  </button>
                  
                  <button
                    onClick={() => setAuthMode('email-register')}
                    className="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl text-sm font-medium text-white hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                    Create New Account
                  </button>
                </div>
              </div>

              {/* Features Section */}
              <div className="mt-8 grid grid-cols-3 gap-4 text-center">
                <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <p className="text-xs text-gray-600 font-medium">AI Powered</p>
                </div>
                <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-xs text-gray-600 font-medium">Smart Priority</p>
                </div>
                <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </div>
                  <p className="text-xs text-gray-600 font-medium">Easy to Use</p>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return renderAuthComponent();
};

export default Auth;
