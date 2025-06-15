# import pymysql
# from pymysql import Error

# def get_db_connection():
#     try:
#         return pymysql.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="travelbus",
#             charset='utf8mb4',  # Added for Urdu support
#             cursorclass=pymysql.cursors.DictCursor
#         )
#     except Error as e:
#         print(f"DB Connection Error: {e}")  # Log to console
#         return None
import pymysql
from pymysql import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """
    Establish and return a database connection
    """
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'travelbus'),
            charset='utf8mb4',  # Support for Unicode characters including Urdu
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,  # Auto commit transactions
            connect_timeout=10,  # Connection timeout
            read_timeout=10,  # Read timeout
            write_timeout=10  # Write timeout
        )
        return connection
    except Error as e:
        print(f"Database Connection Error: {e}")
        return None

def test_connection():
    """
    Test the database connection
    """
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print("✅ Database connection successful!")
                return True
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
        finally:
            connection.close()
    else:
        print("❌ Failed to establish database connection")
        return False

def create_tables():
    """
    Create necessary tables if they don't exist
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # Create buses table
            create_buses_table = """
            CREATE TABLE IF NOT EXISTS buses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bus_name VARCHAR(255) NOT NULL,
                bus_type VARCHAR(100) NOT NULL,
                departure VARCHAR(255) NOT NULL,
                destination VARCHAR(255) NOT NULL,
                departure_time TIME NOT NULL,
                date DATE NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                rewards INT DEFAULT 0,
                facility_images TEXT,
                logo_url VARCHAR(500) DEFAULT '/static/images/default-bus.png',
                booking_url VARCHAR(500) DEFAULT '#',
                seats_total INT DEFAULT 40,
                seats_available INT DEFAULT 40,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_route_date (departure, destination, date),
                INDEX idx_departure_time (departure_time),
                INDEX idx_bus_name (bus_name),
                INDEX idx_bus_type (bus_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor.execute(create_buses_table)
            print("✅ Buses table created/verified successfully!")
            
            # Create bookings table for future use
            create_bookings_table = """
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bus_id INT NOT NULL,
                passenger_name VARCHAR(255) NOT NULL,
                passenger_phone VARCHAR(20) NOT NULL,
                passenger_email VARCHAR(255),
                seats_booked INT NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                booking_status ENUM('confirmed', 'cancelled', 'pending') DEFAULT 'pending',
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                travel_date DATE NOT NULL,
                FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE CASCADE,
                INDEX idx_passenger_phone (passenger_phone),
                INDEX idx_booking_date (booking_date),
                INDEX idx_travel_date (travel_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor.execute(create_bookings_table)
            print("✅ Bookings table created/verified successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    finally:
        connection.close()

def insert_sample_data():
    """
    Insert sample data for testing
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) as count FROM buses")
            result = cursor.fetchone()
            
            if result['count'] > 0:
                print("✅ Sample data already exists!")
                return True
            
            sample_buses = [
                {
                    'bus_name': 'Faisal Movers',
                    'bus_type': 'AC Sleeper',
                    'departure': 'Karachi',
                    'destination': 'Lahore',
                    'departure_time': '22:00:00',
                    'date': '2024-12-25',
                    'price': 3500.00,
                    'rewards': 175,
                    'facility_images': '["wifi.png", "ac.png", "entertainment.png"]',
                    'logo_url': '/static/images/faisal-movers.png',
                    'booking_url': 'https://example.com/book/faisal-movers'
                },
                {
                    'bus_name': 'Daewoo Express',
                    'bus_type': 'AC Business',
                    'departure': 'Islamabad',
                    'destination': 'Karachi',
                    'departure_time': '20:30:00',
                    'date': '2024-12-25',
                    'price': 4200.00,
                    'rewards': 210,
                    'facility_images': '["wifi.png", "ac.png", "charging.png"]',
                    'logo_url': '/static/images/daewoo.png',
                    'booking_url': 'https://example.com/book/daewoo'
                },
                {
                    'bus_name': 'Niazi Express',
                    'bus_type': 'AC Standard',
                    'departure': 'Lahore',
                    'destination': 'Islamabad',
                    'departure_time': '14:00:00',
                    'date': '2024-12-25',
                    'price': 2800.00,
                    'rewards': 140,
                    'facility_images': '["ac.png", "comfortable-seats.png"]',
                    'logo_url': '/static/images/niazi.png',
                    'booking_url': 'https://example.com/book/niazi'
                },
                {
                    'bus_name': 'Skyways',
                    'bus_type': 'Luxury',
                    'departure': 'Karachi',
                    'destination': 'Islamabad',
                    'departure_time': '19:00:00',
                    'date': '2024-12-25',
                    'price': 5500.00,
                    'rewards': 275,
                    'facility_images': '["wifi.png", "ac.png", "entertainment.png", "meals.png"]',
                    'logo_url': '/static/images/skyways.png',
                    'booking_url': 'https://example.com/book/skyways'
                }
            ]
            
            for bus in sample_buses:
                sql = """
                INSERT INTO buses (bus_name, bus_type, departure, destination, departure_time, 
                                 date, price, rewards, facility_images, logo_url, booking_url)
                VALUES (%(bus_name)s, %(bus_type)s, %(departure)s, %(destination)s, %(departure_time)s, 
                        %(date)s, %(price)s, %(rewards)s, %(facility_images)s, %(logo_url)s, %(booking_url)s)
                """
                cursor.execute(sql, bus)
            
            print("✅ Sample data inserted successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False
    finally:
        connection.close()

if __name__ == "__main__":
    print("🚀 Setting up TravelBus Database...")
    
    # Test connection
    if test_connection():
        # Create tables
        if create_tables():
            # Insert sample data
            insert_sample_data()
            print("🎉 Database setup completed successfully!")
        else:
            print("❌ Failed to create tables")
    else:
        print("❌ Database setup failed - connection error")
