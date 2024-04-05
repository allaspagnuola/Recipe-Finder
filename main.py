from flask import Flask, jsonify, request, render_template, flash, Blueprint, url_for
from bson import ObjectId


from db import db

import json


# Create Flask app to connect front-end, back-end, and database
app = Flask(__name__)
bp = Blueprint('auth', __name__, url_prefix='/auth')



# Part 1: Test Flask
@app.route("/")
def flask_mongodb_atlas():
    return "Hello World"


# Part 2: Test API - Insert hard-coded data to test connection to database
@app.route("/test")
def test():
    all = db.collection.find()

    for doc in all:
        db.collection.delete_one({"_id": doc["_id"]})      

    db.collection.insert_one({"name": "MUMS"})

    f=open("test.json")
    data=json.load(f)
    for i in data:
        db.collection.insert_one(i)
    return "No CISSA anymore BINGO!"

# Part 3: HTTP Get method - API to return all recipes currently stored in the database
@app.route("/get-all")
def get_all():
    # Collect all the data from the database
    all = db.collection.find()


    # For each document, convert _id from type ObjectId to string so it can be JSON serializable
    data = []
    for doc in all:
        doc["_id"] = str(doc["_id"])
        try: 
            data.append(doc["ingredients"])
        except:
            pass


    # Return as JSON type
    return jsonify(data)

# Part 4: HTTP Post method - API to insert one recipe into the database
@app.route("/insert-one", methods=["POST"])
def insert_one():
    input_json = request.get_json()


    # this serves as a simple validation that checks if all the fields we need
    # are in the request, and that we're not entering erroneous entries either
    dict_to_return = {
        "name": input_json["name"],
        "ingredients": input_json["ingredients"],
        "method": input_json["method"],
    }
    db.collection.insert_one(dict_to_return)
    # the above call mutates dict_to_return to include the _id of the new entry


    # in the database, Data of type ObjectID can't be parsed by the browser
    # so we convert it to a string first
    dict_to_return["_id"] = str(dict_to_return["_id"])
    return dict_to_return

# Part 5: HTTP Delete method - API to remove one recipe from the database by ID
# e.g. body might be {"_id": "63089f6c32adbaebfa6e8d06"}
@app.route("/remove-one", methods=["DELETE"])
def remove_one():
    input_json = request.get_json()


    # Convert string to MongoDB ObjectId type
    dict_to_query = {"_id": ObjectId(input_json["_id"])}


    # Remove from database
    db.collection.delete_one(dict_to_query)


    return f"successfully deleted {dict_to_query['_id']}"
@app.route('/insert', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form["name"]
        ingredients = request.form["ingredients"]
        method = request.form["method"]
        error = None

        if not name:
            error = 'Name is required.'
        elif not ingredients:
            error = 'Ingredient is required.'
        elif not method:
            error = 'Method is required.'

        
        # REMEMBER to add 
        if not error:
            dict_to_return = {
                "name": name,
                "ingredients": ingredients,
                "method": method,
            }
            db.collection.insert_one(dict_to_return)

        flash(error)

    return render_template("insert.html")

'''
Some more stuff
Will clean this up later
'''

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        
        # REMEMBER to add 
        if not error:
            dict_to_return = {
                "username": username,
                "password": password,
            }
            db.collection.insert_one(dict_to_return)

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.Collection_name.find({"username" : username})


        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')
'''
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view

'''


@app.route('/home', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        input_json = request.json
        dict_to_return = {
            "ingredients": input_json["ingredients"],
        }
        print(dict_to_return)
        return jsonify(dict_to_return)
        
    return render_template("home.html")


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.register_blueprint(bp)
    app.run(port=8000, debug=True)
    url_for('static', filename='style.css')
    url_for('static', filename='insert.css')
    url_for('static', filename='home.css')
