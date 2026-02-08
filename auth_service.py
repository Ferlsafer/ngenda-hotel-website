import os
import time
from threading import Lock, Thread

try:
    import requests
    import jwt
    from datetime import datetime, timedelta
    REQUESTS_AVAILABLE = True
    print("Requests and PyJWT modules available - HMS integration enabled")
except ImportError as e:
    REQUESTS_AVAILABLE = False
    print(f"Warning: {e}. Using mock mode only.")
    print("Install with: pip install requests PyJWT")

class HMSAuthService:
    """Background Authentication Service for HMS API"""
    
    def __init__(self, base_url=None, auth_email=None, auth_password=None, hotel_id=None):
        # Connection Configuration - Use production settings
        self.base_url = base_url or os.getenv('HMS_API_URL', 'http://localhost:5000')
        self.auth_email = auth_email or os.getenv('HMS_AUTH_EMAIL', 'website@ngendahotel.com')
        self.auth_password = auth_password or os.getenv('HMS_AUTH_PASSWORD', 'website-service-account-2026')
        self.hotel_id = hotel_id or os.getenv('HMS_HOTEL_ID', '1')
        
        # Endpoint Configuration
        self.auth_endpoint = os.getenv('HMS_AUTH_ENDPOINT', '/api/auth/login')
        
        # Token storage
        self.jwt_token = None
        self.token_expires_at = None
        self.auth_lock = Lock()
        
        # Auto-retry configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # Auto-refresh buffer (refresh 5 minutes before expiry)
        self.refresh_buffer_minutes = 5
        
        # Verification: Check if we should use real HMS or mock mode
        self.should_use_real_hms = self._verify_production_credentials()
        
        print(f"HMS Auth Service initialized for Hotel ID {self.hotel_id}")
        print(f"API URL: {self.base_url}")
        print(f"Auth Email: {self.auth_email}")
        print(f"Using Real HMS: {self.should_use_real_hms}")
        
    def _verify_production_credentials(self):
        """Verify if we should use real HMS or mock mode"""
        # Check if we have production credentials
        has_real_email = self.auth_email and self.auth_email != 'website@ngendahotel.com'
        has_real_password = self.auth_password and self.auth_password != 'website-service-account-2026'
        has_real_url = self.base_url and 'localhost' not in self.base_url
        
        # If we have real credentials and modules are available, use real HMS
        if REQUESTS_AVAILABLE and (has_real_email or has_real_password or has_real_url):
            print("Production credentials detected - using real HMS")
            return True
        elif REQUESTS_AVAILABLE:
            print("Using development credentials - real HMS available")
            return True
        else:
            print("Missing dependencies or credentials - using mock mode")
            return False
        
    def authenticate(self):
        """Perform authentication with HMS and store JWT token"""
        if not self.should_use_real_hms or not REQUESTS_AVAILABLE:
            print("Using mock authentication (real HMS not available)")
            return self._create_mock_token()
            
        with self.auth_lock:
            try:
                print(f"Authenticating with HMS as {self.auth_email}")
                print(f"Auth URL: {self.base_url}{self.auth_endpoint}")
                
                auth_payload = {
                    'email': self.auth_email,
                    'password': self.auth_password,
                    'hotel_id': self.hotel_id  # Include hotel_id in auth request
                }
                
                print(f"Auth payload: {auth_payload}")
                
                response = requests.post(
                    f"{self.base_url}{self.auth_endpoint}",
                    json=auth_payload,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                print(f"Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        auth_data = response.json()
                        print(f"Parsed auth response: {auth_data}")
                        
                        # Check for access_token key (HMS returns token as 'access_token')
                        if 'access_token' in auth_data:
                            self.jwt_token = auth_data['access_token']
                            expires_in = auth_data.get('expires_in', 3600)  # Default 1 hour
                            
                            # Decode token to get expiry (if possible)
                            try:
                                decoded = jwt.decode(self.jwt_token, options={"verify_signature": False})
                                exp_timestamp = decoded.get('exp')
                                if exp_timestamp:
                                    self.token_expires_at = datetime.fromtimestamp(exp_timestamp)
                                else:
                                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                            except:
                                # Fallback if JWT decode fails
                                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                            
                            # Confirm token storage
                            print(f"Successfully stored JWT token: {self.jwt_token[:10]}...")
                            print(f"Token expires at: {self.token_expires_at}")
                            
                            # Log successful connection
                            print(f"[HMS-SYNC] Connected as {self.auth_email} for Hotel ID {self.hotel_id}")
                            print(f"Authentication successful. Token expires at: {self.token_expires_at}")
                            return True
                        else:
                            print(f"❌ Token not found in response. Available keys: {list(auth_data.keys())}")
                            print(f"Full auth response: {auth_data}")
                            return False
                            
                    except ValueError as e:
                        print(f"Failed to parse JSON response: {e}")
                        print(f"Raw response text: {response.text}")
                        return False
                        
                elif response.status_code == 401:
                    print("❌ 401 Unauthorized - Authentication credentials rejected")
                    print("Check: Email/Password combination or user permissions")
                    return False
                    
                elif response.status_code == 404:
                    print("❌ 404 Not Found - Login endpoint not found")
                    print(f"Check: URL path - {self.base_url}{self.auth_endpoint}")
                    print("Possible issues:")
                    print("- Wrong endpoint path (missing/extra slash)")
                    print("- HMS server not running")
                    print("- Wrong base URL")
                    return False
                    
                elif response.status_code == 500:
                    print("❌ 500 Internal Server Error - HMS server crashed")
                    print("Check: HMS server logs for crash details")
                    return False
                    
                else:
                    print(f"❌ Unexpected status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
            except requests.exceptions.ConnectionError as e:
                print(f"❌ Connection Error: {e}")
                print("Check: HMS server is running and accessible")
                print(f"Attempted URL: {self.base_url}{self.auth_endpoint}")
                return False
                
            except requests.exceptions.Timeout as e:
                print(f"❌ Timeout Error: {e}")
                print("Check: HMS server response time or network connectivity")
                return False
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Request Error: {e}")
                print("Check: Network connectivity and HMS server status")
                return False
                
            except Exception as e:
                print(f"❌ Unexpected Authentication Error: {e}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return False
    
    def _create_mock_token(self):
        """Create mock JWT token for development"""
        with self.auth_lock:
            self.jwt_token = "mock_jwt_token_for_development"
            self.token_expires_at = datetime.now() + timedelta(hours=1)
            print(f"[HMS-SYNC] Mock connection as {self.auth_email} for Hotel ID {self.hotel_id}")
            return True
    
    def get_valid_token(self):
        """Get a valid JWT token, refreshing if necessary"""
        # Check if we need to authenticate or refresh
        if not self._is_token_valid():
            print("Token invalid or expired, re-authenticating...")
            if not self.authenticate():
                print("Authentication failed, using mock token")
                self._create_mock_token()
        
        return self.jwt_token
    
    def _is_token_valid(self):
        """Check if current token is valid and not expired"""
        if not self.jwt_token or not self.token_expires_at:
            return False
        
        # Check if token expires within refresh buffer
        refresh_time = self.token_expires_at - timedelta(minutes=self.refresh_buffer_minutes)
        
        if datetime.now() >= refresh_time:
            print("Token approaching expiry, will refresh")
            return False
            
        return True
    
    def get_auth_headers(self):
        """Get authorization headers with valid JWT token"""
        token = self.get_valid_token()
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-API-Version': 'v1',
            'X-Source': 'ngenda-website',
            'X-Hotel-ID': self.hotel_id
        }
    
    def force_refresh_token(self):
        """Force immediate token refresh - called when 401 is received"""
        print("Forcing immediate token refresh due to 401 Unauthorized")
        with self.auth_lock:
            self.jwt_token = None
            self.token_expires_at = None
        return self.authenticate()
    
    def start_background_refresh(self):
        """Start background thread to automatically refresh token"""
        def refresh_worker():
            while True:
                try:
                    time.sleep(60)  # Check every minute
                    if not self._is_token_valid():
                        print("Background refresh: Re-authenticating...")
                        self.authenticate()
                except Exception as e:
                    print(f"Background refresh error: {e}")
                    time.sleep(30)  # Wait before retry
        
        refresh_thread = Thread(target=refresh_worker, daemon=True)
        refresh_thread.start()
        print("Background token refresh thread started")
    
    def initialize_on_startup(self):
        """Initialize authentication on application startup"""
        print("Initializing HMS authentication on startup...")
        
        # Perform initial authentication
        if self.authenticate():
            print("Initial authentication successful")
            # Start background refresh thread
            self.start_background_refresh()
        else:
            print("Initial authentication failed, using mock mode")
            self._create_mock_token()
            self.start_background_refresh()

# Global auth service instance
_auth_service = None

def get_auth_service():
    """Get or create global auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = HMSAuthService()
    return _auth_service

def initialize_hms_auth():
    """Initialize HMS authentication (call this on app startup)"""
    auth_service = get_auth_service()
    auth_service.initialize_on_startup()
    return auth_service
