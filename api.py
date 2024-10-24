from flask import Flask, jsonify, request  # Import request to handle query parameters
import redis
import json  # Import the json module to handle JSON strings

# Initialize Flask app
app = Flask(__name__)

# Connect to Redis
redis_connection = redis.Redis(host='redis', port=6379, db=1)

# Redis key where prices are stored
REDIS_KEY = 'prices_history'

@app.route('/gold/api/prices', methods=['GET'])
def get_last_n_prices():
    try:
        # Get the 'n' query parameter from the request, default to 30 if not provided
        n = request.args.get('size', default=30, type=int)
        
        # Fetch the last 'n' items from the Redis list
        # Using -n for the start index to get the last n prices
        last_n_items = redis_connection.lrange(REDIS_KEY, -n, -1)
        
        # Decode the bytes data to strings (assuming the data is stored as JSON strings)
        last_n_items = [item.decode('utf-8') for item in last_n_items]
        
        # Convert the JSON strings to Python objects
        last_n_items = [json.loads(item) for item in last_n_items]

        # Return the data as a JSON response
        return jsonify({'dataset': last_n_items}), 200

    except Exception as e:
        # Handle exceptions and return an error message
        return jsonify({"error": str(e)}), 500


# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
