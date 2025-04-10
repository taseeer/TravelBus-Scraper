import re
import json
from datetime import datetime
from database import get_db_connection
from bs4 import BeautifulSoup

# Sample HTML - Replace with actual HTML content
html = ''''''  # Replace with actual HTML source

soup = BeautifulSoup(html, 'html.parser')

# **Extract Departure Date**
date_element = soup.find('div', class_='text-nowrap small')
departure_date = date_element.get_text(strip=True).replace("Departure:", "").strip() if date_element else ""

# Convert scraped date (19 Feb 2025) to YYYY-MM-DD format
if departure_date:
    try:
        departure_date = datetime.strptime(departure_date, "%d %b %Y").strftime("%Y-%m-%d")
    except ValueError:
        departure_date = ""  # Handle invalid date formats

# **Find all bus entries**
bus_entries = soup.find_all('div', class_='my-3 text-reset card detail-card')

bus_data = []

# Connect to MySQL
conn = get_db_connection()
cursor = conn.cursor()

for bus in bus_entries:
    # **Extract Bus Logo**
    logo_img = bus.find('div', class_='col-2 col-lg-3 col-md service-img')
    logo = logo_img.find('img')['src'] if logo_img and logo_img.find('img') else ""

    # **Extract Bus Name & Type**
    bus_name = bus.find('h5', class_='mb-0 font-weight-600').get_text(strip=True) if bus.find('h5', class_='mb-0 font-weight-600') else ""
    bus_type = bus.find('span', class_='mb-0 font-weight-400 text-gray-500 fs-6 small').get_text(strip=True) if bus.find('span', class_='mb-0 font-weight-400 text-gray-500 fs-6 small') else ""

    # **Extract Route Details (Departure & Arrival Cities)**
    departure_div = bus.find('div', class_='d-flex justify-content-center col-4 col-lg-3 col-md')
    departure_city = departure_div.find('h5', class_='mb-0 font-weight-600').get_text(strip=True) if departure_div and departure_div.find('h5') else ""
    departure_full = departure_div.find('p', class_='mb-0').get_text(strip=True) if departure_div and departure_div.find('p') else ""

    arrival_div = bus.find_all('div', class_='d-flex justify-content-center col-4 col-lg-3 col-md')
    arrival_div = arrival_div[1] if len(arrival_div) > 1 else None
    arrival_city = arrival_div.find('h5', class_='mb-0 font-weight-600').get_text(strip=True) if arrival_div and arrival_div.find('h5') else ""
    arrival_full = arrival_div.find('p', class_='mb-0').get_text(strip=True) if arrival_div and arrival_div.find('p') else ""

    # **Extract Departure Time**
    departure_time = bus.find('div', class_='duration').find('h5').get_text(strip=True) if bus.find('div', class_='duration') and bus.find('div', class_='duration').find('h5') else ""

    # **Extract Price**
    price_element = bus.find('h5', class_='mx-2 mb-0 font-weight-600 fs-5 me-3')
    if price_element:
        price_span = price_element.find_all('span')[-1] if price_element.find_all('span') else price_element
        price = re.sub(r'[^\d]', '', price_span.get_text(strip=True))
    else:
        price = "0"

    # **Extract Rewards**
    rewards = bus.find('div', class_='rewards')
    rewards = rewards.find('span', class_='text-primary').get_text(strip=True) if rewards and rewards.find('span', class_='text-primary') else "0"

    # **Extract Facility Images**
    facility_images = []
    facility_divs = bus.find_all('div', class_='d-flex flex-wrap align-items-center my-1 my-lg-0 facilities me-2')
    for div in facility_divs:
        img_tag = div.find('img')
        if img_tag and 'src' in img_tag.attrs:
            facility_images.append(img_tag['src'])

    # Convert facility images list to JSON
    facility_images_json = json.dumps(facility_images)

    # **Extract Booking URL**
    book_button = bus.find('button', class_='btn btn-primary')
    booking_url = ""
    if book_button and 'data-bs-target' in book_button.attrs:
        offcanvas_id = book_button['data-bs-target']
        offcanvas_div = soup.find('div', id=offcanvas_id.replace("#", ""))
        if offcanvas_div:
            link_tag = offcanvas_div.find('a', href=True)
            booking_url = link_tag['href'] if link_tag else ""

    # **Insert into MySQL database (including booking_url)**
    query = """INSERT INTO buses (bus_name, bus_type, departure, destination, departure_time, date, price, rewards, facility_images, logo_url, booking_url)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (bus_name, bus_type, departure_full, arrival_full, departure_time, departure_date, price, rewards, facility_images_json, logo, booking_url)

    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        print(f"Error inserting data into database: {e}")

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

# Save data to a JSON file (optional)
with open("bus_data.json", "w", encoding="utf-8") as file:
    json.dump(bus_data, file, indent=4)

print("Scraped data saved successfully!")