from flask import Flask, render_template, request, url_for, redirect
import joblib
import pymysql.cursors

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prediction_history'
app.config['SECRET_KEY'] = 'secret key'

model = joblib.load('Prediction/model_rf.joblib')


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


# Définir la fonction pour obtenir la classe d'ancienneté
def get_tenure_class(tenure):
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80]
    labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80']

    for i in range(len(bins) - 1):
        if bins[i] <= tenure < bins[i + 1]:
            return labels[i]
    return None


@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db_connection()
    if request.method == 'POST':
        # Récupérer les données du formulaire
        senior_citizen = int(request.form['seniorCitizen'])
        monthly_charges = float(request.form['monthlyCharges'])
        total_charges = float(request.form['totalCharges'])
        gender = request.form['gender']
        partner = request.form['partner']
        dependents = request.form['dependents']
        phone_service = request.form['phoneService']
        multiple_lines = request.form['multipleLines']
        internet_service = request.form['internetService']
        online_security = request.form['onlineSecurity']
        online_backup = request.form['onlineBackup']
        device_protection = request.form['deviceProtection']
        tech_support = request.form['techSupport']
        streaming_tv = request.form['streamingTV']
        streaming_movies = request.form['streamingMovies']
        contract = request.form['contract']
        paperless_billing = request.form['paperlessBilling']
        payment_method = request.form['paymentMethod']
        tenure = int(request.form['tenure'])

        # Déterminer la classe d'ancienneté
        tenure_class = get_tenure_class(tenure)

        # Préparez les données pour le modèle
        input_data = [[
            gender, senior_citizen, partner, dependents, phone_service, multiple_lines,
            internet_service, online_security, online_backup, device_protection, tech_support,
            streaming_tv, streaming_movies, contract, paperless_billing,
            payment_method, monthly_charges, total_charges, tenure, tenure_class
        ]]
        print(input_data)

        # Préparez les données pour le modèle
        input_data = [[
            gender, senior_citizen, partner, dependents, phone_service, multiple_lines,
            internet_service, online_security, online_backup, device_protection, tech_support,
            streaming_tv, streaming_movies, contract, paperless_billing,
            payment_method, monthly_charges, total_charges, tenure_class
        ]]
        print(input_data)

        # Faire la prédiction
        prediction = model.predict(input_data)
        proba = model.predict_proba(input_data)
        confidence = max(proba[0]) * 100

        # Afficher le résultat de la prédiction
        if prediction == 1:
            result = "Client susceptible de se désabonner."
        else:
            result = "Client probablement fidèle."

        # Ajout dans la base de donnée
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions
            (SeniorCitizen, MonthlyCharges, TotalCharges, gender, Partner, Dependents,
             PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup,
             DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract,
             PaperlessBilling, PaymentMethod, tenure, tenure_class, Churn, Confidence)
            VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (senior_citizen, monthly_charges, total_charges, gender, partner, dependents,
                  phone_service, multiple_lines, internet_service, online_security, online_backup,
                  device_protection, tech_support, streaming_tv, streaming_movies, contract,
                  paperless_billing, payment_method, tenure, tenure_class, prediction, confidence)
                )
        conn.commit()
        conn.close()
        return render_template("output.html", prediction_result=result, proba=confidence)

        # Afficher le formulaire par défaut
    return render_template("index.html")


@app.route("/output", methods=["GET", "POST"])
def output():
    return render_template("output.html")


if __name__ == '__main__':
    app.run(debug=True)
