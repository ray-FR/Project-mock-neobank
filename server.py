import flask
import markupsafe
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import timedelta

app=flask.Flask("banking")
bcrypt = Bcrypt(app)


dashboardJs = """
const disconnectButton = document.getElementById("log-out");

disconnectButton.addEventListener("click", () => {
    location.reload();
    document.location.href = '/';
    document.cookie = "userAuth=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
});
"""

@app.route("/")
def main():
    mainHtml = ""
    resp = None
    isIdentified = flask.request.cookies.get('userAuth')
    if not isIdentified:
        mainHtml = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Main-page</title>
    <link rel="stylesheet" href="style/style.css">
    
</head>
<body>
    <h1>Welcome</h1>
    <button onclick="location.href='login'" id="login">Login</button>
    <button onclick="location.href='sign-up'" id="sign-up">Sign-Up</button>
</body>
</html>
"""

    else:
        return flask.redirect(flask.url_for("dashboard"))

    resp = flask.make_response(mainHtml)
    return resp

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    returnMess = ""
    name = ""
    accInfo = ""
    userID = flask.request.cookies.get('userAuth')
    with sqlite3.connect("tmp.sqlite3") as db:
        try:
            cur = db.cursor()
            cur.execute("SELECT firstName, accountID FROM userBase where userID == (?);", (userID,))
            res = cur.fetchall()
            name = res[0][0]
            cur.execute("SELECT money FROM bankAccounts where accountID == (?);", (res[0][1],))
            res = cur.fetchall()
            accInfo = f"<h2> Vous avez {res[0][0]} euros.</h2>"



        except sqlite3.Error as e:
            returnMess = "Error! " + e

    

    dashboardHtml = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Main-page</title>
    <link rel="stylesheet" href="style/style.css">
    <script src="scripts/dashboard.js" defer></script>

</head>
<body>
    <button id="log-out">Log Out</button>
    <h1>Welcome {name}!</h1>
    {accInfo}
    <h2>{returnMess}</h2>

</body>
</html>
"""

    resp = flask.make_response(dashboardHtml)
    return resp





@app.route("/login", methods=["GET", "POST"])
def login():
    returnMess = ""

    email = flask.request.form.get('email')
    password = flask.request.form.get('pass')

    if email and password:
        with sqlite3.connect("tmp.sqlite3") as db:
            try:
                cur = db.cursor()
                cur.execute("SELECT password FROM userBase WHERE email == (?);", (email,))
                res = cur.fetchall()
                if (res == []):
                    returnMess = "Error! Account does not exist"
                else:
                    
                    hashed_password = res[0][0]
                    
                    if (bcrypt.check_password_hash(hashed_password, password)):
                        
                        returnMess = "Success!"
                    else:
                        returnMess = "Error! Wrong password"

            except sqlite3.Error as e:
                returnMess = "Error!"

    loginHtml = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login-bank</title>
</head>
<body>
    <h1>Login!</h1>
    <form method="POST">
        <input required type="email" name="email" placeholder="Email">
        <input required type="password" name="pass" placeholder="Mot de passe">
        <input type="submit" value="Login" >
    </form>
    <h2>{returnMess}</h2>
    <button onclick="location.href='/'" id="main">Back</button>

</body>
</html>
"""
    resp = flask.make_response(loginHtml)
    if userAuth:
        resp.set_cookie("userAuth", str(userAuth), max_age=timedelta(minutes=30), path="/")

    return resp

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    returnMess = ""
    
    email = flask.request.form.get('email')
    firstName = flask.request.form.get('firstName')
    lastName = flask.request.form.get('lastName')
    password = flask.request.form.get('pass')
    
    if email and firstName and  lastName and password:
        with sqlite3.connect("tmp.sqlite3") as db:
            try: 
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cur = db.cursor()
                data = {'email': email, 'firstN': firstName, 'lastN': lastName, 'password': hashed_password}
                cur.execute(f"INSERT INTO userBase (email, firstName, lastName, password) VALUES (:email, :firstN, :lastN, :password);", data)
                db.commit()
                returnMess = "Success!"
            except sqlite3.Error as e:
                
                returnMess = "Error!"
    

    signUpHtml = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign-Up-Bank</title>
</head>
<body>
    <h1>Sign Up!</h1>
    <form method="POST">
        <input required type="email" name="email" placeholder="Email">
        <input required type="text" name="firstName" placeholder="Nom">
        <input required type="text" name="lastName" placeholder="Prénom">
        <input required type="password" name="pass" placeholder="mot de passe">
        <input type="submit" value="Sign up" >
    </form>
    <h2>{returnMess}</h2>
    <button onclick="location.href='/'" id="main">Back</button>

</body>
</html>
"""

    resp = flask.make_response(signUpHtml)
    if userAuth:
        resp.set_cookie("userAuth", str(userAuth), max_age=timedelta(minutes=30), path="/")
    return resp

@app.route("/style/style.css")
def ff():
    resp = flask.make_response("""""")
    resp.headers["content-type"] = "text/css"
    return resp

# @app.route("/scripts/main.js")
# def scriptMain():
#     resp = flask.make_response(scriptSignUp)
#     resp.headers["content-type"] = "text/javascript"
#     return resp

app.run(port=1234,host="127.0.0.1") 