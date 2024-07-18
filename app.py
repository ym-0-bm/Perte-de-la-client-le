from flask import Flask, render_template
import pymysql.cursors

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'job_scraper'
app.config['SECRET_KEY'] = 'secret key'


# Initialisation de la connexion MySQL
def get_db_connection():
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
