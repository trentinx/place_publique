from flask import (Flask, render_template, 
                   request, jsonify, 
                   session, send_file)

""" Initialize Flask app and configure secret key for sessions. """
app = Flask(__name__)
app.secret_key = "your_secret_key_here"


""" Flask routes """
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=8080, host='0.0.0.0')
