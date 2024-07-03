import redis
from flask import Flask, jsonify

app = Flask(__name__)

redis_conn = redis.Redis(host='redis', port=6379, db=0)


@app.route('/api/v1/gold-price', methods=['GET'])
def get_value():
    gold_price = redis_conn.get('milli_price')
    return jsonify({'price': gold_price}), 200


if __name__ == '__main__':
    app.run(debug=True)
