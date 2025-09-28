# Azure Authentication Setup Guide

This guide explains how to configure Azure Active Directory (AAD) authentication for the FastAPI PostgreSQL sample application.

## Overview

The application supports optional Azure Active Directory authentication using OpenID Connect (OIDC). When configured, users can sign in with their Azure AD accounts and access protected features.

## Features

- **Azure AD Integration**: Full integration with Azure Active Directory
- **OpenID Connect (OIDC)**: Standards-based authentication flow
- **Optional Authentication**: Application works with or without Azure AD configured
- **User Profile**: Display authenticated user information
- **Session Management**: Secure server-side session storage
- **Automatic Redirects**: Redirect users to login when authentication is required

## Prerequisites

1. **Azure Subscription**: Active Azure subscription
2. **Azure AD Tenant**: Access to Azure Active Directory
3. **App Registration**: Registered application in Azure AD

## Step 1: Create Azure AD App Registration

### Using Azure Portal

1. **Navigate to Azure Portal**
   - Go to [https://portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure account

2. **Access Azure Active Directory**
   - Search for "Azure Active Directory" in the search bar
   - Select "Azure Active Directory" from the results

3. **Create App Registration**
   - In the left menu, click "App registrations"
   - Click "New registration"
   - Fill out the registration form:
     - **Name**: `FastAPI Restaurant App` (or your preferred name)
     - **Supported account types**: Choose based on your needs:
       - `Accounts in this organizational directory only` (Single tenant)
       - `Accounts in any organizational directory` (Multi-tenant)
     - **Redirect URI**: 
       - Platform: `Web`
       - URI: `http://localhost:8000/auth/callback` (for local development)

4. **Configure Authentication**
   - After creation, go to "Authentication" in the left menu
   - Add additional redirect URIs if needed:
     - Production: `https://your-app-domain.com/auth/callback`
   - Under "Implicit grant and hybrid flows", ensure:
     - ✅ Access tokens (used for implicit flows)
     - ✅ ID tokens (used for implicit and hybrid flows)

5. **Create Client Secret**
   - Go to "Certificates & secrets" in the left menu
   - Click "New client secret"
   - Add description: `FastAPI App Secret`
   - Choose expiration (recommended: 24 months)
   - **Important**: Copy the secret value immediately (it won't be shown again)

6. **Configure API Permissions**
   - Go to "API permissions" in the left menu
   - The following permissions should be present by default:
     - `Microsoft Graph > User.Read` (Delegated)
   - If not present, click "Add a permission" and add it

7. **Note Important Values**
   From the "Overview" page, copy these values:
   - **Application (client) ID**: This is your `AZURE_CLIENT_ID`
   - **Directory (tenant) ID**: This is your `AZURE_TENANT_ID`
   - **Client Secret**: The secret value you created (this is your `AZURE_CLIENT_SECRET`)

### Using Azure CLI

```bash
# Login to Azure
az login

# Create app registration
az ad app create \\
  --display-name "FastAPI Restaurant App" \\
  --web-redirect-uris "http://localhost:8000/auth/callback" \\
  --required-resource-accesses @manifest.json

# Get application details
az ad app list --display-name "FastAPI Restaurant App" --query "[0].{appId:appId,objectId:id}"

# Create service principal
az ad sp create --id <APP_ID>

# Create client secret
az ad app credential reset --id <APP_ID> --display-name "FastAPI App Secret"
```

## Step 2: Configure Application

### Environment Variables

Create or update your `.env` file with the Azure AD configuration:

```bash
# Database configuration (existing)
DBNAME=your_database_name
DBHOST=your_database_host
DBPORT=5432
DBUSER=your_db_user
DBPASS=your_db_password

# Azure Authentication
AZURE_CLIENT_ID=your-application-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback

# Session Secret (generate a secure random string)
SESSION_SECRET_KEY=your-secure-random-session-secret
```

### Docker Configuration

If using Docker Compose, update the `docker-compose.yml` file:

```yaml
services:
  fastapi-app:
    # ... other configuration
    environment:
      # ... existing environment variables
      AZURE_CLIENT_ID: ${AZURE_CLIENT_ID}
      AZURE_CLIENT_SECRET: ${AZURE_CLIENT_SECRET}
      AZURE_TENANT_ID: ${AZURE_TENANT_ID}
      AZURE_REDIRECT_URI: http://localhost:8000/auth/callback
      SESSION_SECRET_KEY: ${SESSION_SECRET_KEY}
```

Then create a `.env` file in the same directory as `docker-compose.yml`:

```bash
AZURE_CLIENT_ID=your-application-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
SESSION_SECRET_KEY=your-secure-random-session-secret
```

## Step 3: Testing Authentication

### Local Development

1. **Start the application**:
   ```bash
   # Without Docker
   python -m uvicorn fastapi_app:app --reload --port 8000
   
   # With Docker
   docker-compose up --build
   ```

2. **Access the application**:
   - Open [http://localhost:8000](http://localhost:8000)
   - You should see a "Sign in with Azure" link in the navigation

3. **Test login flow**:
   - Click "Sign in with Azure"
   - You'll be redirected to Microsoft login page
   - Sign in with your Azure AD account
   - You'll be redirected back to the application
   - Your name should appear in the navigation bar

### Authentication Flow

1. **Login**: User clicks "Sign in with Azure"
2. **Redirect**: User is redirected to Azure AD login page
3. **Authentication**: User enters Azure AD credentials
4. **Authorization**: Azure AD redirects back with authorization code
5. **Token Exchange**: Application exchanges code for access token
6. **User Info**: Application fetches user information from Microsoft Graph
7. **Session**: User information is stored in server-side session
8. **Access**: User can now access authenticated features

## Step 4: Production Deployment

### Azure App Service Configuration

If deploying to Azure App Service, configure the environment variables:

```bash
# Using Azure CLI
az webapp config appsettings set \\
  --resource-group your-resource-group \\
  --name your-app-name \\
  --settings \\
    AZURE_CLIENT_ID="your-client-id" \\
    AZURE_CLIENT_SECRET="your-client-secret" \\
    AZURE_TENANT_ID="your-tenant-id" \\
    AZURE_REDIRECT_URI="https://your-app.azurewebsites.net/auth/callback" \\
    SESSION_SECRET_KEY="your-secure-session-secret"
```

### Update Redirect URIs

Don't forget to add your production URL to the Azure AD app registration:
- Go to Azure Portal > Azure AD > App registrations > Your app
- Navigate to "Authentication"
- Add redirect URI: `https://your-app-domain.com/auth/callback`

## Security Considerations

### Session Security
- Use a strong, random `SESSION_SECRET_KEY`
- Consider session timeout configuration
- Use HTTPS in production

### Client Secret Management
- Store client secrets securely (Azure Key Vault recommended)
- Rotate secrets regularly
- Never commit secrets to source control

### HTTPS Requirements
- Azure AD requires HTTPS for production redirect URIs
- Configure SSL/TLS certificates for your domain
- Use secure cookies in production

## Troubleshooting

### Common Issues

1. **"Azure authentication not configured" error**
   - Ensure all required environment variables are set
   - Check that values don't contain extra spaces or quotes

2. **"Invalid redirect URI" error**
   - Verify the redirect URI in Azure AD matches exactly what you're using
   - Check for http vs https mismatch

3. **"Invalid state parameter" error**
   - This is a security feature - try logging in again
   - Clear browser cookies/session if issue persists

4. **"Failed to get user information" error**
   - Check that `User.Read` permission is granted
   - Ensure the access token is valid

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export FASTAPI_DEBUG=true
```

This will provide more detailed error messages in the application logs.

### Testing Without Azure AD

The application works without Azure AD configuration. Simply don't set the Azure environment variables, and the app will run without authentication features.

## API Endpoints

When Azure authentication is configured, the following endpoints are available:

- `GET /auth/login` - Initiate Azure AD login
- `GET /auth/callback` - Handle Azure AD callback
- `GET /auth/logout` - Logout and clear session
- `GET /auth/profile` - View user profile (requires authentication)

## Integration with Existing Features

The authentication system integrates seamlessly with existing application features:

- **Navigation**: Shows user info and login/logout links
- **User Context**: Current user information is available in all templates
- **Optional Protection**: Individual routes can be protected as needed
- **Backward Compatibility**: Application works with or without authentication

## Next Steps

1. **Customize User Experience**: Modify templates to show user-specific content
2. **Role-Based Access**: Implement Azure AD group-based authorization
3. **API Protection**: Protect API endpoints with authentication requirements
4. **Audit Logging**: Log authentication events for security monitoring

For more information, see:
- [Microsoft Authentication Library (MSAL) Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview)
- [Azure AD App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)