import logging
import os
import pathlib
from datetime import datetime
import secrets

from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import Depends, FastAPI, Form, Request, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.sql import func
from sqlmodel import Session, select

from .models import Restaurant, Review, engine
from .auth import init_azure_auth, get_azure_auth

# Setup logger and Azure Monitor:
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor()


# Setup FastAPI app:
app = FastAPI()

# Add session middleware for authentication
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))
)

# Initialize Azure Authentication if credentials are provided
try:
    if all([
        os.getenv('AZURE_CLIENT_ID'),
        os.getenv('AZURE_CLIENT_SECRET'), 
        os.getenv('AZURE_TENANT_ID')
    ]):
        init_azure_auth()
        logger.info("Azure authentication initialized")
    else:
        logger.info("Azure authentication not configured - running without authentication")
except Exception as e:
    logger.warning(f"Failed to initialize Azure authentication: {e}")

parent_path = pathlib.Path(__file__).parent.parent
app.mount("/mount", StaticFiles(directory=parent_path / "static"), name="static")
templates = Jinja2Templates(directory=parent_path / "templates")
templates.env.globals["prod"] = os.environ.get("RUNNING_IN_PRODUCTION", False)
# Use relative path for url_for, so that it works behind a proxy like Codespaces
templates.env.globals["url_for"] = app.url_path_for


# Dependency to get the database session
def get_db_session():
    with Session(engine) as session:
        yield session


# Authentication helper
def get_current_user(request: Request):
    """Get current authenticated user or None if not authenticated"""
    try:
        auth = get_azure_auth()
        return auth.get_current_user(request)
    except RuntimeError:
        # Azure auth not initialized
        return None


def require_auth(request: Request):
    """Require authentication - redirect to login if not authenticated"""
    try:
        auth = get_azure_auth()
        if not auth.is_authenticated(request):
            request.session['next_url'] = str(request.url)
            return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    except RuntimeError:
        # Azure auth not initialized - continue without authentication
        pass
    return None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: Session = Depends(get_db_session)):
    logger.info("root called")
    
    # Get current user for display
    current_user = get_current_user(request)
    
    statement = (
        select(Restaurant, func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("review_count"))
        .outerjoin(Review, Review.restaurant == Restaurant.id)
        .group_by(Restaurant.id)
    )
    results = session.exec(statement).all()

    restaurants = []
    for restaurant, avg_rating, review_count in results:
        restaurant_dict = restaurant.dict()
        restaurant_dict["avg_rating"] = avg_rating
        restaurant_dict["review_count"] = review_count
        restaurant_dict["stars_percent"] = round((float(avg_rating) / 5.0) * 100) if review_count > 0 else 0
        restaurants.append(restaurant_dict)

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "restaurants": restaurants,
        "current_user": current_user
    })


@app.get("/create", response_class=HTMLResponse)
async def create_restaurant(request: Request):
    logger.info("Request for add restaurant page received")
    return templates.TemplateResponse("create_restaurant.html", {"request": request})


@app.post("/add", response_class=RedirectResponse)
async def add_restaurant(
    request: Request, restaurant_name: str = Form(...), street_address: str = Form(...), description: str = Form(...),
    session: Session = Depends(get_db_session)
):
    logger.info("name: %s address: %s description: %s", restaurant_name, street_address, description)
    restaurant = Restaurant()
    restaurant.name = restaurant_name
    restaurant.street_address = street_address
    restaurant.description = description
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)

    return RedirectResponse(url=app.url_path_for("details", id=restaurant.id), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/details/{id}", response_class=HTMLResponse)
async def details(request: Request, id: int, session: Session = Depends(get_db_session)):
    restaurant = session.exec(select(Restaurant).where(Restaurant.id == id)).first()
    reviews = session.exec(select(Review).where(Review.restaurant == id)).all()

    review_count = len(reviews)

    avg_rating = 0
    if review_count > 0:
        avg_rating = sum(review.rating for review in reviews if review.rating is not None) / review_count

    restaurant_dict = restaurant.dict()
    restaurant_dict["avg_rating"] = avg_rating
    restaurant_dict["review_count"] = review_count
    restaurant_dict["stars_percent"] = round((float(avg_rating) / 5.0) * 100) if review_count > 0 else 0

    return templates.TemplateResponse(
        "details.html", {"request": request, "restaurant": restaurant_dict, "reviews": reviews}
    )


@app.post("/review/{id}", response_class=RedirectResponse)
async def add_review(
    request: Request,
    id: int,
    user_name: str = Form(...),
    rating: str = Form(...),
    review_text: str = Form(...),
    session: Session = Depends(get_db_session),
):
    review = Review()
    review.restaurant = id
    review.review_date = datetime.now()
    review.user_name = user_name
    review.rating = int(rating)
    review.review_text = review_text
    session.add(review)
    session.commit()

    return RedirectResponse(url=app.url_path_for("details", id=id), status_code=status.HTTP_303_SEE_OTHER)


# Authentication Routes
@app.get("/auth/login")
async def login(request: Request):
    """Initiate Azure AD login"""
    try:
        auth = get_azure_auth()
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        
        # Get authorization URL
        auth_url = auth.get_auth_url(state=state)
        return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
        
    except RuntimeError:
        # Azure auth not configured
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Azure authentication not configured"
        )


@app.get("/auth/callback")
async def auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle Azure AD callback"""
    try:
        auth = get_azure_auth()
        
        if error:
            logger.error(f"Authentication error: {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Authentication failed: {error}")
        
        if not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization code missing")
        
        # Verify state parameter
        stored_state = request.session.get('oauth_state')
        if not stored_state or stored_state != state:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")
        
        # Exchange code for token
        token_result = auth.get_token_from_code(code, state)
        
        if 'error' in token_result:
            logger.error(f"Token exchange error: {token_result.get('error_description', token_result['error'])}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {token_result.get('error_description', token_result['error'])}"
            )
        
        # Get user information
        access_token = token_result.get('access_token')
        user_info = auth.get_user_info(access_token)
        
        if not user_info:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get user information")
        
        # Store user in session
        request.session['user'] = {
            'id': user_info.get('id'),
            'name': user_info.get('displayName'),
            'email': user_info.get('mail') or user_info.get('userPrincipalName'),
            'access_token': access_token
        }
        
        # Clean up session
        if 'oauth_state' in request.session:
            del request.session['oauth_state']
        
        # Redirect to originally requested page or home
        next_url = request.session.pop('next_url', '/')
        return RedirectResponse(url=next_url, status_code=status.HTTP_302_FOUND)
        
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Azure authentication not configured"
        )


@app.get("/auth/logout")
async def logout(request: Request):
    """Logout user"""
    try:
        auth = get_azure_auth()
        auth.logout(request)
        
        # Redirect to Azure AD logout
        logout_url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/logout"
        post_logout_redirect = request.url_for('index')
        full_logout_url = f"{logout_url}?post_logout_redirect_uri={post_logout_redirect}"
        
        return RedirectResponse(url=full_logout_url, status_code=status.HTTP_302_FOUND)
        
    except RuntimeError:
        # Azure auth not configured, just clear session and redirect
        if 'user' in request.session:
            del request.session['user']
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/auth/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """Display user profile"""
    current_user = get_current_user(request)
    
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "current_user": current_user
    })
