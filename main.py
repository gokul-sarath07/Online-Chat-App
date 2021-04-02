from flask import Flask, render_template, url_for, redirect, request


NAME_KEY = 'name'

app = Flask(__name__)
app.secret_key = 'secret_pass_code'

@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
