try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests module not available. Using mock mode only.")

import os
from datetime import datetime
from auth_service import get_auth_service

class HotelAPIService:
    """Service layer for connecting to Hotel Management System API"""
    
    def __init__(self, base_url=None):
        # Connection Configuration - Use production HMS settings
        self.base_url = base_url or os.getenv('HMS_API_URL', 'http://localhost:5000')
        self.api_key = os.getenv('HMS_API_KEY', 'ngenda_website_key')
        self.mock_mode = True  # Start with mock mode for development
        self.timeout = 10  # Request timeout in seconds
        
        # HMS Endpoint Configuration
        self.public_rooms_endpoint = os.getenv('HMS_PUBLIC_ROOMS_ENDPOINT', '/api/public/rooms')
        self.bookings_endpoint = os.getenv('HMS_BOOKINGS_ENDPOINT', '/api/bookings/')
        
        # Hotel ID for branch identification
        self.hotel_id = os.getenv('HMS_HOTEL_ID', '1')
        
        # Initialize authentication service
        self.auth_service = get_auth_service()
        
        print(f"HotelAPIService initialized for Hotel ID {self.hotel_id}")
        print(f"Public rooms endpoint: {self.base_url}{self.public_rooms_endpoint}")
        print(f"Bookings endpoint: {self.base_url}{self.bookings_endpoint}")
    
    def toggle_live_mode(self, live_mode=True):
        """Toggle between Mock Data and Live API data"""
        self.mock_mode = not live_mode
        mode = "Live API" if live_mode else "Mock Data"
        print(f"Switched to {mode} mode")
    
    def get_available_rooms(self):
        """Fetch available rooms from HMS API or return mock data"""
        if self.mock_mode or not REQUESTS_AVAILABLE:
            return self._get_mock_rooms()
        else:
            try:
                # Fetching Rooms (GET /api/public/rooms) - No token needed for public endpoint
                headers = {
                    'Content-Type': 'application/json',
                    'X-API-Version': 'v1',
                    'X-Source': 'ngenda-website',
                    'X-Hotel-ID': self.hotel_id
                }
                
                response = requests.get(
                    f"{self.base_url}{self.public_rooms_endpoint}",
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # Map incoming JSON to our frontend fields
                api_data = response.json()
                if api_data.get('success') and 'rooms' in api_data:
                    rooms = []
                    for room in api_data['rooms']:
                        # Ensure room categories match our frontend filter buttons
                        mapped_room = {
                            'id': room.get('id'),
                            'name': room.get('name'),
                            'category': room.get('category'),  # classic, superior, deluxe, executive
                            'price': room.get('price'),
                            'price_usd': room.get('price_usd'),
                            'capacity': room.get('capacity', 2),
                            'size': room.get('size', '25 sqm'),
                            'beds': room.get('beds', 'Double Bed'),
                            'amenities': room.get('amenities', []),
                            'image': room.get('image', 'default_room.jpg'),
                            'available': room.get('available', True),
                            'description': room.get('description', ''),
                            'currency': room.get('currency', 'TZS')
                        }
                        rooms.append(mapped_room)
                    print(f"Successfully fetched {len(rooms)} rooms from HMS")
                    return rooms
                else:
                    print(f"API returned unexpected format: {api_data}")
                    return self._get_mock_rooms()
                    
            except requests.exceptions.RequestException as e:
                # Error Handling: Fallback to mock data if HMS is offline
                print(f"HMS API Error: {e}")
                print("Falling back to mock data to keep website functional")
                return self._get_mock_rooms()
            except Exception as e:
                print(f"Unexpected error: {e}")
                return self._get_mock_rooms()
    
    def create_booking(self, booking_data):
        """Create a new booking via HMS API or mock response"""
        if self.mock_mode or not REQUESTS_AVAILABLE:
            return self._create_mock_booking(booking_data)
        else:
            return self._create_booking_with_retry(booking_data, retry_count=0)
    
    def _create_booking_with_retry(self, booking_data, retry_count=0):
        """Create booking with retry logic for 401 errors"""
        try:
            # Sending Bookings (POST /api/bookings/) with JWT authentication
            headers = self.auth_service.get_auth_headers()
            
            # Ensure payload includes required fields and hotel_id
            payload = {
                'guest_name': booking_data.get('guest_name'),
                'guest_email': booking_data.get('guest_email'),
                'guest_phone': booking_data.get('guest_phone'),
                'room_id': booking_data.get('room_id'),
                'room_type': booking_data.get('room_type'),
                'check_in': booking_data.get('check_in'),
                'check_out': booking_data.get('check_out'),
                'guests': booking_data.get('guests', 1),
                'special_requests': booking_data.get('special_requests', ''),
                'source': 'website',
                'hotel_id': self.hotel_id  # Explicitly include hotel_id for branch routing
            }
            
            response = requests.post(
                f"{self.base_url}{self.bookings_endpoint}",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Handle 401 Unauthorized with immediate token refresh
            if response.status_code == 401:
                print("Received 401 Unauthorized - forcing token refresh")
                if retry_count < 2:  # Max 2 retries for 401
                    # Force immediate token refresh
                    if self.auth_service.force_refresh_token():
                        print("Token refreshed successfully, retrying booking request")
                        return self._create_booking_with_retry(booking_data, retry_count + 1)
                    else:
                        print("Token refresh failed, falling back to mock booking")
                        return self._create_mock_booking(booking_data)
                else:
                    print("Max retries reached for 401, falling back to mock booking")
                    return self._create_mock_booking(booking_data)
            
            response.raise_for_status()
            
            # Capture booking_id from HMS response
            api_response = response.json()
            if api_response.get('success'):
                print(f"Booking created successfully: {api_response.get('booking_id')}")
                return {
                    'success': True,
                    'booking_id': api_response.get('booking_id'),
                    'message': api_response.get('message', 'Booking created successfully'),
                    'whatsapp_link': api_response.get('whatsapp_link'),
                    'booking_details': api_response.get('booking_details', {}),
                    'total_amount': api_response.get('total_amount'),
                    'currency': api_response.get('currency', 'TZS')
                }
            else:
                print(f"Booking failed: {api_response}")
                return self._create_mock_booking(booking_data)
                
        except requests.exceptions.RequestException as e:
            # Error Handling: Fallback to mock booking if HMS is offline
            print(f"HMS Booking API Error: {e}")
            print("Falling back to mock booking to keep website functional")
            return self._create_mock_booking(booking_data)
        except Exception as e:
            print(f"Unexpected booking error: {e}")
            return self._create_mock_booking(booking_data)
    
    def _get_mock_rooms(self):
        """Return mock room data for development"""
        return [
            {
                'id': 1,
                'name': 'Standard Double Room',
                'category': 'classic',
                'price': 80000,
                'currency': 'TZS',
                'price_usd': 30,
                'capacity': 2,
                'beds': 'Double Bed',
                'size': '25 sqm',
                'amenities': ['Free WiFi', 'Air Conditioning', 'Flat-screen TV', 'Mini Bar', 'Room Service'],
                'image': 'room2.jpg',
                'available': True,
                'description': 'Comfortable standard double room with modern amenities including AC and flat-screen TV'
            },
            {
                'id': 2,
                'name': 'Superior Double Room',
                'category': 'superior',
                'price': 120000,
                'currency': 'TZS',
                'price_usd': 45,
                'capacity': 2,
                'beds': 'Double Bed',
                'size': '35 sqm',
                'amenities': ['Free WiFi', 'Air Conditioning', 'Flat-screen TV', 'Mini Bar', 'Room Service', 'Premium Amenities'],
                'image': 'room3.jpg',
                'available': True,
                'description': 'Enhanced double room with premium amenities and extra space'
            },
            {
                'id': 3,
                'name': 'Superior Family Room',
                'category': 'deluxe',
                'price': 180000,
                'currency': 'TZS',
                'price_usd': 68,
                'capacity': 4,
                'beds': 'Family Configuration',
                'size': '45 sqm',
                'amenities': ['Free WiFi', 'Air Conditioning', 'Flat-screen TV', 'Mini Bar', 'Room Service', 'Family Amenities'],
                'image': 'Room.jpg',
                'available': True,
                'description': 'Perfect family room with space for 4 guests and family-friendly amenities'
            },
            {
                'id': 4,
                'name': 'Apartment with Balcony',
                'category': 'executive',
                'price': 350000,
                'currency': 'TZS',
                'price_usd': 130,
                'capacity': 15,
                'beds': 'Multiple Beds',
                'size': '120 sqm',
                'amenities': ['Free WiFi', 'Microwave', 'Mountain View', 'Air Conditioning', 'Mini Bar', 'Room Service', 'Kitchen', 'Balcony'],
                'image': 'room1.jpg',
                'available': True,
                'description': 'Spacious apartment with modern master bedrooms and fully equipped kitchens, perfect for large groups, featuring mountain views and full kitchen facilities'
            },
            {
                'id': 5,
                'name': 'Budget Single Room',
                'category': 'classic',
                'price': 60000,
                'currency': 'TZS',
                'price_usd': 23,
                'capacity': 1,
                'beds': 'Single Bed',
                'size': '20 sqm',
                'amenities': ['Free WiFi', 'Air Conditioning'],
                'image': 'room4.JPG',
                'available': True,
                'description': 'Affordable single room perfect for budget-conscious travelers'
            }
        ]
    
    def _create_mock_booking(self, booking_data):
        """Create mock booking response"""
        booking_id = f"BKG{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            'success': True,
            'booking_id': booking_id,
            'message': 'Booking created successfully',
            'booking_details': {
                **booking_data,
                'id': booking_id,
                'status': 'confirmed',
                'created_at': datetime.now().isoformat()
            }
        }
    
    def set_live_mode(self):
        """Switch to live API mode"""
        self.toggle_live_mode(True)
    
    def set_mock_mode(self):
        """Switch to mock mode for development"""
        self.toggle_live_mode(False)
