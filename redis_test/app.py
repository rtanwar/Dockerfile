from flask import Flask, jsonify
import mysql.connector
import redis

app = Flask(__name__)

# Connect to MariaDB
db_connection = mysql.connector.connect(
    host='mariadb',
    user='exampleuser',
    password='examplepassword',
    database='exampledb'
)

# Connect to Redis
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

# Sample route to fetch data from MariaDB with Redis caching
@app.route('/data')
def get_data():
    cached_data = redis_client.get('cached_data')
    if cached_data:
        return jsonify({'data': cached_data.decode('utf-8')})

    # If data not found in cache, fetch from MariaDB
    cursor = db_connection.cursor()
    cursor.execute('SELECT * FROM your_table')
    data = cursor.fetchall()
    cursor.close()

    # Cache the fetched data in Redis
    redis_client.set('cached_data', str(data))
    cache_hits = redis_client.get('cache_hits')
    cache_misses = redis_client.get('cache_misses')

    print("Cache hits:", int(cache_hits) if cache_hits else 0)
    print("Cache misses:", int(cache_misses) if cache_misses else 0) 
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

