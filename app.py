from flask import Flask, render_template, request
import sqlite3

# Configure application
app = Flask(__name__)

# Ensure that templates are auto-reloaded whenever a file changes
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configuring database
conn = sqlite3.connect('rankings.db')
conn.execute('CREATE TABLE IF NOT EXISTS rating (rank INT, team TEXT, rating FLOAT)')
conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        with sqlite3.connect('rankings.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM rating')
            rows = cur.fetchall()
            conn.commit()
        return render_template('index.html', rows=rows)