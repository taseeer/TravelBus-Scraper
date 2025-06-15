# # app.py
# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
# from database import get_db_connection
# from datetime import time, timedelta
# app = Flask(__name__, static_url_path='/static')
# CORS(app)

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/get_cities', methods=['GET'])
# def get_cities():
#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             sql = """
#             SELECT DISTINCT city_name 
#             FROM (
#                 SELECT departure as city_name FROM buses 
#                 UNION 
#                 SELECT destination as city_name FROM buses
#             ) as cities 
#             ORDER BY city_name
#             """
#             cursor.execute(sql)
#             cities = [row['city_name'] for row in cursor.fetchall()]
#         return jsonify(cities)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         connection.close()

# @app.route('/get_filters', methods=['GET'])
# def get_filters():
#     departure = request.args.get("departure")
#     destination = request.args.get("destination")
#     date = request.args.get("date")

#     if not all([departure, destination, date]):
#         return jsonify({"error": "Missing required parameters"}), 400

#     connection = get_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             # Get available bus services and types for the route and date
#             sql = """
#             SELECT DISTINCT 
#                 bus_name as service_name,
#                 bus_type
#             FROM buses
#             WHERE departure = %s 
#             AND destination = %s 
#             AND date = %s
#             ORDER BY bus_name, bus_type
#             """
#             cursor.execute(sql, (departure, destination, date))
#             results = cursor.fetchall()

#             # Organize filters
#             filters = {
#                 "busServices": list(set(row['service_name'] for row in results)),
#                 "busTypes": list(set(row['bus_type'] for row in results))
#             }
            
#             return jsonify(filters)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         connection.close()

# @app.route('/get_buses', methods=['GET'])
# def get_buses():
#     departure = request.args.get("departure")
#     destination = request.args.get("destination")
#     date = request.args.get("date")
#     services = request.args.getlist("services[]")
#     types = request.args.getlist("types[]")

#     if not all([departure, destination, date]):
#         return jsonify({"error": "Missing required parameters"}), 400

#     connection = get_db_connection()
#     if not connection:
#         return jsonify({"error": "Database connection failed"}), 500

#     try:
#         with connection.cursor() as cursor:
#             sql = """
#             SELECT 
#                 bus_name,
#                 bus_type,
#                 departure,
#                 destination,
#                 departure_time,
#                 date,
#                 price,
#                 COALESCE(rewards, 0) as rewards,
#                 COALESCE(facility_images, '[]') as facility_images,
#                 COALESCE(logo_url, '/static/images/default-bus.png') as logo_url,
#                 COALESCE(booking_url, '#') as booking_url
#             FROM buses
#             WHERE departure = %s 
#             AND destination = %s 
#             AND date = %s
#             """
#             params = [departure, destination, date]

#             if services:
#                 sql += " AND bus_name IN (%s)" % ','.join(['%s'] * len(services))
#                 params.extend(services)
#             if types:
#                 sql += " AND bus_type IN (%s)" % ','.join(['%s'] * len(types))
#                 params.extend(types)

#             sql += " ORDER BY departure_time"

#             cursor.execute(sql, params)
#             buses = cursor.fetchall()

#             # Format the data
#             for bus in buses:
#                 # Convert time to string for JSON serialization
#                 if 'departure_time' in bus and bus['departure_time'] is not None:
#                     bus['departure_time'] = str(bus['departure_time'])

#                 bus['price'] = f"Rs {bus['price']}"
#                 bus['rewards'] = f"{bus['rewards']} points"

#                 if not bus['facility_images'] or bus['facility_images'] == 'null':
#                     bus['facility_images'] = '[]'

#             return jsonify(buses)

#     except Exception as e:
#         print(f"Error in get_buses: {e}")
#         return jsonify({"error": str(e)}), 500
#     finally:
#         connection.close()


# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import time, timedelta
import pymysql
from pymysql import Error

app = Flask(__name__, static_url_path='/static')
CORS(app)

