# HMS Background Authentication Implementation

## Overview
The Ngenda Hotel website now implements a Background Auth pattern for HMS integration, allowing guests to make bookings without requiring login while maintaining secure API communication.

## Architecture

### 1. HMSAuthService (`auth_service.py`)
**Purpose**: Handles JWT authentication with HMS in the background

**Key Features**:
- **Startup Authentication**: Logs in as `website-bot@ngendahotel.com` on application startup
- **Token Storage**: Keeps JWT token in memory with expiry tracking
- **Auto-Refresh**: Automatically re-authenticates 5 minutes before token expiry
- **Background Thread**: Runs a daemon thread to monitor and refresh tokens
- **Fallback**: Provides mock tokens for development when HMS is unavailable

**Key Methods**:
- `authenticate()`: Performs login with HMS and stores JWT token
- `get_valid_token()`: Returns valid token, refreshing if necessary
- `get_auth_headers()`: Returns complete headers with valid JWT token
- `start_background_refresh()`: Starts automatic token refresh thread

### 2. Updated HotelAPIService (`api_service.py`)
**Changes**:
- Integrates with `HMSAuthService` for authentication
- All API calls now use JWT tokens instead of static API keys
- Automatic token refresh before each API call
- Maintains fallback to mock data when HMS is unavailable

### 3. Flask App Integration (`app.py`)
**Changes**:
- Initializes HMS authentication on application startup
- Authentication happens before any routes are served
- Background refresh thread starts automatically

## Authentication Flow

### Startup Process
1. Flask application starts
2. `initialize_hms_auth()` is called
3. HMSAuthService performs login with credentials:
   - Email: `website-bot@ngendahotel.com`
   - Password: From environment variable
4. JWT token is stored in memory with expiry time
5. Background refresh thread starts

### API Request Process
1. Guest makes booking request
2. `HotelAPIService` calls `auth_service.get_auth_headers()`
3. Auth service checks if token is valid (not expired within 5-minute buffer)
4. If invalid, automatically re-authenticates
5. Returns headers with valid JWT token
6. API request is made with JWT authentication

### Token Refresh Process
1. Background thread checks token validity every 60 seconds
2. If token expires within 5 minutes, automatic re-authentication occurs
3. New token is stored in memory
4. Process continues seamlessly

## Configuration

### Environment Variables
```bash
# HMS API Configuration
HMS_API_URL=http://localhost:8000/api
HMS_AUTH_EMAIL=website-bot@ngendahotel.com
HMS_AUTH_PASSWORD=Ngenda@2024!
```

### Required Dependencies
```txt
Flask==2.3.3
PyJWT==2.8.0
requests==2.31.0
```

## Security Features

### 1. No Guest Authentication Required
- Guests interact with website normally
- No login forms or authentication prompts
- Seamless booking experience

### 2. Secure Backend Authentication
- Website authenticates as service account
- JWT tokens with expiration
- Automatic token refresh prevents expired tokens

### 3. Fallback Mechanisms
- Mock tokens for development
- Graceful degradation when HMS is offline
- Error handling with fallback responses

### 4. Thread Safety
- Lock mechanisms for token updates
- Thread-safe token storage and refresh
- Prevents race conditions during authentication

## Benefits

### For Guests
- **No Login Required**: Book directly without account creation
- **Fast Experience**: No authentication delays
- **Mobile Friendly**: Works seamlessly on all devices

### For Operations
- **Centralized Authentication**: Single service account for website
- **Automatic Management**: No manual token refresh required
- **Monitoring**: Built-in logging for authentication events

### For Security
- **JWT Tokens**: Industry-standard authentication
- **Auto-Refresh**: Prevents token expiration issues
- **Service Account**: Limited permissions for website operations

## Error Handling

### Authentication Failures
- Falls back to mock tokens
- Continues operation with mock data
- Logs authentication errors for debugging

### Network Issues
- Automatic retry with exponential backoff
- Graceful degradation to mock mode
- Maintains website functionality

### Token Expiry
- Proactive refresh 5 minutes before expiry
- Background monitoring prevents expired tokens
- Seamless token replacement

## Development vs Production

### Development
- Uses mock tokens when HMS is unavailable
- Detailed logging for debugging
- Fallback to mock data for testing

### Production
- Real HMS authentication required
- Monitoring and alerting for auth failures
- High availability with automatic recovery

## Monitoring

The system provides detailed logging for:
- Authentication attempts and results
- Token refresh events
- API request failures
- Fallback activations

## Future Enhancements

1. **Health Checks**: API endpoint to verify authentication status
2. **Metrics**: Authentication success/failure rates
3. **Alerting**: Notifications for authentication failures
4. **Caching**: Redis-based token storage for scalability
5. **Multi-Service**: Support for multiple HMS instances
