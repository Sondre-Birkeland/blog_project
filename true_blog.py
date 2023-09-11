import mysql.connector
from flask import *
import hashlib
#En liten endring

f = open("C:\\Users\\Ares\\Documents\\Programmer\\Hybrid\\Blog Project\\MySQLpswd.txt", "r")
MySQLpswd = f.read()
f.close()

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = MySQLpswd,
    database = "blog"
)

cur = mydb.cursor()

app = Flask(__name__)

app.secret_key = "fbf8a67df394908936e4fae8aa5d12cc46b6ad92ef90fbef04f8b68917ad5f77"

def get_post_data(id):
    if "user_id" in session:
        cur.execute("""SELECT username, title, content, created_at, COUNT(post_likes.id), posts.id IN (SELECT post_id FROM post_likes WHERE user_id = %s)
            FROM posts 
            JOIN users ON users.id = posts.user_id 
            LEFT JOIN post_likes ON post_likes.post_id = posts.id
            WHERE posts.id = %s""", (session["user_id"], id))
        post = cur.fetchone()
        cur.execute("""SELECT username, content, created_at, COUNT(comment_likes.id), comments.id IN (SELECT comment_id FROM comment_likes WHERE user_id = %s), comments.id
            FROM comments 
            JOIN users ON users.id = comments.user_id 
            LEFT JOIN comment_likes ON comment_likes.comment_id = comments.id
            WHERE post_id = %s
            GROUP BY comments.id""", (session["user_id"], id))
        comments = cur.fetchall()
    else:
        cur.execute("""SELECT username, title, content, created_at, COUNT(post_likes.id)
            FROM posts 
            JOIN users ON users.id = posts.user_id 
            LEFT JOIN post_likes ON post_likes.post_id = posts.id
            WHERE posts.id = %s""", (id, ))
        post = cur.fetchone()
        cur.execute("""SELECT username, content, created_at, COUNT(comment_likes.id)
            FROM comments 
            JOIN users ON users.id = comments.user_id 
            LEFT JOIN comment_likes ON comment_likes.comment_id = comments.id
            WHERE post_id = %s
            GROUP BY comments.id""", (id, ))
        comments = cur.fetchall()
    cur.execute("SELECT * FROM tags JOIN post_tags ON tags.id = post_tags.tag_id WHERE post_id = %s", (id, ))
    tags = cur.fetchall()
    return post, comments, tags

def like_handler(id):
    try:
        if "like" in request.form:
            cur.execute("INSERT INTO post_likes(user_id, post_id) VALUES (%s, %s)", (session["user_id"], id))
            mydb.commit()
        elif "dislike" in request.form:
            cur.execute("DELETE FROM post_likes WHERE user_id = %s AND post_id = %s", (session["user_id"], id))
        elif "comment_like" in request.form:
            cur.execute("INSERT INTO comment_likes(user_id, comment_id) VALUES (%s, %s)", (session["user_id"], request.form["comment_id"]))
        elif "comment_dislike" in request.form:
            cur.execute("DELETE FROM comment_likes WHERE user_id = %s AND comment_id = %s", (session["user_id"], request.form["comment_id"]))
    except:
        pass

@app.route("/")
def index():
    cur.execute("SELECT posts.id, username, title, created_at FROM posts LEFT JOIN users ON users.id = posts.user_id")
    posts = cur.fetchall()
    return render_template("index.html", posts = posts)

@app.route("/<int:id>", methods=["GET", "POST"])
def show_post(id):
    if request.method == "POST":
        if "content" in request.form:
            cur.execute("INSERT INTO comments(user_id, post_id, content) VALUES (%s, %s, %s)", (session["user_id"], id, request.form["content"]))
            mydb.commit()
        else:
            like_handler(id)
    post, comments, tags = get_post_data(id)
    return render_template("show_post.html", post=post, comments=comments, tags=tags, post_id=id)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        pswd = request.form["password"]
        h = hashlib.sha256()
        h.update(bytes(pswd, 'utf-8'))
        cur.execute("SELECT id, is_admin FROM users WHERE username = %s AND password = %s", (request.form["username"], h.hexdigest()))
        user = cur.fetchone()
        if user:
            session["user_id"] = user[0]
            session["user_is_admin"] = user[1]
            return redirect(url_for("index"))
        else:
            error = "Incorrect username or password"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_is_admin", None)
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        pswd = request.form["password"]
        h = hashlib.sha256()
        h.update(bytes(pswd, "utf-8"))
        hashed_pswd = h.hexdigest()
        try:
            cur.execute("INSERT INTO users(username, password) VALUES (%s, %s)", (request.form["username"], hashed_pswd))
            mydb.commit()
            return redirect(url_for("index"))
        except:
            error = "username is already taken"
    return render_template("register.html", error=error)

