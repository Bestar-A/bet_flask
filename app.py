from flask import Flask, render_template
from flask_socketio import SocketIO
from scraper import scrape_crash_game_data, scrape_background
import threading
import time

import hmac
import hashlib
import binascii

import numpy as np

def sha256_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()
_salt = '0000000000000000000301e2801a9a9598bfb114e574a91a887f2132f33047e6'
def game_result(seed, salt):
    n_bits = 52  # number of most significant bits to use

    # 1. HMAC_SHA256(message=seed, key=salt) 
    # Convert the seed and salt to bytes
    seed_bytes = bytes.fromhex(seed)
    salt_bytes = salt.encode('utf-8')
    
    # Perform HMAC-SHA256
    hmac_hash = hmac.new(salt_bytes, seed_bytes, hashlib.sha256)
    hmac_hex = binascii.hexlify(hmac_hash.digest()).decode('utf-8')
    
    # 2. r = 52 most significant bits
    seed = hmac_hex[:n_bits // 4]  # Slice to get the 52 most significant bits
    r = int(seed, 16)

    # 3. X = r / 2^52
    X = r / (2 ** n_bits)  # uniformly distributed in [0; 1)
    X = round(X, 9)  # Round to 9 decimal places as in the JS version

    # 4. X = 99 / (1 - X)
    X = 99 / (1 - X)

    # 5. return max(trunc(X), 100)
    result = int(X)  # Truncate X by converting to an integer
    return max(1, result / 100)

_hash = None
app = Flask(__name__)
socketio = SocketIO(app)
def background_scraping():
    while True:
        data = scrape_crash_game_data()
        if data == None :
            continue
        global _hash
        # if sha256_hash(data) != _hash:
        temp = data
        _hash = data
        results = []
        for _ in range(10):
            temp1 = game_result(temp, _salt)
            results.append(temp1)
            temp = sha256_hash(temp)
            
        socketio.emit('update_data', {'data': results})
        time.sleep(1)  # Scrape every 10 seconds

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('request_info')  # Listen for 'request_info' event from the client
def handle_request_info():
    # Send the current first_game_hash to the client
    socketio.emit('send_info', {'info': 'Data'})

if __name__ == '__main__':
    threading.Thread(target=background_scraping).start()
    threading.Thread(target=scrape_background).start()
    socketio.run(app, port=5000)
    
