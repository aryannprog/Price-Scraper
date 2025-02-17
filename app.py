from flask import Flask, request, render_template, jsonify, send_file
import sqlite3
from scraper import identify_sales_channel, fetch_price  # Import your scraping function
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Temporary CSV file path
TEMP_CSV_PATH = "fetched_prices.csv"

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Manage Data page
@app.route('/manage_data')
def manage_data():
    return render_template('manage_data.html')

# Fetch Prices page (initial page load)
@app.route('/fetch_prices')
def fetch_prices():
    return render_template('fetch_prices.html')

# Manage Data page
@app.route('/historical_reads')
def historical_reads():
    return render_template('historical_reads.html')

# Function to fetch latest prices
@app.route('/fetch_prices_api')
def fetch_prices_api():
    try:
        conn = sqlite3.connect("dataset.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SKU_CODE, Product_Description, Channel_wise_URL FROM products")
        rows = cursor.fetchall()
        conn.close()

        fetched_data = []
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp

        for row in rows:
            sku_code, description, url = row
            channel_name = identify_sales_channel(url)  # Identify channel name
            price = fetch_price(channel_name, url, retries=3, delay=2)

            fetched_data.append({
                "SKU_CODE": sku_code,
                "Product_Description": description,
                "Channel_wise_URL": url,
                "Channel_Name": channel_name,
                "Price": price,
                "Timestamp": current_timestamp  # Add timestamp
            })

        if fetched_data:
            save_to_historical_db(fetched_data)  # Save to historical.db with timestamp

            # Convert fetched data to CSV and save temporarily
            df = pd.DataFrame(fetched_data)
            df.to_csv(TEMP_CSV_PATH, index=False)

        return jsonify(fetched_data)

    except Exception as e:
        print(f"Error: {e}")  # Debugging in terminal
        return jsonify([])  # Return empty list in case of error
    
# Fetch historical data from database
@app.route("/fetch_historical")
def fetch_historical():
    try:
        conn = sqlite3.connect("historical.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SKU_CODE, Product_Description, Sales_Channel, Price, Timestamp FROM prices")
        data = cursor.fetchall()
        conn.close()

        # Convert to JSON format
        history = [
            {"SKU_CODE": row[0], "Product_Description": row[1], "Sales_Channel": row[2], "Price": row[3], "Timestamp": row[4]}
            for row in data
        ]

        return jsonify(history)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Function to download fetched prices as CSV and then clear the file
@app.route('/download_prices', methods=['GET'])
def download_csv():
    try:
        if os.path.exists(TEMP_CSV_PATH) and os.path.getsize(TEMP_CSV_PATH) > 0:
            # Send the file for download
            response = send_file(TEMP_CSV_PATH, as_attachment=True, download_name="fetched_prices.csv")

            # After sending the file, clear its content
            open(TEMP_CSV_PATH, 'w').close()

            return response
        else:
            return jsonify({"error": "No data available. Please fetch data first."}), 400
    except Exception as e:
        return jsonify({"error": "Something went wrong."}), 500

# Generate and provide CSV for download
@app.route("/download_historical", methods=["GET"])
def download_historical():
    try:
        conn = sqlite3.connect("historical.db")
        df = pd.read_sql_query("SELECT * FROM prices", conn)
        conn.close()

        # Save CSV file temporarily
        csv_file = "historical_prices.csv"
        df.to_csv(csv_file, index=False)

        return send_file(csv_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Fetch data from dataset.db and return as HTML table
@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    try:
        conn = sqlite3.connect("dataset.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SKU_CODE, Product_Description, Channel_wise_URL FROM products")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "<p>No data available in the dataset.</p>"

        # Generate an HTML table dynamically
        table_html = """
        <table border="1" class="data-table">
            <thead>
                <tr>
                    <th>SKU Code</th>
                    <th>Product Description</th>
                    <th>Channel URL</th>
                </tr>
            </thead>
            <tbody>
        """
        for row in rows:
            table_html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td><a href='{row[2]}' target='_blank'>🔗 Visit Link</a></td></tr>"

        table_html += "</tbody></table>"

        return table_html  # Returning HTML content directly

    except Exception as e:
        return f"<p>Error loading data: {str(e)}</p>"    

@app.route('/add-data', methods=['POST'])
def add_data():
    try:
        sku_code = request.form.get('sku_code')
        product_description = request.form.get('product_description')
        channel_url = request.form.get('channel_url')

        if not sku_code or not product_description or not channel_url:
            return "❌ Missing required fields", 400

        conn = sqlite3.connect("dataset.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (SKU_CODE, Product_Description, Channel_wise_URL) 
            VALUES (?, ?, ?)
        """, (sku_code, product_description, channel_url))
        conn.commit()
        conn.close()

        return f"✅ Successfully added SKU Code: {sku_code}"
    except Exception as e:
        return f"❌ Error: {e}"
    
@app.route('/delete-data', methods=['POST'])
def delete_data():
    try:
        sku_code = request.form.get('delete_sku_code')

        if not sku_code:
            return "❌ SKU Code required", 400

        conn = sqlite3.connect("dataset.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE SKU_CODE = ?", (sku_code,))
        conn.commit()
        conn.close()

        return f"✅ Deleted SKU Code: {sku_code}"
    except Exception as e:
        return f"❌ Error: {e}"

# Store latest price data in historical.db
def save_to_historical_db(data):
    conn = sqlite3.connect("historical.db")
    cursor = conn.cursor()

    for row in data:
        cursor.execute("""
            INSERT INTO prices (SKU_CODE, Product_Description, Sales_Channel, Price, Timestamp) 
            VALUES (?, ?, ?, ?, ?)
        """, (row["SKU_CODE"], row["Product_Description"], row["Channel_Name"], row["Price"], row["Timestamp"]))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)