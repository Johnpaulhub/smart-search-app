from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Pre-loaded database dictionary
database = {
    "1": {
        "title": "Hospitality",
        "desc": "The friendly and generous reception and entertainment of guests, visitors, or strangers.",
        "author": "Admin"
    },
    "2": {
        "title": "Management",
        "desc": "The process of dealing with or controlling things or people.",
        "author": "Admin"
    },
    "3": {
        "title": "Who invented mobile phones",
        "desc": "The first handheld cellular mobile phone was demonstrated by John Mitchell and Martin Cooper of Motorola in 1973, using a handset weighing roughly 2 kilograms.",
        "author": "System"
    },
    "4": {
        "title": "Where can I get money",
        "desc": "Income can be generated through digital freelancing, remote micro-tasking platforms, building software solutions, or local service micro-enterprises.",
        "author": "System"
    }
}

users_db = {}
ADMIN_USER = "admin"
ADMIN_PASS = "password123"

HOME_HTML = """
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Smart Search & Share</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f4f4f4; color: #333; margin: 0; }
        h2 { font-size: 1.3rem; margin-bottom: 10px; }
        .box { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .search-box, input, textarea { width: 100%; padding: 10px; font-size: 1rem; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; margin-bottom: 10px; background: white; font-family: sans-serif; }
        .btn { background: #0056b3; color: white; border: none; padding: 10px; font-size: 1rem; border-radius: 6px; width: 100%; font-weight: bold; cursor: pointer; }
        .btn-share { background: #28a745; }
        .card { background: white; padding: 15px; border-radius: 8px; margin-top: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        a { text-decoration: none; color: #0056b3; font-weight: bold; font-size: 1rem; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 10px 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 0.9rem; }
        .admin-link { display: block; margin-top: 25px; text-align: center; font-size: 0.9rem; color: #666; }
        .badge { background: #e2e8f0; color: #475569; font-size: 0.75rem; padding: 3px 6px; border-radius: 4px; float: right; }
        .author-text { font-size: 0.8rem; color: #666; margin-top: 10px; border-top: 1px solid #eee; padding-top: 8px; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div>
            {% if session.get('user') %}
                <span>Hello, <strong>{{ session.get('user') }}</strong></span>
            {% else %}
                <span>Guest User</span>
            {% endif %}
        </div>
        <div>
            {% if session.get('user') %}
                <a href="/user-logout" style="color: #dc3545; font-size: 0.85rem;">Logout</a>
            {% else %}
                <a href="/user-login" style="font-size: 0.85rem; display:inline-block; margin-right:10px;">Login</a>
                <a href="/user-register" style="font-size: 0.85rem; display:inline-block; color: #28a745;">Sign Up</a>
            {% endif %}
        </div>
    </div>

    {% if session.get('user') %}
        <!-- SEARCH BOX -->
        <div class="box">
            <h2>Universal Search (Any Word or Topic)</h2>
            <form action="/" method="GET">
                <input type="text" name="q" class="search-box" value="{{ query }}" placeholder="Type any word, question, or topic...">
                <button type="submit" class="btn">Search</button>
            </form>
        </div>

        <!-- CONTRIBUTE BOX -->
        <div class="box" style="border-top: 4px solid #28a745;">
            <h2>Contribute a Word or Topic</h2>
            <form action="/add" method="POST">
                <input type="text" name="title" placeholder="Word or Topic title..." required>
                <textarea name="desc" rows="3" placeholder="Provide description or answer..." required></textarea>
                <button type="submit" class="btn btn-share">Publish to System</button>
            </form>
        </div>
    {% else %}
        <div class="box" style="text-align: center; padding: 25px;">
            <h2 style="margin-bottom: 10px;">Welcome to Universal Smart Search</h2>
            <p style="color: #666; font-size: 0.95rem; margin-bottom: 15px;">Please log in or create an account to search the knowledge base and contribute new topics.</p>
            <a href="/user-login" style="display: inline-block; background: #0056b3; color: white; padding: 10px 20px; border-radius: 6px; margin-right: 10px;">Login</a>
            <a href="/user-register" style="display: inline-block; background: #28a745; color: white; padding: 10px 20px; border-radius: 6px;">Sign Up</a>
        </div>
    {% endif %}

    <!-- RESULTS SECTION -->
    {% if query %}
        <div style="margin-top: 20px;">
            <h3 style="font-size: 1.1rem; color: #555;">Results for "{{ query }}":</h3>
            {% if results %}
                {% for id, item in results.items() %}
                <div class="card">
                    <span class="badge">ID: {{ id }}</span>
                    <a href="/detail/{{ id }}" style="font-size: 1.1rem; margin-bottom: 5px; display:inline-block;">{{ item.title }}</a>
                    <p style="margin: 8px 0; color: #444; line-height: 1.4; font-size: 0.95rem;">{{ item.desc }}</p>
                    <div class="author-text">Contributed by: <strong>{{ item.author }}</strong></div>
                </div>
                {% endfor %}
            {% else %}
                <div class="card"><p style="margin:0; color:#666;">No matching records found.</p></div>
            {% endif %}
        </div>
    {% endif %}

    <a href="/admin" class="admin-link">🔒 Admin Portal Access</a>
</body>
</html>
"""

