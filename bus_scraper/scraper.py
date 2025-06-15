import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import pymysql
from pymysql import Error

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            database='travelbus',
            user='root',
            password='',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def scrape_bus_data(html_content, base_url=''):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        bus_data = []
        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
        except Exception as db_error:
            print(f"Database connection failed, continuing without DB: {db_error}")

        # Extract Departure Date
        date_div = soup.find('div', class_='text-nowrap small')
        departure_date = ""
        if date_div:
            date_text = date_div.get_text(strip=True)
            date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', date_text)
            if date_match:
                try:
                    departure_date = datetime.strptime(date_match.group(1), "%d %b %Y").strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # Find all bus cards
        bus_cards = soup.find_all('div', class_='detail-card')
        
        for card in bus_cards:
            try:
                # Bus Name and Type
                name_div = card.find('h5', class_='font-weight-600')
                bus_name = ""
                bus_type = ""
                if name_div:
                    name_parts = [part.strip() for part in name_div.get_text().split('\n') if part.strip()]
                    if name_parts:
                        bus_name = name_parts[0]
                        if len(name_parts) > 1:
                            bus_type = name_parts[1]

                # Logo URL
                logo_img = card.find('img', class_='img-fluid')
                logo_url = logo_img['src'] if logo_img and logo_img.get('src') else ""

                # Departure Information
                departure_div = card.find('div', class_='departure')
                departure_city = ""
                departure_full = ""
                if departure_div:
                    departure_city = departure_div.find('h5').get_text(strip=True) if departure_div.find('h5') else ""
                    departure_full = departure_div.find('p').get_text(strip=True) if departure_div.find('p') else ""

                # Arrival Information
                arrival_div = card.find('div', class_='arrival')
                arrival_city = ""
                arrival_full = ""
                if arrival_div:
                    arrival_city = arrival_div.find('h5').get_text(strip=True) if arrival_div.find('h5') else ""
                    arrival_full = arrival_div.find('p').get_text(strip=True) if arrival_div.find('p') else ""

                # Departure Time
                time_div = card.find('div', class_='duration')
                departure_time = ""
                if time_div:
                    departure_time = time_div.find('h5').get_text(strip=True) if time_div.find('h5') else ""

                # Price
                price_h5 = card.find('h5', class_='fs-5')
                price = "0"
                if price_h5:
                    price_span = price_h5.find('span')
                    if price_span:
                        price = re.sub(r'[^\d]', '', price_span.get_text(strip=True)) or "0"

                # Rewards Points
                rewards_div = card.find('div', class_='rewards')
                rewards = "0"
                if rewards_div:
                    rewards_span = rewards_div.find('span', class_='text-primary')
                    if rewards_span:
                        rewards = re.sub(r'[^\d]', '', rewards_span.get_text(strip=True)) or "0"

                # Facilities
                facility_images = []
                facility_divs = card.find_all('div', class_='facilities')
                for div in facility_divs:
                    imgs = div.find_all('img')
                    for img in imgs:
                        if img.get('src'):
                            facility_images.append(img['src'])
                facility_images_json = json.dumps(facility_images)

                # Booking URL
                book_button = card.find('button', class_='btn-primary')
                booking_url = base_url if book_button else ""

                # Create data structure for frontend (with nested objects)
                frontend_data = {
                    "bus_name": bus_name,
                    "bus_type": bus_type,
                    "departure": {
                        "city_code": departure_city,
                        "full_name": departure_full
                    },
                    "arrival": {
                        "city_code": arrival_city,
                        "full_name": arrival_full
                    },
                    "departure_time": departure_time,
                    "date": departure_date,
                    "price": f"Rs {price}",
                    "rewards": f"{rewards} points",
                    "facility_images": facility_images,  # Array for frontend
                    "logo_url": logo_url,
                    "booking_url": booking_url
                }
                bus_data.append(frontend_data)

                # Save to database if connection exists
                if conn and cursor:
                    try:
                        sql = """INSERT INTO buses (
                            bus_name, bus_type, departure, destination, 
                            departure_time, date, price, rewards, 
                            facility_images, logo_url, booking_url
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        
                        cursor.execute(sql, (
                            bus_name, bus_type, departure_full, arrival_full,
                            departure_time, departure_date, price, rewards,
                            facility_images_json, logo_url, booking_url
                        ))
                        conn.commit()
                    except Exception as db_insert_error:
                        print(f"Failed to insert bus data: {db_insert_error}")
                        conn.rollback()

            except Exception as e:
                print(f"Error processing bus card: {str(e)}")
                continue

        # Close database connection if it exists
        if conn:
            cursor.close()
            conn.close()

        return {
            "status": "success",
            "message": f"Successfully scraped {len(bus_data)} buses",
            "data": bus_data
        }

    except Exception as e:
        # Ensure database connection is closed even if error occurs
        if 'conn' in locals() and conn:
            conn.close()
        return {
            "status": "error",
            "message": f"Scraping error: {str(e)}"
        }
