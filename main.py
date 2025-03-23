from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('login.html')

@app.route("/login", methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        if checkpass(request.form['email'],request.form['password']):
            return loguserin(request.form['email'])
        else:
            error = 'invalida'
    return render_template('login.html', error=error)

    
def checkpass(email,password):
    return True

def loguserin(email):
    return render_template('home.html')

app.run(host='0.0.0.0',port='80' ,debug=True)