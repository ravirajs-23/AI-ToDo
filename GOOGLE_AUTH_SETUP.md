# Google Authentication Setup Guide

This guide will help you set up Google OAuth authentication for your AI To-Do List Manager.

## Prerequisites

1. A Google Cloud Platform account
2. A Google Cloud project

## Step 1: Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID gen-lang-client-0993618600

## Step 2: Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API" and enable it
3. Also enable "Google Identity" if available

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Add authorized origins:
   - `http://localhost:3000` (for development)
   - `http://localhost:5000` (for backend)
5. Add authorized redirect URIs:
   - `http://localhost:3000` (for development)
6. Click "Create"
7. Copy the Client ID (you'll need this for both frontend and backend)

## Step 4: Configure Environment Variables

### Backend Configuration

Create a `.env` file in the backend directory with:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# AI Provider Configuration
AI_PROVIDER=chatgpt
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Frontend Configuration

Create a `.env` file in the frontend directory with:

```env
# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here
```

## Step 5: Install Dependencies

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
cd frontend
npm install
```

## Step 6: Run the Application

### Start the Backend

```bash
cd backend
python app.py
```

The backend will be available at `http://localhost:5000`

### Start the Frontend

```bash
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Step 7: Test Authentication

1. Open `http://localhost:3000` in your browser
2. You should see a Google login button
3. Click the button and sign in with your Google account
4. After successful authentication, you should see the to-do list interface
5. Create some tasks and verify they are saved to your user account

## Security Notes

1. **Never commit your `.env` files** to version control
2. **Use strong secret keys** in production
3. **Configure proper CORS settings** for production domains
4. **Use HTTPS** in production
5. **Regularly rotate your OAuth credentials**

## Troubleshooting

### Common Issues

1. **"Invalid client" error**: Check that your Google Client ID is correct
2. **CORS errors**: Ensure your backend CORS settings include your frontend domain
3. **"Token verification failed"**: Verify your Google Client ID matches between frontend and backend
4. **Database errors**: Make sure the SQLite database file is writable

### Debug Steps

1. Check browser console for JavaScript errors
2. Check backend logs for authentication errors
3. Verify environment variables are loaded correctly
4. Test the `/api/health` endpoint to ensure backend is running

## Production Deployment

For production deployment:

1. Update authorized origins and redirect URIs in Google Cloud Console
2. Use environment variables for all sensitive configuration
3. Enable HTTPS
4. Configure proper CORS settings
5. Use a production-grade database (PostgreSQL, MySQL, etc.)
6. Set up proper logging and monitoring

## Support

If you encounter issues:

1. Check the Google Cloud Console for API quotas and limits
2. Review the Google OAuth 2.0 documentation
3. Check the application logs for detailed error messages
