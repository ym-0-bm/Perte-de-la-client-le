CREATE TABLE Client (
    idclient INT PRIMARY KEY AUTO_INCREMENT,
    genre VARCHAR(10),
    personneagée BOOLEAN,
    Partenaire VARCHAR(10),
    Dépendants VARCHAR(10)
);

CREATE TABLE Abonnement (
    idabonnement INT PRIMARY KEY AUTO_INCREMENT,
    idclient INT,
    ancienneté INT,
    Contrat VARCHAR(50),
    FacturationSansPapier VARCHAR(10),
    MéthodeDePaiement VARCHAR(50),
    ChargesMensuelles FLOAT,
    ChargesTotales FLOAT,
    FOREIGN KEY (idclient) REFERENCES Client(idclient)
);

CREATE TABLE Services (
    idservices INT PRIMARY KEY AUTO_INCREMENT,
    idclient INT,
    ServiceTéléphonique VARCHAR(10),
    LignesMultiples VARCHAR(10),
    ServiceInternet VARCHAR(50),
    SécuritéEnLigne VARCHAR(50),
    SauvegardeEnLigne VARCHAR(50),
    ProtectionDesAppareils VARCHAR(50),
    SupportTechnique VARCHAR(50),
    TVEnStreaming VARCHAR(50),
    FilmsEnStreaming VARCHAR(50),
    FOREIGN KEY (idclient) REFERENCES Client(idclient)
);

CREATE TABLE statut (
    idstatut INT PRIMARY KEY AUTO_INCREMENT,
    idclient INT,
    statut VARCHAR(10),
    FOREIGN KEY (idclient) REFERENCES Client(idclient)
);
