from flask import Flask, render_template, request
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import joblib
import pymysql.cursors
from encoder_columns import encoder_columns

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prediction_history'
app.config['SECRET_KEY'] = 'secret key'

# Charger le model
model = joblib.load('Prediction/model.joblib')
column_names = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
    'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
    'StreamingTV', 'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod',
    'MonthlyCharges', 'TotalCharges', 'tenure_class'
]


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
            payment_method, monthly_charges, total_charges, tenure_class
        ]]
        # print(input_data)

        # Convertir en DataFrame en utilisant les colonnes d'origine
        input_df = pd.DataFrame(input_data, columns=column_names)
        # print(input_df)

        # Encoder les données d'entrée
        encoded_input_data = pd.DataFrame(
            OneHotEncoder(
                handle_unknown='ignore',
                sparse_output=False).fit_transform(input_df),
            columns=OneHotEncoder().fit(input_df).get_feature_names_out(input_df.columns)
        )

        # print(encoded_input_data)

        # Créer un DataFrame avec des colonnes manquantes et des valeurs par défaut (0)
        missing_columns = [col for col in encoder_columns if col not in encoded_input_data.columns.to_list()]
        missing_data = pd.DataFrame(0.0, index=encoded_input_data.index, columns=missing_columns)

        # Ajouter les colonnes manquantes au DataFrame existant
        encoded_input_data = pd.concat([encoded_input_data, missing_data], axis=1)

        # Réorganiser les colonnes pour s'assurer qu'elles sont dans le même ordre que celles du modèle
        encoded_input_df = encoded_input_data[encoder_columns]
        print(encoded_input_df)

        # Faire la prédiction
        prediction = model.predict(encoded_input_df)
        proba = model.predict_proba(encoded_input_df)
        confidence = max(proba[0]) * 100

        # Afficher le résultat de la prédiction
        if prediction == 1:
            result = "Client susceptible de se désabonner."
            statut = "Yes"
        else:
            result = "Client probablement fidèle."
            statut = "No"

        # Ajout dans la base de donnée
        cursor = conn.cursor()

        # Insérer dans Client
        cursor.execute("INSERT INTO Client (genre, personneagée, Partenaire, Dépendants) VALUES (%s, %s, %s, %s)",
                       (gender, senior_citizen, partner, dependents))
        idclient = cursor.lastrowid  # Récupère idclient généré

        # Insérer dans Abonnement
        cursor.execute(
            """
            INSERT INTO Abonnement (
            idclient, ancienneté, Contrat, FacturationSansPapier, MéthodeDePaiement, ChargesMensuelles, ChargesTotales
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (idclient, tenure, contract, paperless_billing, payment_method, monthly_charges, total_charges))

        # Insérer dans Services
        cursor.execute(
            """INSERT INTO Services (
            idclient, ServiceTéléphonique, LignesMultiples, ServiceInternet, SécuritéEnLigne, SauvegardeEnLigne, 
            ProtectionDesAppareils, SupportTechnique, TVEnStreaming, FilmsEnStreaming
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (idclient, phone_service, multiple_lines, internet_service, online_security, online_backup,
             device_protection, tech_support, streaming_tv, streaming_movies))

        # Insérer dans statut
        cursor.execute("INSERT INTO statut (idclient, statut, score) VALUES (%s, %s, %s)",
                       (idclient, statut, confidence))

        conn.commit()
        conn.close()
        return render_template("output.html", prediction_result=result, proba=confidence)

        # Afficher le formulaire par défaut
    return render_template("index.html")


@app.route("/output", methods=["GET", "POST"])
def output():
    return render_template("output.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Récupérer les données depuis la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM Client
    JOIN Abonnement ON Client.idclient = Abonnement.idclient
    JOIN Services ON Client.idclient = Services.idclient
    JOIN statut ON Client.idclient = statut.idclient
    ORDER BY Client.idclient DESC LIMIT 5
    """)
    predictions_recent = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) AS nombre_total_de_prédictions FROM statut')
    nombre_total_de_predictions = cursor.fetchone()
    nombre_total_de_predictions = nombre_total_de_predictions["nombre_total_de_prédictions"]
    cursor.execute("SELECT COUNT(*) AS clients_fidèles FROM statut WHERE statut = 'No'")
    clients_fideles = cursor.fetchone()
    clients_fideles = clients_fideles["clients_fidèles"]
    cursor.execute("SELECT COUNT(*) AS clients_perdus FROM statut WHERE statut = 'Yes'")
    clients_perdus = cursor.fetchone()
    clients_perdus = clients_perdus["clients_perdus"]
    print(nombre_total_de_predictions, clients_fideles, clients_perdus)
    conn.close()

    return render_template("admin/index.html", predictions_recent=predictions_recent,
                           nombre_total_de_predictions=nombre_total_de_predictions,
                           clients_fideles=clients_fideles,
                           clients_perdus=clients_perdus
                           )


@app.route("/admin/liste", methods=["GET", "POST"])
def liste():
    # Récupérer les données depuis la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
            SELECT * FROM Client
            JOIN Abonnement ON Client.idclient = Abonnement.idclient
            JOIN Services ON Client.idclient = Services.idclient
            JOIN statut ON Client.idclient = statut.idclient
            ORDER BY Client.idclient DESC LIMIT 5
        """
    )
    predictions = cursor.fetchall()

    conn.close()

    return render_template("admin/liste.html", predictions=predictions)


if __name__ == '__main__':
    app.run(debug=True)