def get_db_connection():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="travelbus",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Error as e:
        print(f"DB Connection Error: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_cities', methods=['GET'])
def get_cities():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT DISTINCT city_name 
            FROM (
                SELECT departure as city_name FROM buses 
                UNION 
                SELECT destination as city_name FROM buses
            ) as cities 
            ORDER BY city_name
            """
            cursor.execute(sql)
            cities = [row['city_name'] for row in cursor.fetchall()]
        return jsonify(cities)
    except Exception as e:
        print(f"Error in get_cities: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/get_filters', methods=['GET'])
def get_filters():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    date = request.args.get("date")

    if not all([departure, destination, date]):
        return jsonify({"error": "Missing required parameters"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT DISTINCT 
                bus_name as service_name,
                bus_type
            FROM buses
            WHERE departure = %s 
            AND destination = %s 
            AND date = %s
            ORDER BY bus_name, bus_type
            """
            cursor.execute(sql, (departure, destination, date))
            results = cursor.fetchall()

            filters = {
                "busServices": list(set(row['service_name'] for row in results)),
                "busTypes": list(set(row['bus_type'] for row in results))
            }
            
            return jsonify(filters)
    except Exception as e:
        print(f"Error in get_filters: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/get_buses', methods=['GET'])
@app.route('/get_buses', methods=['GET'])
def get_buses():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    date = request.args.get("date")
    services = request.args.getlist("services[]")
    types = request.args.getlist("types[]")

    if not all([departure, destination, date]):
        return jsonify({"error": "Missing required parameters"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT 
                bus_name,
                bus_type,
                departure,
                destination,
                departure_time,
                date,
                price,
                COALESCE(rewards, 0) as rewards,
                COALESCE(facility_images, '[]') as facility_images,
                COALESCE(logo_url, '/static/images/default-bus.png') as logo_url,
                COALESCE(booking_url, '#') as booking_url
            FROM buses
            WHERE departure = %s 
            AND destination = %s 
            AND date = %s
            """
            params = [departure, destination, date]

            if services:
                sql += " AND bus_name IN (%s)" % ','.join(['%s'] * len(services))
                params.extend(services)
            if types:
                sql += " AND bus_type IN (%s)" % ','.join(['%s'] * len(types))
                params.extend(types)

            sql += " ORDER BY departure_time"

            cursor.execute(sql, params)
            buses = cursor.fetchall()

            # Format the data
            for bus in buses:
                # Convert time to string for JSON serialization
                if 'departure_time' in bus and bus['departure_time'] is not None:
                    bus['departure_time'] = str(bus['departure_time'])

                bus['price'] = f"Rs {bus['price']}"
                bus['rewards'] = f"{bus['rewards']} points"

                if not bus['facility_images'] or bus['facility_images'] == 'null':
                    bus['facility_images'] = '[]'

            return jsonify(buses)

    except Exception as e:
        print(f"Error in get_buses: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


@app.route('/health')
def health_check():
    connection = get_db_connection()
    if connection:
        connection.close()
        return jsonify({"status": "healthy", "database": "connected"})
    else:
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 500
@app.route('/get_sastaticket_buses', methods=['GET'])
def get_sastaticket_buses():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    date = request.args.get("date")
    services = request.args.getlist("services[]")
    types = request.args.getlist("types[]")

    if not all([departure, destination, date]):
        return jsonify({"error": "Missing required parameters"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT 
                bus_name,
                bus_type,
                departure_city as departure,
                arrival_city as destination,
                departure_time,
                date,
                price,
                logo_url,
                booking_url,
                is_refundable
            FROM sastaticket
            WHERE departure_city = %s 
            AND arrival_city = %s 
            AND date = %s
            """
            params = [departure, destination, date]

            if services:
                sql += " AND bus_name IN (%s)" % ','.join(['%s'] * len(services))
                params.extend(services)
            if types:
                sql += " AND bus_type IN (%s)" % ','.join(['%s'] * len(types))
                params.extend(types)

            sql += " ORDER BY departure_time"

            cursor.execute(sql, params)
            buses = cursor.fetchall()

            # Format the data to match your existing structure
            formatted_buses = []
            for bus in buses:
                formatted_bus = {
                    'bus_name': bus['bus_name'],
                    'bus_type': bus['bus_type'],
                    'departure': bus['departure'],
                    'destination': bus['destination'],
                    'departure_time': str(bus['departure_time']),
                    'date': bus['date'],
                    'price': f"Rs {bus['price']}",
                    'rewards': "0 points",  # Default if not available
                    'facility_images': '[]',  # Default if not available
                    'logo_url': bus['logo_url'] or '/static/images/default-bus.png',
                    'booking_url': bus['booking_url'] or '#',
                    'is_refundable': bus['is_refundable']
                }
                formatted_buses.append(formatted_bus)

            return jsonify(formatted_buses)

    except Exception as e:
        print(f"Error in get_sastaticket_buses: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()
@app.route('/get_sastaticket_cities', methods=['GET'])
def get_sastaticket_cities():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT DISTINCT city_name 
            FROM (
                SELECT departure_city as city_name FROM sastaticket 
                UNION 
                SELECT arrival_city as city_name FROM sastaticket
            ) as cities 
            ORDER BY city_name
            """
            cursor.execute(sql)
            cities = [row['city_name'] for row in cursor.fetchall()]
        return jsonify(cities)
    except Exception as e:
        print(f"Error in get_sastaticket_cities: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
