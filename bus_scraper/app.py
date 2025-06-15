from flask import Flask, render_template, request, jsonify
from scraper import scrape_bus_data
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Get form data
        html_content = request.form.get('html_content', '').strip()
        base_url = request.form.get('base_url', '').strip()
        
        # Validation
        if not html_content:
            return jsonify({
                "status": "error", 
                "message": "No HTML content provided. Please paste the HTML content from the bus search results."
            })
        
        if not base_url:
            base_url = "https://bookme.pk/bus/search-results"
        
        # Check if HTML contains expected structure
        if 'detail-card' not in html_content and 'bus' not in html_content.lower():
            return jsonify({
                "status": "error", 
                "message": "The provided HTML doesn't appear to contain bus data. Please make sure you're copying the correct HTML from the search results page."
            })
        
        # Scrape the data
        result = scrape_bus_data(html_content, base_url)
        
        # Enhanced response
        if result["status"] == "success" and len(result["data"]) == 0:
            return jsonify({
                "status": "warning", 
                "message": "No bus data found in the provided HTML. Please check if the HTML structure is correct.",
                "data": []
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Server error: {str(e)}"
        })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Bus scraper is running!"})

if __name__ == '__main__':
    # Ensure static and template directories exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, port=5001)
