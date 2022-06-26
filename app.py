from flask import Flask
import sqlite3

# Configure application
app = Flask(__name__)

# Ensure that templates are auto-reloaded whenever a file changes
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configuring database
conn = sqlite3.connect('rankings.db')
conn.execute('CREATE TABLE IF NOT EXISTS rating (rank INT, team TEXT, rating FLOAT)')
conn.close()

@app.route('/')
def index():
    return 'hello'