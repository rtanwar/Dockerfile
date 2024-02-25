from flask import Flask, jsonify
import mysql.connector
import redis
import logging
import sys

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
# Connect to MariaDB
db_connection = mysql.connector.connect(
    host='mariadb',
    user='exampleuser',
    password='examplepassword',
    database='exampledb'
)

# Connect to Redis
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
def redis_cache_info():
    hits = redis_client.info()['keyspace_hits']
    # Get the number of failed lookups of keys
    misses = redis_client.info()['keyspace_misses']
    # Calculate and print the hit/miss ratio
    if hits + misses > 0:
        ratio = hits / (hits + misses)
        return f'Hit/Miss ratio: {ratio}'
    else:
        return 'No data yet'


def try_cached_data(qry,parameters=None):
    query_key  = f"{qry}|{parameters}"
    cached_data = redis_client.get(query_key )
    if cached_data:
        data = cached_data.decode('utf-8')        
    else:
        cursor = db_connection.cursor()
        if parameters:
            cursor.execute(qry,parameters)
        else:
            cursor.execute(qry)
        data = cursor.fetchall()
        cursor.close()    
        redis_client.set(qry, str(data))
    return jsonify({'data': data})

# Sample route to fetch data from MariaDB with Redis caching
@app.route('/data')
@app.route('/data/<id>')
@app.route('//<id>')
@app.route('/')
def get_data(id=None):
    import random
    #num = random.randint(0,2)
    print(id)    
    if (id):
        qry = 'SELECT * FROM your_table  WHERE id=%s'
        data = try_cached_data(qry,(id,))
    else:
        qry = 'SELECT * FROM your_table'
        data = try_cached_data(qry)
    #cache_hits = redis_client.get('keyspace_hits')
    #cache_misses = redis_client.get('keyspace_misses')
    #print("Cache hits:", int(cache_hits) if cache_hits else 0)
    #print("Cache misses:", int(cache_misses) if cache_misses else 0) 
    print(redis_cache_info())
    #print(redis_client.info())
    #app.logger.warning('testing warning log')
    #app.logger.error('testing error log')
    #app.logger.info('testing info log')
    
    #cached_data = redis_client.get(qry,input)    
    #if cached_data:
    #    print('cached_data')
    #return jsonify({'data': data.decode('utf-8')})
    return data
        #return jsonify({'data': cached_data.decode('utf-8')},{'redis_client':redis_client.info()} )
    # If data not found in cache, fetch from MariaDB
    cursor = db_connection.cursor()    
    cursor.execute(qry,input)
    data = cursor.fetchall()
    cursor.close()
    # Cache the fetched data in Redis
    redis_client.set(qry, str(data))
    return jsonify({'data': data})
    #return "Check your console"
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

