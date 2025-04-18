import requests
from bs4 import BeautifulSoup
import time
import json
import os

# === CONFIGURATION ===

URL_SITE = "https://jobs.extracadabra.com/paris"
INTERVALLE_VERIF_SECONDES = 2  # Vérifie toutes les 60 secondes

TOKEN_BOT = os.getenv("TOKEN_BOT")
ID_CHAT_TELEGRAM = os.getenv("ID_CHAT_TELEGRAM")

FICHIER_OFFRES_VUES = "offres_vues.json"  # Pour mémoriser les missions déjà envoyées

# === FONCTION : Envoyer un message via Telegram ===
def envoyer_message_telegram(texte):
    url_api = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    donnees = {
        "chat_id": ID_CHAT_TELEGRAM,
        "text": texte,
        "parse_mode": "HTML"
    }
    requests.post(url_api, data=donnees)

# === FONCTION : Charger les missions déjà vues (depuis un fichier JSON) ===
def charger_offres_vues():
    try:
        with open(FICHIER_OFFRES_VUES, "r") as fichier:
            return json.load(fichier)
    except:
        return []

# === FONCTION : Sauvegarder les missions vues ===
def sauvegarder_offres_vues(liste_offres):
    with open(FICHIER_OFFRES_VUES, "w") as fichier:
        json.dump(liste_offres, fichier)

# === FONCTION : Récupérer toutes les offres disponibles depuis le site ===
def recuperer_missions():
    url = "https://jobs.extracadabra.com/paris"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    missions = []

    cartes = soup.find_all("div", class_="q-pb-none")

    for carte in cartes:
        try:
            poste = carte.find("span", class_="q-ma-none text-bold text-h4").text.strip()

            infos = carte.find_all("div", class_="q-item__label")
            if len(infos) >= 2:
                lieu = infos[0].text.strip()
                adresse = infos[1].text.strip()
            elif len(infos) == 1:
                lieu = infos[0].text.strip()
                adresse = "Adresse inconnue"
            else:
                lieu = "Lieu inconnu"
                adresse = "Adresse inconnue"

            date = "Date non précisée"
            heure = "Heure non précisée"

            mission = {
                "id": f"{poste}-{lieu}",  # Plus simple, car pas de date dans le HTML ici
                "poste": poste,
                "lieu": lieu,
                "adresse": adresse,
                "date": f"{date} {heure}",
            }
            missions.append(mission)
        except Exception as e:
            print("❌ Erreur extraction mission :", e)

    return missions



# === PROGRAMME PRINCIPAL ===
def surveiller_site():
    offres_deja_envoyees = charger_offres_vues()

    while True:
        print("🔍 Vérification des nouvelles missions...")
        nouvelles_missions = recuperer_missions()
        message = (f"test")
        envoyer_message_telegram(message)

        # Filtrer les missions qu’on n’a jamais vues
        missions_non_vues = [m for m in nouvelles_missions if m["id"] not in offres_deja_envoyees]

        for mission in missions_non_vues:
            message = (
                f"📢 <b>{mission['poste']}</b> chez <b>{mission['lieu']}</b>\n"
                f"📍 {mission['adresse']} | 📅 {mission['date']}\n"
                f"🔗 https://jobs.extracadabra.com/paris?nb=24"
            )
            envoyer_message_telegram(message)
            print("✅ Mission envoyée :", mission["poste"])
            offres_deja_envoyees.append(mission["id"])

        # Sauvegarder l’état actuel
        sauvegarder_offres_vues(offres_deja_envoyees)


        # Attendre avant de recommencer
        time.sleep(INTERVALLE_VERIF_SECONDES)

# === LANCER LE SCRIPT ===
if __name__ == "__main__":
    surveiller_site()
