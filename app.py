from flask import Flask, render_template, request, redirect
import sqlite3
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configure application
app = Flask(__name__)

# Ensure that templates are auto-reloaded whenever a file changes
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configuring database
conn = sqlite3.connect('rankings.db')
conn.execute('CREATE TABLE IF NOT EXISTS rating (team TEXT, rating FLOAT)')
cur = conn.cursor()
cur.execute('DELETE FROM rating')
conn.commit()

# Loading the top 20 ranked teams into the database by web scraping the official Wikipedia page for FIFA Ranking
URL = 'https://en.wikipedia.org/wiki/FIFA_Men%27s_World_Rankings'
page = requests.get(URL)
soup = BeautifulSoup(page.text, 'lxml')
table1 = soup.find('table')
teams_list = []
for j in table1.find_all('tr')[3:23]:
    row_data = j.find_all('td')
    row = []
    row.append(row_data[2].text.lstrip('\xa0'))
    row.append(row_data[3].text.rstrip('\n'))
    cur = conn.cursor()
    cur.execute('INSERT INTO rating (team, rating) VALUES(?, ?)', (row[0], row[1]))
    conn.commit()
    teams_list.append(row[0].lower())

conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Displays the ranking table on the home page
        conn = sqlite3.connect('rankings.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT ROW_NUMBER() OVER(ORDER BY rating DESC) rank, team, rating FROM rating')
        rows = cur.fetchall()
        conn.close()
        return render_template('index.html', rows=rows)

    else:
        # Updates rating based on the result of a match
        # Official formula: https://digitalhub.fifa.com/m/f99da4f73212220/original/edbm045h0udbwkqew35a-pdf.pdf
        team1 = request.form.get('team1')
        team2 = request.form.get('team2')
        result = request.form.get('result')
        imp = request.form.get('imp')
        if team1 and team2 and team1.lower() in teams_list and team2.lower() in teams_list and result is not None and imp and team1.lower() != team2.lower():
            result = int(result)
            imp = int(imp)
            with sqlite3.connect('rankings.db') as conn:
                cur = conn.cursor()
                cur.execute('SELECT rating FROM rating WHERE LOWER(team) = ?', (team1.lower(), ))
                team1_rating = (cur.fetchall())[0]
                team1_rating = team1_rating[0]
                cur.execute('SELECT rating FROM rating WHERE LOWER(team) = ?', (team2.lower(), ))
                team2_rating = (cur.fetchall())[0]
                team2_rating = team2_rating[0]

                if result > 0:
                    change = imp * (1 - 1 / (1 + 10**(-(team1_rating - team2_rating) / 600)))
                    team1_rating += change
                    team2_rating -= change

                elif result < 0:
                    change = imp * (1 - 1 / (1 + 10**(-(team2_rating - team1_rating) / 600)))
                    team1_rating -= change
                    team2_rating += change

                else:
                    team1_rating += imp * (0.5 - 1 / (1 + 10**(-(team1_rating - team2_rating) / 600)))
                    team2_rating += imp * (0.5 - 1 / (1 + 10**(-(team2_rating - team1_rating) / 600)))

                cur.execute('UPDATE rating SET rating = ? WHERE LOWER(team) = ?', (round(team1_rating, 2), team1.lower()))
                conn.commit()
                cur.execute('UPDATE rating SET rating = ? WHERE LOWER(team) = ?', (round(team2_rating, 2), team2.lower()))
                conn.commit()

        # Adds a team to the database
        team = request.form.get('team')
        rating = request.form.get('rating')
        if team and rating and team.lower() not in teams_list:
            with sqlite3.connect('rankings.db') as conn:
                cur = conn.cursor()
                letters = list(team)
                letters[0] = letters[0].upper()
                for i in range(1, len(letters)):
                    if letters[i-1] == ' ':
                        letters[i] = letters[i].upper()
                    else:
                        letters[i] = letters[i].lower()
                team = ''.join(str(letter) for letter in letters)
                cur.execute('INSERT INTO rating (team, rating) VALUES(?, ?)', (team, rating))
                conn.commit()
                teams_list.append(team.lower())

        # Changes the rating of an existing team in the database
        if team and rating and team.lower() in teams_list:
            with sqlite3.connect('rankings.db') as conn:
                cur = conn.cursor()
                cur.execute('UPDATE rating SET rating = ? WHERE LOWER(team) = ?', (rating, team.lower()))
                conn.commit()

        # Deletes a team from the database
        delete = request.form.get('delete')
        if delete:
            with sqlite3.connect('rankings.db') as conn:
                cur = conn.cursor()
                cur.execute('DELETE FROM rating WHERE LOWER(team) = ?', (delete.lower(), ))
                conn.commit()

        return redirect("/")
