from flask import Flask, redirect, request, render_template, flash, session
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "test"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register_user", methods=['POST'])
def register_user():
    is_valid = True
    if len(request.form['fn']) < 1:
        is_valid = False
        flash("Please enter a first name")
    if len(request.form['ln']) < 1:
        is_valid = False
        flash("Please enter a last name")
    if len(request.form['em']) < 1:
        is_valid = False
        flash("Please enter an email")
    if len(request.form['pw']) <= 5:
        is_valid = False
        flash("Password must be at least 5 long")
    if request.form['pw'] != request.form['cpw']:
        is_valid = False
        flash("Passwords don't match")
        
    if not request.form['fn'].isalpha():
        is_valid = False
        flash("First name can not contain numbers")
    if not request.form['ln'].isalpha():
        is_valid = False
        flash("Last name can not contain numbers")
    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("Invalid email address!")
        
    if is_valid:
        mysql = connectToMySQL("thought_dashboard")
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW())"
        hashed_pw = bcrypt.generate_password_hash(request.form['pw'])
        data = {
            "fn": request.form['fn'],
            "ln": request.form['ln'],
            "em": request.form['em'],
            "pw": hashed_pw
        }
        user_id = mysql.query_db(query, data)
        if user_id:
            session['user_id'] = user_id
        return redirect("/thoughts")
    else:
        return redirect("/")
    
@app.route("/login_user", methods=['POST'])
def login_user():
    is_valid = True
    if len(request.form['lem']) < 1:
        is_valid = False
        flash("Email cannot be blank")
    if len(request.form['lpw']) < 1:
        is_valid = False
        flash("Password cannot be blank")
    
    if not is_valid:
        return redirect("/")
    
    mysql = connectToMySQL("thought_dashboard")
    query = "SELECT * FROM users WHERE email=%(lem)s"
    data = {"lem": request.form['lem']}
    result = mysql.query_db(query, data)
    
    if result:
        user_data = result[0]
        if bcrypt.check_password_hash(user_data['password'], request.form['lpw']):
            session['user_id'] = user_data['id_user']
            return redirect("/thoughts")
        else:
            flash("Invalid Email or Password used.")
            return redirect("/")
    else:
        flash("Email doesn't exist")
        return redirect("/")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/thoughts")
def dashboard():
    if 'user_id' not in session:
        return redirect("/")
    
    mysql = connectToMySQL("thought_dashboard")
    query = "SELECT * FROM users WHERE id_user = %(id)s"
    data = {'id': session['user_id']}
    users = mysql.query_db(query, data)
    
    mysql = connectToMySQL("thought_dashboard")
    query = "SELECT users.first_name, users.last_name, thoughts.id_thought, thoughts.thought, COUNT(thoughts_id_thought) as times_liked FROM users_thoughts RIGHT JOIN thoughts ON thoughts.id_thought = users_thoughts.thoughts_id_thought JOIN users ON thoughts.user_id = users.id_user GROUP BY thoughts_id_thought ORDER BY times_liked DESC"
    all_thoughts = mysql.query_db(query)
    print(all_thoughts)
    mysql = connectToMySQL("thought_dashboard")
    query = "SELECT * FROM users_thoughts WHERE users_id_user = %(user_id)s"
    data = {'user_id': session['user_id']}
    liked_thoughts = [thought['thoughts_id_thought'] for thought in mysql.query_db(query, data)]
    
    if all_thoughts:
        for thought in all_thoughts:
            if thought['id_thought'] in liked_thoughts:
                thought['already_liked'] = True
            else:
                thought['already_liked'] = False
                
    return render_template("thoughts.html", user=users[0], thoughts=all_thoughts)

