from flask import Flask, render_template, request, jsonify
from scraper import scrape_bus_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    html_content = request.form.get('html_content')
    base_url = request.form.get('base_url', '').strip()
    
    if not html_content:
        return jsonify({"status": "error", "message": "No HTML content provided"})
    
    result = scrape_bus_data(html_content, base_url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001)  # This will run on port 5001