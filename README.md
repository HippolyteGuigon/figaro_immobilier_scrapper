# le_figaro_immobilier_scrapper
Scrapper du site Internet Le figaro immobilier (https://immobilier.lefigaro.fr) afin d'en tirer plus rapidement des informations

## Lancer l'application 

- Utiliser la commance ```streamlit run app/app.py``` pour lancer l'application streamlit. 

## Installer les dépendances nécessaires

- Pour installer les librairies nécessaires, lancer ```pip install -r requirements.txt```

## Description du projet 

Le but de ce projet est de construire une application Streamlit qui sera constituée de 3 pages différentes: 

•	Sur une première page , on aura un filtreur avec le type de bien (maison/appartement), le loyer maximal par mois, le nombre de pièces et de chambres 
Si on demande une nouvelle ville et qu’il n’y a pas suffisamment d’exemples, alors le scrappeur devra se mettre en route automatiquement et aller lui-même chercher les données correspondantes. Un message et une barre de recherche sera alors montré à l’utilisateur


•	Sur une deuxième page, on veut des analyses macro avec une carte de ville (l’utilisateur peut sélectionner la ville) montrant le prix moyen par quartier, le nombre de pièces, le cout thermique etc 


•	Sur une troisième page, on veut une prédiction, par quartier du nombre d’appartements qui seront mis en location ainsi que le prix moyen pour lequel ils le seront 
