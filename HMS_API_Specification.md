# HMS API Specification for Ngenda Hotel & Apartments

## 🎯 **Project Overview**
**Client**: Ngenda Hotel & Apartments Website (Flask Application)
**Developer**: WindSurf (HMS Development Team)
**Integration**: Real-time booking synchronization between website and Hotel Management System

---

## 📋 **Required API Endpoints**

### **1. Rooms Management**
```
GET /api/rooms
Description: Retrieve all available rooms
Response Format:
{
    "success": true,
    "rooms": [
        {
            "id": 1,
            "name": "Standard Double Room",
            "category": "classic",
            "price": 80000,
            "price_usd": 30,
            "size": "25m²",
            "capacity": 2,
            "image": "room1.jpg",
            "amenities": ["AC", "Netflix", "WiFi"],
            "available": true,
            "description": "Comfortable room with modern amenities"
        }
    ]
}

GET /api/rooms/{room_id}
Description: Retrieve specific room details
Response Format:
{
    "success": true,
    "room": {
        "id": 1,
        "name": "Standard Double Room",
        "category": "classic",
        "price": 80000,
        "price_usd": 30,
        "size": "25m²",
        "capacity": 2,
        "image": "room1.jpg",
        "amenities": ["AC", "Netflix", "WiFi"],
        "available": true,
        "description": "Comfortable room with modern amenities",
        "gallery": ["room1.jpg", "room1b.jpg", "room1c.jpg"]
    }
}
```

### **2. Real-time Availability**
```
GET /api/availability
Description: Check real-time room availability
Query Parameters:
- room_id (optional): Specific room ID
- check_in (required): Check-in date (YYYY-MM-DD)
- check_out (required): Check-out date (YYYY-MM-DD)
- guests (optional): Number of guests

Response Format:
{
    "success": true,
    "availability": {
        "room_id": 1,
        "status": "available", // "available", "sold_out", "maintenance"
        "available_dates": ["2024-03-20", "2024-03-21"],
        "total_rooms": 5,
        "booked_rooms": 2
    },
    "last_updated": "2024-03-15T10:30:00Z"
}

CRITICAL REQUIREMENT: Real-time sync - if walk-in guest books at physical hotel desk, website must instantly show room as "sold_out"
```

### **3. Booking Management**
```
POST /api/bookings
Description: Create new booking
Request Format:
{
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "guest_phone": "+255123456789",
    "room_type": "Standard Double Room",
    "room_id": 1,
    "check_in": "2024-03-15",
    "check_out": "2024-03-17",
    "guests": 2,
    "special_requests": "Late check-in requested",
    "source": "website" // Identify booking source
}

Response Format:
{
    "success": true,
    "booking_id": "BKG20240315123456",
    "message": "Booking created successfully",
    "status": "confirmed",
    "total_amount": 80000,
    "currency": "TZS",
    "whatsapp_link": "https://wa.me/255745765119?text=Booking%20confirmed%3A%20BKG20240315123456%20for%20Ngenda%20Hotel",
    "booking_details": {
        "guest_name": "John Doe",
        "room_type": "Standard Double Room",
        "check_in": "2024-03-15",
        "check_out": "2024-03-17",
        "guests": 2,
        "special_requests": "Late check-in requested"
    },
    "created_at": "2024-03-15T14:30:00Z"
}

GET /api/bookings/{booking_id}
Description: Retrieve booking details
Response Format:
{
    "success": true,
    "booking": {
        "id": "BKG20240315123456",
        "status": "confirmed", // "confirmed", "pending", "cancelled", "checked_in", "checked_out"
        "guest_name": "John Doe",
        "room_type": "Standard Double Room",
        "check_in": "2024-03-15",
        "check_out": "2024-03-17",
        "total_amount": 80000,
        "currency": "TZS",
        "created_at": "2024-03-15T14:30:00Z",
        "modified_at": "2024-03-15T15:45:00Z"
    }
}

PUT /api/bookings/{booking_id}
Description: Modify existing booking
Request Format: Same as POST /api/bookings (only fields to modify)

Response Format:
{
    "success": true,
    "message": "Booking updated successfully",
    "booking": { /* Updated booking details */ }
}

DELETE /api/bookings/{booking_id}
Description: Cancel booking
Response Format:
{
    "success": true,
    "message": "Booking cancelled successfully",
    "cancellation_policy": "Free cancellation up to 24 hours before check-in"
}
```

### **4. Guest Management**
```
GET /api/guests/{guest_id}
Description: Retrieve guest booking history
Response Format:
{
    "success": true,
    "guest": {
        "id": 123,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+255123456789",
        "total_bookings": 5,
        "loyalty_points": 150
    }
}

POST /api/guests
Description: Register new guest
Request Format:
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+255123456789",
    "password": "hashed_password",
    "preferences": {
        "room_type": "deluxe",
        "newsletter": true
    }
}
```

---

## 🔧 **Technical Requirements**

### **1. Authentication & Security**
```
Headers Required:
- Authorization: Bearer {api_token}
- Content-Type: application/json
- X-API-Version: v1

Rate Limiting:
- 100 requests per minute per IP
- 1000 requests per hour per IP
- Burst: 200 requests per 10 seconds

API Keys:
- Production: Provide secure API keys
- Development: Use test keys for sandbox
```

### **2. Real-time Features**
```
WebSocket Integration (Optional but Recommended):
- Endpoint: ws://hms.ngendahotel.com/ws/availability
- Purpose: Instant room status updates
- Events: "room_available", "room_sold_out", "room_maintenance"

Webhook Support:
- Endpoint: POST /api/webhooks/room-status
- Purpose: Receive instant updates from HMS
- Authentication: HMAC signature verification
```