@app.route("/post", methods=["GET", "POST"])
def make_post():
    if "user_id" in session and session["user_is_admin"]:
        if request.method == "POST":
            cur.execute("INSERT INTO posts(title, content, user_id) VALUES(%s, %s, %s)", (request.form["title"], request.form["content"], session["user_id"]))
            cur.execute("SELECT id FROM posts ORDER BY id DESC LIMIT 1")
            newpost_id = cur.fetchone()[0]
            if "tags" in request.form:
                tagset = [(newpost_id, tag) for tag in request.form.getlist("tags")]
                cur.executemany("INSERT INTO post_tags(post_id, tag_id) VALUES (%s, %s)", tagset)
                mydb.commit()
            return redirect(url_for("show_post", id=newpost_id))
        cur.execute("SELECT * FROM tags")
        return render_template("make_post.html", tags=cur.fetchall())
    else:
        return redirect(url_for("index"))

@app.route("/search/tags/<int:id>")
def tag_search(id):
    cur.execute("SELECT posts.id, username, title, created_at FROM posts LEFT JOIN users ON users.id = posts.user_id JOIN post_tags ON posts.id = post_tags.post_id WHERE tag_id = %s", (id, ))
    posts = cur.fetchall()
    return render_template("tag_search.html", posts=posts)

@app.route("/search", methods=["POST"])
def search():
    query = '%'+request.form["search_bar"]+'%'
    cur.execute("SELECT posts.id, username, title, created_at FROM posts LEFT JOIN users ON users.id = posts.user_id WHERE title LIKE %s OR content LIKE %s", (query, query))
    posts = cur.fetchall()
    return render_template("search.html", posts=posts)

@app.route("/tag_editor", methods=["GET", "POST"])
def tag_edit():
    if "user_id" in session and session["user_is_admin"]:
        if request.method == "POST":
            if "bad_tags" in request.form:
                bad_tags = [(tag, ) for tag in request.form.getlist("bad_tags")]
                cur.executemany("DELETE FROM tags WHERE id = %s", bad_tags)
                mydb.commit()
            elif "name" in request.form:
                new_tag = request.form["name"]
                cur.execute("INSERT INTO tags(name) VALUES (%s)", (new_tag, ))
                mydb.commit()
        cur.execute("SELECT * FROM tags")
        tags = cur.fetchall()
        return render_template("tag_editor.html", tags=tags)
    else:
        return redirect(url_for("index"))

@app.route("/<int:id>/tags", methods=["GET", "POST"])
def post_tag_edit(id):
    if "user_id" in session and session["user_is_admin"]:
        if request.method == "POST":
            if "bad_tags" in request.form:
                bad_tags = [(id, tag) for tag in request.form.getlist("bad_tags")]
                cur.executemany("DELETE FROM post_tags WHERE post_id = %s AND tag_id = %s", bad_tags)
                mydb.commit()
            elif "good_tags" in request.form:
                good_tags = [(id, tag) for tag in request.form.getlist("good_tags")]
                cur.executemany("INSERT INTO post_tags(post_id, tag_id) VALUES (%s, %s)", good_tags)
                mydb.commit()
            return redirect(url_for("show_post", id=id))
        cur.execute("SELECT tag_id, name FROM post_tags LEFT JOIN tags ON post_tags.tag_id=tags.id WHERE post_id=%s", (id, ))
        present_tags=cur.fetchall()
        cur.execute("SELECT * FROM tags WHERE id NOT IN (SELECT tag_id FROM post_tags WHERE post_id=%s)", (id, ))
        absent_tags=cur.fetchall()
        return render_template("post_tag_editor.html", present_tags=present_tags, absent_tags=absent_tags) #Make a new template for this?
    else:
        return redirect(url_for("show_post", id=id))