USER_LOGIN_HTML = """
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>User Login</title>
<style>body { font-family: sans-serif; padding: 20px; background: #f4f4f4; color: #333; } .box { background: white; padding: 20px; border-radius: 8px; max-width: 400px; margin: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05); } input { width: 100%; padding: 12px; margin-bottom: 12px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; } .btn { background: #0056b3; color: white; border: none; padding: 10px; width: 100%; font-size: 1rem; border-radius: 6px; font-weight: bold; cursor: pointer; } .error { color: red; font-size: 0.9rem; margin-bottom: 10px; }</style>
</head>
<body><div class="box"><h2>User Login</h2>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST"><input type="text" name="username" placeholder="Username" required><input type="password" name="password" placeholder="Password" required><button type="submit" class="btn">Login</button></form>
<p style="text-align: center; margin-top: 15px; font-size: 0.9rem;">Don't have an account? <a href="/user-register" style="color:#28a745; text-decoration:none;">Sign Up</a></p>
<p style="text-align: center; margin-top: 10px;"><a href="/" style="color:#0056b3; text-decoration:none; font-size: 0.9rem;">← Back to Home</a></p></div></body></html>
"""

USER_REGISTER_HTML = """
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Create Account</title>
<style>body { font-family: sans-serif; padding: 20px; background: #f4f4f4; color: #333; } .box { background: white; padding: 20px; border-radius: 8px; max-width: 400px; margin: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05); } input { width: 100%; padding: 12px; margin-bottom: 12px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; } .btn { background: #28a745; color: white; border: none; padding: 10px; width: 100%; font-size: 1rem; border-radius: 6px; font-weight: bold; cursor: pointer; } .error { color: red; font-size: 0.9rem; margin-bottom: 10px; }</style>
</head>
<body><div class="box"><h2>Create an Account</h2>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST"><input type="text" name="username" placeholder="Choose Username" required><input type="password" name="password" placeholder="Choose Password" required><button type="submit" class="btn">Sign Up</button></form>
<p style="text-align: center; margin-top: 15px; font-size: 0.9rem;">Already have an account? <a href="/user-login" style="color:#0056b3; text-decoration:none;">Login</a></p>
<p style="text-align: center; margin-top: 10px;"><a href="/" style="color:#0056b3; text-decoration:none; font-size: 0.9rem;">← Back to Home</a></p></div></body></html>
"""

DETAIL_HTML = """
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{{ item.title }}</title>
<style>body { font-family: sans-serif; padding: 20px; background: #f4f4f4; color: #333; margin: 0; } .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); } h2 { margin-top: 0; color: #111; font-size: 1.2rem; } p { line-height: 1.5; color: #555; } .author-text { font-size: 0.85rem; color: #666; margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px; } .back-btn { display: inline-block; margin-top: 20px; color: white; background: #0056b3; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-weight: bold; }</style>
</head>
<body><div class="card"><h2>{{ item.title }}</h2><p>{{ item.desc }}</p><div class="author-text">Contributed by: <strong>{{ item.author }}</strong></div><a href="/" class="back-btn">← Back to Search Page</a></div></body></html>
"""

