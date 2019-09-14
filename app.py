from flask import Flask, render_template, request, jsonify, redirect, abort, url_for, session, make_response, copy_current_request_context
from flask_mysqldb import MySQL,MySQLdb
from werkzeug.utils import secure_filename
import os
from time import sleep
import threading

import requests


app = Flask(__name__)
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= 'MyNewPass'
app.config['MYSQL_DB']= 'Test'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'
app.config['FILE_UPLOADS'] = '/home/hassan/Desktop/Assesment/'

mysql= MySQL(app)


key = "AIzaSyDR_5xy6JWiVF3K_bppQMCxljTnrNjs4_k"

app.secret_key = "One for all"

search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
details_url = "https://maps.googleapis.com/maps/api/place/details/json"




@app.route('/', methods=['GET'])
def home():
    if session.get('logged')== True:
        session['browser']=request.user_agent.browser
        name = request.cookies.get('name')
        email = request.cookies.get('email')
        return render_template("home.html", name = name, email= email)
    return render_template("login.html")


@app.route('/success', methods=['POST', 'GET'])
def success():
    app.secret_key= "One for all"
    session['name'] =  request.cookies.get('name')
    session['email'] = request.cookies.get('email')
    
    return render_template('success.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM accounts WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if  user["password"].encode('UTF-8') == password:

                resp = make_response(render_template('success.html'))
                resp.set_cookie('name', user['username'])
                resp.set_cookie('email',user['email'])
                session['logged'] = True
                
                return resp
            
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("login.html")


@app.route('/upload', methods=['POST','GET'])
def upload():
    @copy_current_request_context
    def save_file(closeAfterWrite):
        f = request.files['file']
        loc = app.config['FILE_UPLOADS'] + f.filename
        f.save(loc)
        closeAfterWrite()
    def passExit():
        pass
    if request.method == 'POST':
        f= request.files['file']
        normalExit = f.stream.close
        f.stream.close = passExit
        t = threading.Thread(target=save_file,args=(normalExit,))
        t.start()
        return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route("/places/<string:query>")
def results(query):
	search_payload = {"key":key, "input":query, "inputtype":'textquery'}
	search_req = requests.get(search_url, params=search_payload)
	search_json = search_req.json()

	place_id = search_json["candidates"][0]["place_id"]

	details_payload = {"key":key, "placeid":place_id}
	details_resp = requests.get(details_url, params=details_payload)
	details_json = details_resp.json()

	url = details_json["result"]["url"]
	return jsonify({'result' : url})


@app.route("/api/<int:number>", methods=['GET'])
def api(number):
    total = 0
    while number >= 10:
        total += number % 10
        number = number//10
    total += number
    return str(total)
if __name__ =='__main__':
    app.secret_key = "One for all"
    app.run(debug=True)