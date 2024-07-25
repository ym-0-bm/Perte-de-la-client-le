from flask import Flask
import pandas as pd
import pymysql.cursors

# Charger le CSV
df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')

# Connexion à la base de données
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'perte de clientele'
app.config['SECRET_KEY'] = 'secret key'


# Initialisation de la connexion MySQL
def get_db_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


conn = get_db_connection()
cursor = conn.cursor()

# Ajouter une colonne 'idclient' avec une numérotation à partir de 1
df['idclient'] = range(1, len(df) + 1)
# df.to_csv('chemin_vers_votre_nouveau_fichier_csv.csv', index=False)
# print(list(df.head(2)))

# Insérer les données dans la table Client
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Client (genre, personneagée, Partenaire, Dépendants)
        VALUES (%s, %s, %s, %s)
    """, (row['gender'], row['SeniorCitizen'], row['Partner'], row['Dependents']))

# Insérer les données dans la table Abonnement
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Abonnement (idclient, ancienneté, Contrat, FacturationSansPapier, MéthodeDePaiement,
        ChargesMensuelles, ChargesTotales)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (row['idclient'], row['tenure'], row['Contract'], row['PaperlessBilling'], row['PaymentMethod'],
          row['MonthlyCharges'], row['TotalCharges']))

# # Insérer les données dans la table Services
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Services (idclient, ServiceTéléphonique, LignesMultiples, ServiceInternet,
        SécuritéEnLigne, SauvegardeEnLigne, ProtectionDesAppareils, SupportTechnique, TVEnStreaming, FilmsEnStreaming)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (row['idclient'], row['PhoneService'], row['MultipleLines'], row['InternetService'], row['OnlineSecurity'],
          row['OnlineBackup'], row['DeviceProtection'], row['TechSupport'], row['StreamingTV'], row['StreamingMovies']))

# # Insérer les données dans la table Statut
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Statut (idclient, statut)
        VALUES (%s, %s)
    """, (row['idclient'], row['Churn']))

conn.commit()
cursor.close()
conn.close()
