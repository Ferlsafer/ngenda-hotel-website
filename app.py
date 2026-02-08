from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from config import config
from api_service import HotelAPIService
from auth_service import initialize_hms_auth
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Flask app
def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize API service
    api_service = HotelAPIService(app.config['HMS_API_URL'])
    
    # Initialize HMS authentication on startup with production credentials
    print("Initializing HMS authentication with production settings...")
    auth_service = initialize_hms_auth()
    
    # Log successful initialization
    print(f"Flask app initialized for {app.config['HOTEL_NAME']} ({app.config['HOTEL_LOCATION']})")
    print(f"HMS API URL: {app.config['HMS_API_URL']}")
    print(f"Hotel ID: {app.config['HMS_HOTEL_ID']}")
    
    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Will be updated
    app.config['MAIL_PASSWORD'] = 'your-app-password'   # Will be updated
    app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
    
    def send_contact_email(name, email, message):
        """Send contact form email"""
        try:
            # Email configuration for Ngenda Hotel
            # Note: You'll need to configure SMTP settings for info@ngendahotel.co.tz
            sender_email = 'info@ngendahotel.co.tz'  # Hotel email as sender
            sender_password = 'hotel-email-password'  # Hotel email password
            
            # Send to hotel email
            recipient_email = 'info@ngendahotel.co.tz'
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            
            # Handle single or multiple recipients
            if isinstance(recipient_email, list):
                msg['To'] = ', '.join(recipient_email)
            else:
                msg['To'] = recipient_email
                
            msg['Subject'] = f'New Contact Form Submission from {name}'
            
            # Email body
            body = f"""
            New Contact Form Submission
            
            Name: {name}
            Email: {email}
            
            Message:
            {message}
            
            ---
            This message was sent from the Ngenda Hotel & Apartments contact form.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            
            # Handle single or multiple recipients
            if isinstance(recipient_email, list):
                server.sendmail(sender_email, recipient_email, text)
            else:
                server.sendmail(sender_email, recipient_email, text)
                
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    # Main routes
    @app.route('/')
    def index():
        """Render the home page"""
        # Get rooms from API service with fallback data
        try:
            rooms_data = api_service.get_available_rooms()
            if not rooms_data:
                # Fallback hardcoded rooms if API returns empty
                rooms_data = [
                    {
                        'id': 1,
                        'name': 'Classic Balcony Room',
                        'price': 299000,
                        'currency': 'TZS',
                        'category': 'classic',
                        'image': 'Room.jpg',
                        'size': '30m²',
                        'capacity': 3,
                        'beds': 'balcony'
                    },
                    {
                        'id': 2,
                        'name': 'Superior Double Room',
                        'price': 399000,
                        'currency': 'TZS',
                        'category': 'superior',
                        'image': 'room1.jpg',
                        'size': '35m²',
                        'capacity': 3,
                        'beds': 'double'
                    },
                    {
                        'id': 3,
                        'name': 'Executive Master Suite',
                        'price': 450000,
                        'currency': 'TZS',
                        'category': 'executive',
                        'image': 'room3.jpg',
                        'size': '55m²',
                        'capacity': 2,
                        'beds': 'king'
                    },
                    {
                        'id': 4,
                        'name': 'Deluxe Double Room',
                        'price': 350000,
                        'currency': 'TZS',
                        'category': 'deluxe',
                        'image': 'room2.jpg',
                        'size': '40m²',
                        'capacity': 2,
                        'beds': 'double'
                    },
                    {
                        'id': 5,
                        'name': 'Premium Garden View',
                        'price': 320000,
                        'currency': 'TZS',
                        'category': 'superior',
                        'image': 'room5.JPG',
                        'size': '32m²',
                        'capacity': 3,
                        'beds': 'double'
                    }
                ]
        except Exception as e:
            print(f"Error fetching rooms: {e}")
            # Use fallback data if API service fails
            rooms_data = [
                {
                    'id': 1,
                    'name': 'Classic Balcony Room',
                    'price': 299000,
                    'currency': 'TZS',
                    'category': 'classic',
                    'image': 'Room.jpg',
                    'size': '30m²',
                    'capacity': 3,
                    'beds': 'balcony'
                },
                {
                    'id': 2,
                    'name': 'Superior Double Room',
                    'price': 399000,
                    'currency': 'TZS',
                    'category': 'superior',
                    'image': 'room1.jpg',
                    'size': '35m²',
                    'capacity': 3,
                    'beds': 'double'
                },
                {
                    'id': 3,
                    'name': 'Executive Master Suite',
                    'price': 450000,
                    'currency': 'TZS',
                    'category': 'executive',
                    'image': 'room3.jpg',
                    'size': '55m²',
                    'capacity': 2,
                    'beds': 'king'
                },
                {
                    'id': 4,
                    'name': 'Deluxe Double Room',
                    'price': 350000,
                    'currency': 'TZS',
                    'category': 'deluxe',
                    'image': 'room2.jpg',
                    'size': '40m²',
                    'capacity': 2,
                    'beds': 'double'
                },
                {
                    'id': 5,
                    'name': 'Premium Garden View',
                    'price': 320000,
                    'currency': 'TZS',
                    'category': 'superior',
                    'image': 'room5.JPG',
                    'size': '32m²',
                    'capacity': 3,
                    'beds': 'double'
                }
            ]
        
        return render_template('index.html', rooms=rooms_data)
    
    @app.route('/room_detail/<int:room_id>')
    def room_detail(room_id):
        """Render individual room detail page"""
        try:
            rooms_data = api_service.get_available_rooms()
            room = next((r for r in rooms_data if r['id'] == room_id), None)
            
            if not room:
                flash('Room not found', 'error')
                return redirect(url_for('index'))
            
            # Get similar rooms (same category, excluding current room)
            similar_rooms = [r for r in rooms_data if r['category'] == room['category'] and r['id'] != room_id][:3]
            
            return render_template('room_detail.html', room=room, similar_rooms=similar_rooms)
        except Exception as e:
            flash(f'Error loading room details: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    @app.route('/about')
    def about():
        """Render about page"""
        return render_template('about-1.html')
    
    @app.route('/gallery')
    def gallery():
        """Render gallery page"""
        return render_template('gallery-fixed.html')
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Render the contact page and handle form submission"""
        if request.method == 'POST':
            try:
                # Get form data
                name = request.form.get('username', '').strip()
                email = request.form.get('email', '').strip()
                message = request.form.get('message', '').strip()
                
                # Validate form data
                if not name or not email or not message:
                    flash('Please fill in all required fields.', 'error')
                    return render_template('contact-1.html')
                
                # Validate email format
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    flash('Please enter a valid email address.', 'error')
                    return render_template('contact-1.html')
                
                # Send email
                send_contact_email(name, email, message)
                flash('Thank you for your message! We will get back to you soon.', 'success')
                
            except Exception as e:
                flash(f'Sorry, there was an error sending your message. Please try again. Error: {str(e)}', 'error')
        
        return render_template('contact-1.html')
    
    @app.route('/services')
    def services():
        """Render services detail page"""
        return render_template('service-details.html')
    
    @app.route('/faq')
    def faq():
        """Render FAQ page"""
        return render_template('faq.html')
    
    # Room routes with API integration
    @app.route('/rooms')
    def rooms():
        """Render rooms page with dynamic room data"""
        try:
            rooms_data = api_service.get_available_rooms()
            return render_template('rooms.html', rooms=rooms_data)
        except Exception as e:
            flash(f'Error loading rooms: {str(e)}', 'error')
            return render_template('rooms.html', rooms=[])
    
    # Booking routes
    @app.route('/book', methods=['POST'])
    def create_booking():
        """Handle booking form submission"""
        try:
            booking_data = {
                'guest_name': request.form.get('guest_name'),
                'guest_email': request.form.get('guest_email'),
                'guest_phone': request.form.get('guest_phone'),
                'room_id': request.form.get('room_id'),  # Add room_id extraction
                'room_type': request.form.get('room_type'),
                'check_in': request.form.get('check_in'),
                'check_out': request.form.get('check_out'),
                'guests': int(request.form.get('guests', 1)),
                'special_requests': request.form.get('special_requests', '')
            }
            
            # Validate required fields
            required_fields = ['guest_name', 'guest_email', 'guest_phone', 'room_id', 'room_type', 'check_in', 'check_out']
            for field in required_fields:
                if not booking_data.get(field):
                    return jsonify({'success': False, 'message': f'{field} is required'}), 400
            
            # Create booking via API
            result = api_service.create_booking(booking_data)
            
            if result.get('success'):
                flash('Booking created successfully! Your booking ID is: ' + result.get('booking_id', ''), 'success')
                return jsonify({'success': True, 'booking_id': result.get('booking_id')})
            else:
                return jsonify({'success': False, 'message': result.get('message', 'Booking failed')}), 400
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/booking-success/<booking_id>')
    def booking_success(booking_id):
        """Render booking success page"""
        return render_template('booking-success.html', booking_id=booking_id)
    
    # Legacy routes (keeping existing ones)
    @app.route('/room-detail')
    def room_detail_legacy():
        """Legacy room detail route"""
        return render_template('room-detail.html')
    
    @app.route('/service-details')
    def service_details():
        """Render the service details page"""
        return render_template('service-details.html')
    
    @app.route('/project-detail')
    def project_detail():
        """Render the project detail page"""
        return render_template('project-detail.html')
    
    # Blog routes
    @app.route('/blog')
    def blog():
        """Render the blog grid page"""
        return render_template('news-grid.html')
    
    @app.route('/blog/<post_type>')
    def blog_post(post_type):
        """Render different blog post types"""
        if post_type == 'image':
            return render_template('post-image.html')
        elif post_type == 'gallery':
            return render_template('post-gallery.html')
        elif post_type == 'video':
            return render_template('post-video.html')
        elif post_type == 'right-sidebar':
            return render_template('post-right-sidebar.html')
        else:
            return render_template('post-gallery.html')
    
    # API endpoints for AJAX calls
    @app.route('/api/rooms')
    def api_rooms():
        """API endpoint to get rooms data"""
        try:
            rooms_data = api_service.get_available_rooms()
            return jsonify({'success': True, 'rooms': rooms_data})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
