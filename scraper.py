import time 
from selenium import webdriver 
from datetime import datetime 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
import requests
import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Usage
canvas_selector = "#myCanvas"  # Replace with the appropriate CSS selector for the canvas
output_filename = "output_canvas.png"  # The name of the output PNG file

# Set up ChromeDriver service
service = Service('driver/chromedriver.exe')

options = webdriver.ChromeOptions()

#run in headless mode
options.add_argument("--headless")

# disable the AutomationControlled feature of Blink rendering engine
options.add_argument('--disable-blink-features=AutomationControlled')

# disable pop-up blocking
options.add_argument('--disable-popup-blocking')

# start the browser window in maximized mode
options.add_argument('--start-maximized')

# disable extensions
options.add_argument('--disable-extensions')

# disable sandbox mode
options.add_argument('--no-sandbox')

# disable shared memory usage
options.add_argument('--disable-dev-shm-usage')

# Initialize Chrome with both service and options
driver = webdriver.Chrome(service=service, options=options) 

url = 'https://bc.game/game/crash'

driver.get(url) 
time.sleep(5)

# Define a global variable to store the first_game_hash data
first_game_hash = None

def scrape_crash_game_data():
    return first_game_hash  # Declare the global variable to modify it

def scrape_background():
    while(True): 
        time.sleep(3)
        try:
            def post_data_to_api(data_to_post):
                script = f"""
                return fetch('https://bc.game/api/game/bet/multi/history', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({json.dumps(data_to_post)})
                }}).then(response => response.json());
                """
                return driver.execute_script(script)

            data_to_post = {
                'gameUrl':"crash",
                'page':1,
                'pageSize':50,
            }

            try:
                response = post_data_to_api(data_to_post)
                if isinstance(response, dict):
                    first_game_Detail = response.get('data', {}).get('list', [{}])[0].get('gameDetail', {})
                    if first_game_Detail:
                        game_hash = json.loads(first_game_Detail)
                        global first_game_hash
                        first_game_hash = game_hash.get('hash', {})
                    else:
                        print("First game hash not found in the response.")
                else:
                    print("Invalid response format.")
            except Exception as e:
                print(f"Failed to fetch data: {e}")
        except Exception as e:
            print(f"An error occurred while posting data: {e}") 
