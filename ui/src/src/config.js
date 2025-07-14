// Configuration file for the Azure AI Translator Web UI
// Update these values according to your environment

export const config = {
  // Backend API base URL - update this to match your Azure Function App URL
  apiBaseUrl: import.meta.env.VITE_BASE_URL || 'https://your-backend-url.azurewebsites.net/api',
  
  // Authentication configuration
  auth: {
    // For development/testing purposes - replace with actual authentication
    // In production, you should implement proper OAuth2/Azure AD authentication
    mockToken: 'your-actual-token-here',
    
    // Enable mock authentication for development
    useMockAuth: 'development'
  },
  
  // File upload configuration
  upload: {
    // Maximum file size in bytes (10MB)
    maxFileSize: 10 * 1024 * 1024,
    
    // Allowed file types
    allowedTypes: [
      'application/pdf',
      'text/plain',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/png',
      'image/gif'
    ]
  }
};
