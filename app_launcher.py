import webbrowser
import os
import sys
import threading
import time
from app import app, server

# Function to open browser after a short delay
def open_browser():
    # Wait for the server to start
    time.sleep(2)
    # Open browser
    webbrowser.open('http://127.0.0.1:8050/')

if __name__ == '__main__':
    # Start the browser in a separate thread
    threading.Thread(target=open_browser).start()
    
    # Run the app
    app.run_server(debug=False) 