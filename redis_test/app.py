from flask import Flask, jsonify
from flask import render_template, render_template_string, request, g
import mysql.connector
import redis
import logging
import sys
import random
import string
import pickle
import time


app = Flask(__name__)
#engine = db.create_engine('mysql+pymysql://exampleuser:examplepassword@mariadb/exampledb?charset=utf8mb4')

logging.basicConfig(level=logging.DEBUG)
# Connect to MariaDB
#db_connection = mysql.connector.connect( host='mariadb', user='exampleuser', password='examplepassword', database='exampledb', connect_timeout=28800 )

from flask_mysqldb import MySQL
 
app = Flask(__name__)
 
app.config['MYSQL_HOST'] = 'mariadb'
app.config['MYSQL_USER'] = 'exampleuser'
app.config['MYSQL_PASSWORD'] = 'examplepassword'
app.config['MYSQL_DB'] = 'classicmodels'
app.config['CACHE_ENABLED'] = True
mysql = MySQL(app)


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

# Function to generate dummy data

def generate_dummy_data(num_rows):
    dummy_data = []
    for _ in range(num_rows):
        name = generate_random_string(10)
        email = f"{name}@example.com"
        dummy_data.append((name, email))
    return dummy_data

# Function to insert dummy data into the database
@app.route('/dummydata/<int:num_rows>')
def insert_dummy_data(num_rows):    
    #c = db_connection.cursor()
    c = mysql.connection.cursor()
    dummy_data = generate_dummy_data(num_rows)  # Generating 10 rows of dummy data
    print(dummy_data)
    c.executemany('INSERT INTO your_table (name, email) VALUES (%s, %s)', dummy_data)
    #db_connection.commit()
    mysql.connection.commit()
    return f'{num_rows} Record(s) Inserted!'
    

# Connect to Redis
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)



def redis_cache_info():
    hits = redis_client.info()['keyspace_hits']
    # Get the number of failed lookups of keys
    misses = redis_client.info()['keyspace_misses']
    # Calculate and print the hit/miss ratio
    if hits + misses > 0:
        ratio = hits / (hits + misses)
        return f'Hit/Miss ratio: {ratio} {hits}/{misses}'
    else:
        return 'No data yet'


def try_cached_data(qry,parameters=None):
    cached_data=None
    if parameters:
        query_key  = f"{qry}|{parameters}"
    else:
        query_key  = f"{qry}"    
    #fetch data from cache
    print('CACHE_ENABLED',app.config['CACHE_ENABLED'])
    if app.config['CACHE_ENABLED']:
        cached_data = redis_client.get(query_key)    
    if cached_data:
        print('from CACHE')
        #data = cached_data.decode('utf-8')
        data = pickle.loads(cached_data)
    else:
        print('from DB')
        #cursor = db_connection.cursor(buffered=True)
        cursor = mysql.connection.cursor()
        if parameters:
            cursor.execute(qry,parameters)
        else:
            cursor.execute(qry)
        data = cursor.fetchall()        
        pickled_object = pickle.dumps(data)
        #redis_client.set(query_key, str(data))
        redis_client.set(query_key, pickled_object)
        cursor.close()    
    return data


def get_db_data(qry,parameters=None):    
    print('from DB')
    cursor = mysql.connection.cursor()
    if parameters:
        cursor.execute(qry,parameters)
    else:
        cursor.execute(qry)
    data = cursor.fetchall()
    #redis_client.set(query_key, str(data))
    cursor.close()    
    return data

@app.before_request
def before_request():
   g.request_start_time = time.time()
   g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@app.route('/disablecache')
def cache_disable():
    app.config['CACHE_ENABLED'] =False;
    c = app.config['CACHE_ENABLED']
    return f'Cache Disabled! {c}'

@app.route('/enablecache')
def cache_enable():
    app.config['CACHE_ENABLED'] =True;
    c = app.config['CACHE_ENABLED']
    return f'Cache Enabled! {c}'

@app.route('/')
def index():
    render_html =render_template_string("""
                    <a href="{{url_for('delete_cache')}}">Delete Cache</a></p>
                    <a href="{{url_for('get_data')}}">Try Cache Data</a></p>
                    <a href="{{url_for('get_dbdata')}}">DB Data</a></p>
                    <a href="{{url_for('cache_disable')}}">Disable Cache</a></p>
                    <a href="{{url_for('cache_enable')}}">Enable Cache</a>""")
    return render_html

@app.route('/deletecache')
def delete_cache():      
    qry = 'SELECT customerNumber,customerName,SLEEP(0.01) sleep FROM customers'  
    query_key  = f"{qry}"  
    redis_client.delete(query_key)
    return f'Cache for key: {query_key} deleted!'

# Sample route to fetch data from MariaDB with Redis caching
@app.route('/data')
@app.route('/data/<id>')
def get_data(id=None):
    import random
    #num = random.randint(0,2)
    print(id)    
    if (id):
        qry = 'SELECT customerNumber,customerName,SLEEP(0.01) sleep FROM customers where customerNumber=%s'        
        data = try_cached_data(qry,(id,))
    else:
        qry = 'SELECT customerNumber,customerName,SLEEP(0.01) sleep FROM customers'
        data = try_cached_data(qry)
    print(redis_cache_info())
    return jsonify({'time':g.request_time(),'data': data})

@app.route('/dbdata')
@app.route('/dbdata/<id>')
def get_dbdata(id=None):
    import random
    #num = random.randint(0,2)
    print(id)    
    if (id):
        qry = 'SELECT customerNumber,customerName,SLEEP(0.01) sleep FROM customers where customerNumber=%s'        
        data = get_db_data(qry,(id,))
    else:
        qry = 'SELECT customerNumber,customerName,SLEEP(0.01) sleep FROM customers'
        data = get_db_data(qry)            
    return jsonify({'data': data,'time':g.request_time()})


    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

