import re
import json
from datetime import datetime
from database import get_db_connection
from bs4 import BeautifulSoup

def scrape_bus_data(html_content, base_url=''):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract Departure Date
        date_element = soup.find('div', class_='text-nowrap small')
        departure_date = date_element.get_text(strip=True).replace("Departure:", "").strip() if date_element else ""

        # Convert scraped date (19 Feb 2025) to YYYY-MM-DD format
        if departure_date:
            try:
                departure_date = datetime.strptime(departure_date, "%d %b %Y").strftime("%Y-%m-%d")
            except ValueError:
                departure_date = ""

        # Find all bus entries
        bus_entries = soup.find_all('div', class_='my-3 text-reset card detail-card')
        bus_data = []

        # Connect to MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        for bus in bus_entries:
            # Extract Bus Logo
            logo_img = bus.find('div', class_='col-2 col-lg-3 col-md service-img')
            logo = logo_img.find('img')['src'] if logo_img and logo_img.find('img') else ""

            # Extract Bus Name & Type
            bus_name_element = bus.find('h5', class_='mb-0 font-weight-600')
            bus_name = bus_name_element.find(text=True, recursive=False).strip() if bus_name_element else ""
            bus_type = bus.find('span', class_='mb-0 font-weight-400 text-gray-500 fs-6 small').get_text(strip=True) if bus.find('span', class_='mb-0 font-weight-400 text-gray-500 fs-6 small') else ""

            # Extract Route Details
            departure_div = bus.find('div', class_='d-flex justify-content-center col-4 col-lg-3 col-md')
            departure_city = departure_div.find('h5', class_='mb-0 font-weight-600').get_text(strip=True) if departure_div and departure_div.find('h5') else ""
            departure_full = departure_div.find('p', class_='mb-0').get_text(strip=True) if departure_div and departure_div.find('p') else ""

            arrival_divs = bus.find_all('div', class_='d-flex justify-content-center col-4 col-lg-3 col-md')
            arrival_div = arrival_divs[1] if len(arrival_divs) > 1 else None
            arrival_city = arrival_div.find('h5', class_='mb-0 font-weight-600').get_text(strip=True) if arrival_div and arrival_div.find('h5') else ""
            arrival_full = arrival_div.find('p', class_='mb-0').get_text(strip=True) if arrival_div and arrival_div.find('p') else ""

            # Extract Departure Time
            departure_time_div = bus.find('div', class_='duration')
            departure_time = departure_time_div.find('h5').get_text(strip=True) if departure_time_div and departure_time_div.find('h5') else ""

            # Extract Price - Fixed implementation
            price_element = bus.find('h5', class_=lambda x: x and 'font-weight-600' in x and 'fs-5' in x)
            if price_element:
                price_span =price_element.find_all('span')[-1] if price_element.find_all('span') else price_element
                
                price = re.sub(r'[^\d]', '', price_span.get_text(strip=True))
                if not price:  # If no digits found, set to 0
                    price = "0"
            else:
                price = "0"
      
        
            # Extract Rewards
            rewards_div = bus.find('div', class_='rewards')
            rewards = rewards_div.find('span', class_='text-primary').get_text(strip=True) if rewards_div and rewards_div.find('span', class_='text-primary') else "0"

            # Extract Facility Images - Fixed implementation
            facility_images = []
            facility_divs = bus.find_all('div', class_=lambda x: x and 'd-flex' in x and 'flex-wrap' in x and 'align-items-center' in x and 'facilities' in x)
            for div in facility_divs:
                img_tags = div.find_all('img')
                for img in img_tags:
                    if img and 'src' in img.attrs:
                        facility_images.append(img['src'])

            facility_images_json = json.dumps(facility_images)

            # Use the base_url provided by the user as the booking URL
            booking_url = base_url

            # Insert into MySQL database
            query = """INSERT INTO buses (bus_name, bus_type, departure, destination, departure_time, date, 
                      price, rewards, facility_images, logo_url, booking_url)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (bus_name, bus_type, departure_full, arrival_full, departure_time, 
                     departure_date, price, rewards, facility_images_json, logo, booking_url)

            try:
                cursor.execute(query, values)
                conn.commit()
            except Exception as e:
                conn.close()
                return {"status": "error", "message": f"Error inserting data into database: {str(e)}"}

            bus_data.append({
                "bus_name": bus_name,
                "bus_type": bus_type,
                "departure": {"city_code": departure_city, "full_name": departure_full},
                "arrival": {"city_code": arrival_city, "full_name": arrival_full},
                "departure_time": departure_time,
                "date": departure_date,
                "price": f"Rs {price}",
                "rewards": f"{rewards} points",
                "facility_images": facility_images,
                "logo_url": logo,
                "booking_url": booking_url
            })

        conn.close()

        # Save data to JSON file (optional)
        with open("bus_data.json", "w", encoding="utf-8") as file:
            json.dump(bus_data, file, indent=4, ensure_ascii=False)

        return {"status": "success", "message": "Data scraped and saved successfully", "data": bus_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}