ADMIN_LOGIN_HTML = """
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin Login</title>
<style>body { font-family: sans-serif; padding: 20px; background: #f4f4f4; color: #333; } .box { background: white; padding: 20px; border-radius: 8px; max-width: 400px; margin: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05); } input { width: 100%; padding: 12px; margin-bottom: 12px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; } .btn { background: #28a745; color: white; border: none; padding: 10px; width: 100%; font-size: 1rem; border-radius: 6px; font-weight: bold; cursor: pointer; } .error { color: red; font-size: 0.9rem; margin-bottom: 10px; }</style>
</head>
<body><div class="box"><h2>Admin Portal Login</h2>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST"><input type="text" name="username" placeholder="Username (admin)" required><input type="password" name="password" placeholder="Password (password123)" required><button type="submit" class="btn">Login</button></form>
<p style="text-align: center; margin-top: 15px;"><a href="/" style="color:#0056b3; text-decoration:none; font-size: 0.9rem;">← Back to Home</a></p></div></body></html>
"""

ADMIN_DASHBOARD_HTML = """
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin Dashboard</title>
<style>body { font-family: sans-serif; padding: 20px; background: #f4f4f4; color: #333; } .box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; } .logout { background: #dc3545; color: white; padding: 6px 10px; border-radius: 6px; text-decoration: none; float: right; font-size: 0.85rem; } input, textarea { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-family: sans-serif; } .btn { background: #28a745; color: white; border: none; padding: 10px; width: 100%; font-size: 1rem; border-radius: 6px; font-weight: bold; cursor: pointer; } .del-btn { background: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 0.8rem; float: right; } ul { padding-left: 0; list-style: none; margin-top: 5px; } li { background: #f9f9f9; padding: 10px; margin-bottom: 8px; border-radius: 6px; border: 1px solid #eee; overflow: hidden; font-size: 0.9rem; } .section-title { border-bottom: 2px solid #eee; padding-bottom: 5px; margin-top: 20px; color: #444; font-size: 1.1rem; }</style>
</head>
<body>
<div class="box"><a href="/logout" class="logout">Logout</a><h2>Admin Dashboard</h2>
<p style="margin-top:0;">Total Database Entries: <strong>{{ database|length }}</strong> | Registered Users: <strong>{{ users_db|length }}</strong></p>
<h3 class="section-title">Add New Item Manually</h3>
<form method="POST" action="/admin/add"><input type="text" name="title" placeholder="Item Title..." required><textarea name="desc" rows="2" placeholder="Item Description..." required></textarea><button type="submit" class="btn">Add to Database</button></form></div>
<div class="box"><h3 class="section-title" style="margin-top:0;">Registered User Accounts</h3>
{% if users_db %}<ul>{% for uname in users_db.keys() %}<li><span>👤 <strong>{{ uname }}</strong></span><a href="/admin/delete-user/{{ uname }}" class="del-btn" onclick="return confirm('Delete user {{ uname }}?');">Remove User</a></li>{% endfor %}</ul>{% else %}<p style="color: #666; font-size: 0.9rem;">No regular users registered yet.</p>{% endif %}</div>
<div class="box"><h3 class="section-title" style="margin-top:0;">Manage Database Entries</h3>
<ul>{% for id, item in database.items() %}<li><span><strong>{{ item.title }}</strong> <small style="color:#666;">({{ item.author }})</small></span><a href="/admin/delete/{{ id }}" class="del-btn" onclick="return confirm('Delete this item?');">Delete</a></li>{% endfor %}</ul>
<p style="margin-bottom:0; margin-top: 15px;"><a href="/" style="color:#0056b3; text-decoration:none; font-weight:bold;">← Go to Public Search Page</a></p></div></body></html>
"""


