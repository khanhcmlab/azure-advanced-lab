import os
import json
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
import msal
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware


class AzureAuth:
    def __init__(self, app_id: str, app_secret: str, tenant_id: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_id = tenant_id
        self.redirect_uri = redirect_uri
        
        # MSAL Configuration
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["User.Read"]
        
        # Create MSAL instance
        self.msal_app = msal.ConfidentialClientApplication(
            app_id,
            authority=self.authority,
            client_credential=app_secret,
        )
        
        # OAuth configuration for Authlib
        self.oauth = OAuth()
        self.oauth.register(
            name='azure',
            client_id=app_id,
            client_secret=app_secret,
            server_metadata_url=f'https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid_configuration',
            client_kwargs={
                'scope': 'openid email profile User.Read'
            }
        )

    def get_auth_url(self, state: str = None) -> str:
        """Generate Azure AD authorization URL"""
        auth_url = self.msal_app.get_authorization_request_url(
            self.scope,
            redirect_uri=self.redirect_uri,
            state=state
        )
        return auth_url

    def get_token_from_code(self, code: str, state: str = None) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        result = self.msal_app.acquire_token_by_authorization_code(
            code,
            scopes=self.scope,
            redirect_uri=self.redirect_uri
        )
        return result

    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Microsoft Graph"""
        import requests
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None

    def is_authenticated(self, request: Request) -> bool:
        """Check if user is authenticated"""
        return 'user' in request.session

    def get_current_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if self.is_authenticated(request):
            return request.session.get('user')
        return None

    def require_auth(self, request: Request):
        """Decorator to require authentication"""
        if not self.is_authenticated(request):
            # Store the original URL to redirect back after login
            request.session['next_url'] = str(request.url)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

    def logout(self, request: Request):
        """Clear user session"""
        if 'user' in request.session:
            del request.session['user']
        if 'next_url' in request.session:
            del request.session['next_url']


# Global Azure Auth instance (will be initialized in app.py)
azure_auth: Optional[AzureAuth] = None


def init_azure_auth(
    app_id: str = None,
    app_secret: str = None, 
    tenant_id: str = None,
    redirect_uri: str = None
) -> AzureAuth:
    """Initialize Azure Authentication"""
    global azure_auth
    
    # Get from environment variables if not provided
    app_id = app_id or os.getenv('AZURE_CLIENT_ID')
    app_secret = app_secret or os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
    redirect_uri = redirect_uri or os.getenv('AZURE_REDIRECT_URI', 'http://localhost:8000/auth/callback')
    
    if not all([app_id, app_secret, tenant_id]):
        raise ValueError("Azure authentication requires AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID")
    
    azure_auth = AzureAuth(app_id, app_secret, tenant_id, redirect_uri)
    return azure_auth


def get_azure_auth() -> AzureAuth:
    """Get the global Azure Auth instance"""
    if azure_auth is None:
        raise RuntimeError("Azure authentication not initialized. Call init_azure_auth() first.")
    return azure_auth