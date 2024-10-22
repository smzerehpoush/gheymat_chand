from flask import Flask, jsonify
import redis
import json  # Import the json module to handle JSON strings

# Initialize Flask app
app = Flask(__name__)

# Connect to Redis
redis_connection = redis.Redis(host='redis', port=6379, db=1)

# Redis key where prices are stored
REDIS_KEY = 'prices_history'

@app.route('/gold/api/prices', methods=['GET'])
def get_last_30_prices():
    try:
        # Fetch the last 30 items from the Redis list
        last_30_items = redis_connection.lrange(REDIS_KEY, -60, -1)
        
        # Decode the bytes data to strings (assuming the data is stored as JSON strings)
        last_30_items = [item.decode('utf-8') for item in last_30_items]
        
        # Convert the JSON strings to Python objects
        last_30_items = [json.loads(item) for item in last_30_items]

        # Return the data as a JSON response
        return jsonify({'dataset': last_30_items}), 200

    except Exception as e:
        # Handle exceptions and return an error message
        return jsonify({"error": str(e)}), 500


# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
