from flask import Flask, render_template, request, redirect
import sqlite3

# Configure application
app = Flask(__name__)

# Ensure that templates are auto-reloaded whenever a file changes
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configuring database
conn = sqlite3.connect('rankings.db')
conn.execute('CREATE TABLE IF NOT EXISTS rating (team TEXT, rating FLOAT)')
cur = conn.cursor()
cur.execute('DELETE FROM rating')
conn.commit()
conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        conn = sqlite3.connect('rankings.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT ROW_NUMBER() OVER(ORDER BY rating DESC) rank, team, rating FROM rating')
        rows = cur.fetchall()
        return render_template('index.html', rows=rows)

    else:
        team = request.form.get("team")
        rating = request.form.get("rating")

        if team and rating:
            with sqlite3.connect("rankings.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO rating (team, rating) VALUES(?, ?)", (team, rating))
                con.commit()
        return redirect("/")