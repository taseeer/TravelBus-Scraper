# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import get_db_connection

app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_cities', methods=['GET'])
def get_cities():
    connection = get_db_connection()
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
    try:
        with connection.cursor() as cursor:
            # Get available bus services and types for the route and date
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

            # Organize filters
            filters = {
                "busServices": list(set(row['service_name'] for row in results)),
                "busTypes": list(set(row['bus_type'] for row in results))
            }
            
            return jsonify(filters)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/get_buses', methods=['GET'])
def get_buses():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    date = request.args.get("date")
    services = request.args.getlist("services[]")  # Get selected services as list
    types = request.args.getlist("types[]")  # Get selected types as list

    if not all([departure, destination, date]):
        return jsonify({"error": "Missing required parameters"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Base query
            sql = """
            SELECT 
                bus_name,
                bus_type,
                departure,
                destination,
                departure_time,
                date,
                CONCAT('Rs ', price) as price,
                CONCAT(rewards, ' points') as rewards,
                facility_images,
                logo_url,
                booking_url
            FROM buses
            WHERE departure = %s 
            AND destination = %s 
            AND date = %s
            """
            params = [departure, destination, date]

            # Add filter conditions if services or types are selected
            if services:
                sql += " AND bus_name IN (%s)" % ','.join(['%s'] * len(services))
                params.extend(services)
            if types:
                sql += " AND bus_type IN (%s)" % ','.join(['%s'] * len(types))
                params.extend(types)

            cursor.execute(sql, params)
            buses = cursor.fetchall()
            
            # Process facility images
            for bus in buses:
                if bus['facility_images']:
                    bus['facility_images'] = bus['facility_images']
                else:
                    bus['facility_images'] = '[]'
            
            return jsonify(buses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)