@app.route("/thoughts/create", methods=['POST'])
def on_create():
    is_valid = True
    
    if len(request.form['thought_content']) < 5:
        is_valid = False
        flash("Thought content must be at least 5 characters long")
    if len(request.form['thought_content']) > 256:
        is_valid = False
        flash("Thought content can not be more than 255 characters long")
        
    if is_valid:
        mysql = connectToMySQL("thought_dashboard")
        query = "INSERT INTO thoughts (thought, user_id, created_at, updated_at) VALUES (%(cont)s, %(author_id)s, NOW(), NOW())"
        data = {
            'cont': request.form['thought_content'],
            'author_id': session['user_id']
        }
        mysql.query_db(query, data)
    
    return redirect("/thoughts")
    
@app.route("/thoughts/details/<thought_id>")
def thought_detail(thought_id):
    mysql = connectToMySQL("thought_dashboard")
    query = "SELECT users.first_name, users.id_user, thoughts.thought, thoughts.id_thought FROM thoughts JOIN users ON thoughts.user_id = users.id_user WHERE thoughts.id_thought = %(thought_id)s"
    data = {'thought_id': thought_id}
    all_thoughts = mysql.query_db(query, data)
    
    mysql = connectToMySQL("thought_dashboard")
    query = "SELECT * FROM users_thoughts WHERE users_id_user = %(user_id)s"
    data = {'user_id': session['user_id']}
    liked_thoughts = [thought['thoughts_id_thought'] for thought in mysql.query_db(query, data)]
    
    mysql = connectToMySQL("thought_dashboard")
    query = "SELECT users.first_name, users.last_name, users.id_user FROM thoughts JOIN users_thoughts ON thoughts.id_thought = users_thoughts.thoughts_id_thought JOIN users ON users_thoughts.users_id_user = users.id_user WHERE thoughts.id_thought = %(thought_id)s"
    data = {'thought_id': thought_id}
    liked_users = mysql.query_db(query, data)
    
    tmp = []
    if liked_users:
        for i, d in enumerate(liked_users):
            if d['id_user'] == all_thoughts[0]['id_user']:
                tmp = liked_users.pop(i)
                print(tmp)
                break
        liked_users.append(tmp)
    print(liked_users)
    
    if all_thoughts:
        thought_data = all_thoughts[0]
        if thought_data['id_thought'] in liked_thoughts:
            thought_data['already_liked'] = True
        else:
            thought_data['already_liked'] = False
    else:
        return redirect("/thoughts")
        
    return render_template("thought_detail.html", thought_data = thought_data, liked_users = liked_users)

@app.route("/thoughts/add_like/<thought_id>")
def on_like(thought_id):
    mysql = connectToMySQL("thought_dashboard")
    query = "INSERT INTO users_thoughts (users_id_user, thoughts_id_thought) VALUES (%(user_id)s, %(thought_id)s)"
    data = {
        'user_id': session['user_id'],
        'thought_id': thought_id
    }
    mysql.query_db(query, data)
    return redirect(f"/thoughts/details/{thought_id}")

@app.route("/thoughts/unlike/<thought_id>")
def on_unlike(thought_id):
    mysql = connectToMySQL("thought_dashboard")
    query = "DELETE FROM users_thoughts WHERE users_thoughts.users_id_user = %(user_id)s AND users_thoughts.thoughts_id_thought = %(thought_id)s"
    data = {
        'user_id': session['user_id'],
        'thought_id': thought_id
    }
    mysql.query_db(query, data)
    return redirect(f"/thoughts/details/{thought_id}")
    
@app.route("/thoughts/delete/<thought_id>")    
def on_delete(thought_id):
    mysql = connectToMySQL("thought_dashboard")
    query = "DELETE FROM users_thoughts WHERE thoughts.id_thought = %(thought_id)s"
    data = {'thought_id': thought_id}
    mysql.query_db(query, data)
    
    mysql = connectToMySQL("thought_dashboard")
    query = "DELETE FROM thoughts WHERE thoughts.id_thought = %(thought_id)s"
    mysql.query_db(query, data)
    
    return redirect("/thoughts")
    
if __name__ == "__main__":
    app.run(debug=True)