import flask
from flask_bcrypt import Bcrypt
from flask_session import Session
import sqlite3

app=flask.Flask("banking")
bcrypt = Bcrypt(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def main():
    isIdentified = flask.session.get('userAuth')
    if isIdentified:
        return flask.redirect(flask.url_for("dashboard"))      

    

    
    return flask.render_template("index.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    userID = flask.session.get('userAuth')
    logOut = flask.request.form.get('log-out')
    if logOut:
        flask.session['userAuth'] = None
        return flask.redirect(flask.url_for("main"))

    if not userID:
        return flask.redirect(flask.url_for("login"))
    name = ""
    accInfo = ""
    sAccInfo = ""
    addAccM = flask.request.form.get('amount-add')
    sendAccM = flask.request.form.get('amount-send')
    withdrawAccM = flask.request.form.get('amount-withdraw')
    createSharedAcc = flask.request.form.get('createNameSharedAccount')
    joinSharedAcc = flask.request.form.get('joinNameSharedAccount')
    addSAccM = flask.request.form.get('amount-Sadd')
    withdrawSAccM = flask.request.form.get('amount-Swithdraw')

        
    
    with sqlite3.connect("tmp.sqlite3") as db:
        try:
            cur = db.cursor()
            cur.execute("SELECT firstName, accountID, sharedAccountID FROM userBase where userID == (?);", (userID,))
            res = cur.fetchall()
            name = res[0][0]
            accID = res[0][1]
            
            cur.execute("SELECT money, isBlocked FROM bankAccounts where accountID == (?);", (accID,))
            bankRes = cur.fetchall()
            money = bankRes[0][0]
            accountStatus = bankRes[0][1]
            if accountStatus == 1:
                accInfo = f"<div id = 'dashboard'><div id = 'blocked-acc-info'><h4> Your account has been blocked.</h4>\n<p>Please contact your bank administrator.</p>\n</div>"

            if accountStatus == 0:
                accInfo = f"<div id = 'dashboard'><div id='acc-info'><h4> You have {money} euros on your personal account.</h4>\n<div class='action-btn-flex'><button class='money-button' value='add-acc'>Add money</button>\n<button class='money-button' value='send-acc'>Send money</button>\n<button class='money-button' value='withdraw-acc'>Withdraw money</button>\n</div></div>"
            if res[0][2] == None:
                sAccInfo = "<div id='no-sharedAcc-info'><h4> You do not have a shared bank account.</h4>\n<div class='action-btn-flex'><button id='create-shared-account'>Create shared account</button>\n<button id='join-shared-account'>Join shared account</button>\n</div>\n</div>\n</div>"
                if createSharedAcc:
                    passShrAcc = flask.request.form.get('passwordSharedAccount')
                    hashed_password = bcrypt.generate_password_hash(passShrAcc).decode('utf-8')
                    cur.execute("INSERT INTO bankAccounts (accountType, name, password) VALUES (1, (?), (?));", (createSharedAcc,hashed_password))
                    cur.execute("SELECT last_insert_rowid();")
                    sAccID = cur.fetchone()[0]
                    cur.execute("UPDATE userBase SET sharedAccountID = (?) WHERE userID == (?);", (sAccID,userID))
                    db.commit()
                    flask.flash(f"Created shared account successfully!", 'success')
                    return flask.redirect(flask.url_for('dashboard'))
                if joinSharedAcc:
                    cur.execute("SELECT accountID, password FROM bankAccounts where name == (?);", (joinSharedAcc,))
                    tmp = cur.fetchall()
                    if (tmp == []):
                        flask.flash(f"Error! Shared account doesn't exist", 'error')
                        return flask.redirect(flask.url_for('dashboard'))

                    passShrAcc = flask.request.form.get('passwordSharedAccount')
                    if (bcrypt.check_password_hash(tmp[0][1], passShrAcc)):
                        cur.execute("UPDATE userBase SET sharedAccountID = (?) WHERE userID == (?);", (tmp[0][0],userID))
                        flask.flash(f"Joined shared account!", 'success')
                        return flask.redirect(flask.url_for('dashboard'))
                    flask.flash(f"Error! wrong password", 'error')
                    return flask.redirect(flask.url_for('dashboard'))
                
                
            else:
                sAccID = res[0][2]
                cur.execute("SELECT money, isBlocked FROM bankAccounts where accountID == (?);", (sAccID,))
                sharedBankRes = cur.fetchall()

                sharedMoney = sharedBankRes[0][0]
                
                if sharedBankRes[0][1] == 1:
                    sAccInfo = f"<div id = 'blocked-acc-info'><h4> Your shared account has been blocked.</h4>\n<p>Please contact your bank administrator.</p>\n</div>\n</div>"

                if sharedBankRes[0][1] == 0:
                    sAccInfo = f"<div id='Sacc-info'><h4> You have {sharedMoney} euros on your shared account.</h4>\n"
                    if accountStatus == 1:
                        sAccInfo += "<div class='action-btn-flex'><button class='money-button' value='add-Sacc' disabled >Add money</button>\n<button class='money-button' value='withdraw-Sacc' disabled>Withdraw money</button>\n</div></div></div>"
                    else:
                        sAccInfo += "<div class='action-btn-flex'><button class='money-button' value='add-Sacc'>Add money</button>\n<button class='money-button' value='withdraw-Sacc'>Withdraw money</button>\n</div></div></div>"

                if addSAccM:
                    cur.execute("UPDATE bankAccounts SET money=(?)+(?) WHERE accountID == (?);", (sharedMoney, addSAccM, sAccID))
                    cur.execute("UPDATE bankAccounts SET money=(?)-(?) WHERE accountID == (?);", (money, addSAccM, accID))
                    db.commit()
                    flask.flash(f"Added {addSAccM}€ to the shared account successfully!", 'success')
                    return flask.redirect(flask.url_for('dashboard'))
                if withdrawSAccM:
                    cur.execute("UPDATE bankAccounts SET money=(?)-(?) WHERE accountID == (?);", (sharedMoney, withdrawSAccM, sAccID))
                    cur.execute("UPDATE bankAccounts SET money=(?)+(?) WHERE accountID == (?);", (money, withdrawSAccM, accID))
                    db.commit()
                    flask.flash(f"Withdrawn {withdrawSAccM}€ from the shared account successfully!", 'success')
                    return flask.redirect(flask.url_for('dashboard'))


                



            if addAccM:
                cur.execute("UPDATE bankAccounts SET money=(?)+(?) WHERE accountID == (?);", (money, addAccM, accID))
                db.commit()
                flask.flash(f"Added {addAccM}€ to your personal account successfully!", 'success')
                return flask.redirect(flask.url_for('dashboard'))
            
            if sendAccM:
                email = flask.request.form.get('send-email')
                cur.execute("SELECT userBase.accountID, money, firstName FROM userBase INNER JOIN bankAccounts ON userBase.accountID = bankAccounts.accountID where email == (?);", (email,))
                res = cur.fetchall()
                if res == []:
                    flask.flash(f"Error! User doesn't exist!", 'error')
                    return flask.redirect(flask.url_for('dashboard'))
                else:
                    moneyReceiver = res[0][1]
                    cur.execute("UPDATE bankAccounts SET money=(?)+(?) WHERE accountID == (?);", (moneyReceiver, sendAccM, res[0][0]))
                    
                    cur.execute("UPDATE bankAccounts SET money=(?)-(?) WHERE accountID == (?);", (money, sendAccM, flask.session.get('userAuth')))

                    db.commit()
                    flask.flash(f"Sent {sendAccM}€ to {res[0][2]} successfully!", 'error')
                    return flask.redirect(flask.url_for("dashboard"))
            
            if withdrawAccM:
                cur.execute("UPDATE bankAccounts SET money=(?)-(?) WHERE accountID == (?);", (money, withdrawAccM, accID))
                db.commit()
                flask.flash(f"Withdrawn {withdrawAccM}€ successfully!", 'success')
                return flask.redirect(flask.url_for('dashboard'))
            
            return flask.render_template("dashboard.html", name = name, accInfo = accInfo, sAccInfo = sAccInfo)
            

            


        except sqlite3.Error as e:
            returnMess = "Error! " + str(e)

    

    






@app.route("/login", methods=["GET", "POST"])
def login():
    returnMess = ""
    userAuth = None
    email = flask.request.form.get('email')
    password = flask.request.form.get('pass')

    if email and password:
        with sqlite3.connect("tmp.sqlite3") as db:
            try:
                cur = db.cursor()
                cur.execute("SELECT password, userID FROM userBase WHERE email == (?);", (email,))
                res = cur.fetchall()
                if (res == []):
                    flask.flash("Error! Account doesn't exist", 'error')
                    return flask.redirect(flask.url_for('login'))
                else:
                    
                    hashed_password = res[0][0]
                    
                    if (bcrypt.check_password_hash(hashed_password, password)):
                        userAuth = res[0][1]
                        flask.session["userAuth"] = str(userAuth)
                        flask.flash("Successfully login!", 'success')
                        return flask.redirect(flask.url_for('dashboard'))
                    else:
                        flask.flash("Error! Wrong password", 'error')
                        return flask.redirect(flask.url_for('login'))

            except sqlite3.Error as e:
                flask.flash("Error!" + str(e), 'error')
                return flask.redirect(flask.url_for('login'))



    
    
    return flask.render_template("login.html")

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    returnMess = ""
    userAuth = None
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
                cur.execute("INSERT INTO userBase (email, firstName, lastName, password, userType) VALUES (:email, :firstN, :lastN, :password, 0);", data)
                cur.execute("SELECT last_insert_rowid();")
                res = cur.fetchall()
                userAuth = res[0][0]
                cur.execute("INSERT INTO bankAccounts (accountType) VALUES (0);")
                cur.execute("SELECT last_insert_rowid();")
                res = cur.fetchall()
                cur.execute("UPDATE userBase SET accountID = (?) WHERE email==(?);", (res[0][0], email))
                db.commit()
                flask.session["userAuth"] = str(userAuth)
                flask.flash("Successfully signed up!", 'success')
                return flask.redirect(flask.url_for('dashboard'))
            except sqlite3.Error as e:
                
                
                flask.flash("Error! Account already exists!", 'error')
                return flask.redirect(flask.url_for('signup'))
    

    

    
    return flask.render_template("signup.html")



app.run(port=1234,host="127.0.0.1") 