### **3. Data Synchronization**
```
Inventory Sync:
- Frequency: Every 30 seconds or on change
- Method: Polling or WebSocket
- Fallback: Manual refresh button on website

Conflict Resolution:
- Double booking prevention
- Real-time availability checking
- Automatic status updates
```

### **4. Currency & Pricing**
```
Multi-Currency Support:
- Default currency: TZS
- Supported currencies: TZS, USD, EUR
- Exchange rates: Update daily from central bank

Pricing Structure:
{
    "room_rate": 80000,
    "currency": "TZS",
    "usd_equivalent": 30,
    "seasonal_pricing": {
        "peak_season_multiplier": 1.2,
        "off_season_multiplier": 0.8
    }
}
```

---

## 🚀 **Integration Instructions**

### **For WindSurf Development Team**

#### **Step 1: API Base URL**
```
Development: http://localhost:8000/api
Staging: https://staging.hms.ngendahotel.com/api
Production: https://hms.ngendahotel.com/api
```

#### **Step 2: Environment Setup**
```bash
# HMS Configuration
export HMS_API_BASE_URL="https://hms.ngendahotel.com/api"
export HMS_API_KEY="your_production_api_key"
export HMS_WEBHOOK_SECRET="your_webhook_secret"
```

#### **Step 3: Testing Protocol**
```bash
# Test all endpoints
curl -X GET "https://hms.ngendahotel.com/api/rooms" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"

# Test booking creation
curl -X POST "https://hms.ngendahotel.com/api/bookings" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "guest_name": "Test User",
    "guest_email": "test@example.com",
    "room_type": "Standard Double Room",
    "check_in": "2024-03-15",
    "check_out": "2024-03-17"
  }'
```

### **For Website Integration**

#### **Step 1: Update Configuration**
```python
# config.py
HMS_API_URL = 'https://hms.ngendahotel.com/api'
HMS_API_KEY = 'your_production_api_key'
```

#### **Step 2: Switch to Live Mode**
```python
# app.py
api_service = HotelAPIService(app.config['HMS_API_URL'])
api_service.set_live_mode()
```

#### **Step 3: Update Booking Flow**
```python
# Handle WhatsApp integration
def create_booking():
    result = api_service.create_booking(booking_data)
    
    if result.get('success') and result.get('whatsapp_link'):
        # Store booking ID and WhatsApp link
        session['booking_id'] = result.get('booking_id')
        session['whatsapp_link'] = result.get('whatsapp_link')
        
        return jsonify({
            'success': True,
            'booking_id': result.get('booking_id'),
            'whatsapp_link': result.get('whatsapp_link')
        })
```

---

## 📞 **Error Handling**

### **HTTP Status Codes**
```
200: Success
201: Created
400: Bad Request
401: Unauthorized
404: Not Found
409: Conflict (double booking)
422: Validation Error
429: Too Many Requests
500: Internal Server Error
```

### **Error Response Format**
```json
{
    "success": false,
    "error": {
        "code": "ROOM_NOT_AVAILABLE",
        "message": "Room is no longer available",
        "details": "This room was just booked by another guest"
    },
    "timestamp": "2024-03-15T14:30:00Z"
}
```

---

## 📱 **WhatsApp Integration Details**

### **WhatsApp Link Generation**
```
Format: https://wa.me/255745765119?text={encoded_message}

Message Template:
"Booking Confirmed! 🏨 Your booking ID: {booking_id} for {room_type} at Ngenda Hotel. Check-in: {check_in}, Check-out: {check_out}. View details: {booking_url}"

Variables:
- booking_id: BKG20240315123456
- room_type: Standard Double Room
- check_in: 2024-03-15
- check_out: 2024-03-17
- booking_url: https://ngendahotel.com/booking/BKG20240315123456
```

---

## 🎯 **Success Criteria**

### **Phase 1: Core Functionality**
- [ ] All endpoints respond with correct data structures
- [ ] Real-time availability updates work instantly
- [ ] WhatsApp links generated correctly
- [ ] Multi-currency support implemented
- [ ] Error handling covers all edge cases

### **Phase 2: Integration Testing**
- [ ] Website can create bookings via HMS API
- [ ] Real-time sync between HMS and website
- [ ] WhatsApp confirmation flow works end-to-end
- [ ] Fallback to mock data when HMS is down

### **Phase 3: Production Ready**
- [ ] API documentation complete
- [ ] Performance testing completed
- [ ] Security audit passed
- [ ] Monitoring and logging implemented

---

## 📞 **Contact Information**

### **WindSurf Development Team**
- **Technical Lead**: [WindSurf Developer Name]
- **Email**: [developer@windsurf.com]
- **Phone**: [WindSurf Contact Number]
- **Project Repository**: [Git repo URL if available]

### **Ngenda Hotel Team**
- **Technical Contact**: [Hotel IT Manager]
- **Email**: info@ngendahotel.com
- **Phone**: +255671 271 247
- **Address**: Isyesye–Hayanga, Mbeya, Tanzania

---

## 🚀 **Next Steps**

1. **Review Specification**: Confirm all requirements meet your needs
2. **Environment Setup**: Provide HMS API credentials
3. **Development Timeline**: Agree on implementation schedule
4. **Testing Protocol**: Establish testing procedures
5. **Deployment Plan**: Plan production rollout

---

*Last Updated: February 2026*
*Version: 1.0*
