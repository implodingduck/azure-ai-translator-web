# Azure AI Translator Web UI - File Management

This React application provides a user interface for managing files and directories in your Azure storage, designed to work with the Azure AI Translator backend API.

## Features

- **Directory Management**: List, create, and browse directories
- **File Upload**: Upload files to selected directories using Azure SAS tokens
- **File Listing**: View files within directories
- **Real-time Status**: Loading indicators and error handling
- **Responsive Design**: Works on desktop and mobile devices

## Setup

1. **Configure the backend URL and authentication**:
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` and update:
   - `REACT_APP_API_BASE_URL`: Your Azure Function App URL
   - `REACT_APP_ACCESS_TOKEN`: Your authentication token

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

## API Integration

The UI integrates with the following backend endpoints:

- `GET /ListDirectories` - List all available directories
- `GET /ListFilesInDirectory/{directory}` - List files in a specific directory
- `POST /CreateBlobDirectory` - Create a new directory
- `POST /GenerateSasToken` - Generate SAS token for file upload

## File Upload Process

1. User selects a directory from the list
2. User chooses a file to upload
3. Application requests a SAS token from the backend
4. File is uploaded directly to Azure storage using the SAS URL
5. File list is refreshed to show the new file

## Configuration

Key configuration options in `src/config.js`:

- `apiBaseUrl`: Backend API endpoint
- `auth.mockToken`: Authentication token
- `upload.maxFileSize`: Maximum file size (default: 10MB)
- `upload.allowedTypes`: Allowed file types (optional validation)

## Authentication

Currently uses a mock authentication system for development. In production, you should implement proper OAuth2/Azure AD authentication by:

1. Installing an authentication library (e.g., `@azure/msal-react`)
2. Setting up Azure AD app registration
3. Updating the auth configuration in `config.js`
4. Modifying the `BackendApi` class to use proper token acquisition

## Styling

The UI uses a modern, clean design with:
- Responsive grid layout
- Professional color scheme
- Hover effects and transitions
- Loading states and error messages
- Mobile-friendly responsive design

## Troubleshooting

1. **CORS Issues**: Ensure your Azure Function App has CORS configured for your domain
2. **Authentication Errors**: Verify your access token is valid and not expired
3. **Upload Failures**: Check that the SAS URL generation is working correctly
4. **Network Errors**: Verify the backend API URL is correct and accessible

## Development

To extend the functionality:

1. Add new API methods to `BackendApi.js`
2. Update the UI components in `App.jsx`
3. Modify styles in `App.css`
4. Update configuration in `config.js`