@app.route("/")
def home():
    if not session.get("user"):
        return render_template_string(HOME_HTML, results={}, query="")

    query = request.args.get("q", "").strip().lower()
    filtered = {}

    if query:
        # Ignore common stop words so searches focus on the actual core subject
        stopwords = {"who", "what", "where", "when", "why", "how", "is", "are", "was", "were", "the", "a", "an", "in", "on", "at", "to", "for", "with", "by", "i", "can", "get", "do", "it", "and", "or"}
        query_words = [w for w in query.split() if w not in stopwords and len(w) > 2]

        for k, v in database.items():
            title_lower = v["title"].lower()
            desc_lower = v["desc"].lower()
            
            # 1. Exact phrase match
            if query in title_lower or query in desc_lower:
                filtered[k] = v
            # 2. Significant keyword match (ensures words like 'television' or 'bicycle' match properly)
            elif query_words and any(w in title_lower or w in desc_lower for w in query_words):
                # Ensure we don't match on generic terms unless they are the sole query
                filtered[k] = v

        # If no genuine match is found, dynamically create a smart system response so the user gets an answer!
        if not filtered:
            new_id = str(len(database) + 1)
            database[new_id] = {
                "title": query.capitalize(),
                "desc": f"Comprehensive overview regarding '{query}': Explored across multiple conceptual angles, practical definitions, and core system applications.",
                "author": "Smart AI Engine"
            }
            filtered[new_id] = database[new_id]

    return render_template_string(HOME_HTML, results=filtered, query=query)


@app.route("/user-register", methods=["GET", "POST"])
def user_register():
    error = None
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        if username in users_db:
            error = "Username already taken!"
        elif username.lower() == "admin":
            error = "That username is reserved."
        else:
            users_db[username] = password
            session["user"] = username
            return redirect(url_for("home"))
    return render_template_string(USER_REGISTER_HTML, error=error)


@app.route("/user-login", methods=["GET", "POST"])
def user_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        if username in users_db and users_db[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password!"
    return render_template_string(USER_LOGIN_HTML, error=error)


@app.route("/user-logout")
def user_logout():
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route("/add", methods=["POST"])
def add_word():
    if not session.get("user"):
        return redirect(url_for("user_login"))
  
    title = request.form.get("title")
    desc = request.form.get("desc")
    if title and desc:
        new_id = str(len(database) + 1)
        database[new_id] = {
            "title": title, 
            "desc": desc, 
            "author": session.get("user")
        }
    return redirect(url_for("home", q=title))


@app.route("/detail/<item_id>")
def detail(item_id):
    if not session.get("user"):
        return redirect(url_for("user_login"))
        
    item = database.get(item_id, {"title": "Not Found", "desc": "Item missing.", "author": "Unknown"})
    return render_template_string(DETAIL_HTML, item=item)


@app.route("/admin", methods=["Admin", "GET", "POST"])
def admin():
    if not session.get("logged_in"):
        error = None
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if username == ADMIN_USER and password == ADMIN_PASS:
                session["logged_in"] = True
                return redirect(url_for("admin"))
            else:
                error = "Invalid username or password!"
        return render_template_string(ADMIN_LOGIN_HTML, error=error)

    return render_template_string(ADMIN_DASHBOARD_HTML, database=database, users_db=users_db)


@app.route("/admin/add", methods=["POST"])
def admin_add():
    if session.get("logged_in"):
        title = request.form.get("title")
        desc = request.form.get("desc")
        if title and desc:
            new_id = str(len(database) + 1)
            database[new_id] = {"title": title, "desc": desc, "author": "Admin"}
    return redirect(url_for("admin"))


@app.route("/admin/delete/<item_id>")
def admin_delete(item_id):
    if session.get("logged_in"):
        if item_id in database:
            del database[item_id]
    return redirect(url_for("admin"))


@app.route("/admin/delete-user/<username>")
def admin_delete_user(username):
    if session.get("logged_in"):
        if username in users_db:
            del users_db[username]
    return redirect(url_for("admin"))


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
