# Utiliser une image officielle Python 3.10 en version slim
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires pour installer les dépendances
COPY requirements.txt .

# Installer les dépendances avec pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu du projet dans le conteneur
COPY . .

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Définir la commande par défaut pour exécuter l'application
CMD ["streamlit", "run", "features/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
