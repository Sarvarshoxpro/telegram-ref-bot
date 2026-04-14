from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

HTML = """
<h2>🎁 Giveaway Admin Panel</h2>

<h3>🏆 TOP 10</h3>
<ul>
{% for user in users %}
<li>@{{user[0]}} — {{user[1]}} ta</li>
{% endfor %}
</ul>

<form action="/reset">
<button>♻️ Reset Contest</button>
</form>
"""

@app.route("/")
def home():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    
    cur.execute("SELECT username, referrals FROM users ORDER BY referrals DESC LIMIT 10")
    users = cur.fetchall()
    
    conn.close()
    
    return render_template_string(HTML, users=users)


@app.route("/reset")
def reset():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    
    cur.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    
    return "✅ Contest reset qilindi"


app.run(host="0.0.0.0", port=10000)
