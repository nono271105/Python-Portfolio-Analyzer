
# Python Portfolio Analyzer

**Outil Python d’analyse de portefeuille exposé aux thématiques défense & géopolitique.**

Ce script analyse un portefeuille construit autour d’ETF et d’options call sélectionnés pour tirer parti de la tendance haussière liée à la doctrine de défense américaine (ex : Iron Dome, Trump, dépenses militaires). Il est désormais **automatisé et déployé sur une machine virtuelle** pour des rapports quotidiens.

---

## Fonctionnalités

- Récupération de données de marché (prix spot, dividendes)
- Calcul de volatilité implicite (`Bisection Method - Dichotomy`)
- Pricing des options (Black-Scholes)
- Évaluation du portefeuille (valeur, P&L, exposition)
- Génération d’un rapport synthétique **HTML**
- **Envoi automatisé et sécurisé des rapports par e-mail**

---

## Structure des fichiers

- `main_portfolio.py` : Point d'entrée principal pour l'exécution du rapport.
- `portfolio_analyzer.py` : Effectue les calculs et la consolidation des positions du portefeuille.
- `portfolio_reporter.py` : Génère le rapport HTML synthétique du portefeuille.
- `market_data_fetcher.py` : Gère la récupération des données de marché (prix spot, rendements obligataires) via Yahoo Finance.
- `implied_volatility_calculator.py` : Estime la volatilité implicite des options en utilisant la méthode de la dichotomie.
- `option_pricing.py` : Calcule le prix des options call selon le modèle de Black-Scholes.
- `email_reporter.py` : Gère l'envoi des rapports générés par e-mail.
- `requirements.txt` : Liste toutes les dépendances Python nécessaires au projet.

---

## Installation

**Python ≥ 3.7 requis**

Pour installer et exécuter le projet, il est fortement recommandé d'utiliser un environnement virtuel :

```bash
# 1. Créez un environnement virtuel (si ce n'est pas déjà fait)
python3 -m venv myenv

# 2. Activez l'environnement virtuel
source myenv/bin/activate

# 3. Installez les dépendances du projet
pip install -r requirements.txt
```

---

## Déploiement et Automatisation sur VM

Le système est conçu pour un déploiement robuste et une exécution automatisée sur une machine virtuelle (VM), telle qu'une instance Google Cloud.

### 1. Préparation de la VM

* **Copiez les fichiers du projet :** Transférez tous les fichiers du projet (`.py`, `requirements.txt`, etc.) de votre machine locale vers un répertoire dédié sur la VM (ex: `/home/votrenomutilisateur/iron/`) 

* **Installez les dépendances sur la VM :** Une fois les fichiers copiés sur la VM, connectez-vous en SSH, naviguez dans le répertoire du projet, activez l'environnement virtuel et installez les dépendances :
    ```bash
    cd /home/xxxx/iron/
    python3 -m venv myenv
    source myenv/bin/activate
    pip install -r requirements.txt
    ```

### 2. Configuration de l'automatisation avec Cron

Les rapports sont automatiquement générés et envoyés par e-mail deux fois par jour via une tâche Cron.

* **Ouvrez votre `crontab` pour édition sur la VM :**
    ```bash
    crontab -e
    ```
* **Ajoutez les lignes suivantes à votre `crontab` :**
    * **Important :** Adaptez les chemins (`/home/xxxx/...`) et les variables d'environnement (`SENDER_EMAIL`, `SENDER_PASSWORD`, `RECEIVER_EMAIL`) avec vos informations. Le `SENDER_PASSWORD` doit être un mot de passe d'application si vous utilisez Gmail avec l'authentification à deux facteurs.
    * Les heures sont définies en **UTC** sur la VM, ce qui correspond à l'heure de Paris (CEST) ajustée. Par exemple, 15h30 CEST = 13h30 UTC, et 22h00 CEST = 20h00 UTC.

    ```cron
    # ------------- Tâches Cron pour Iron Dome --------------
    # Rapports quotidiens à 15h30 et 22h00 (heure de Paris / CEST)
    # Ceci correspond à 13h30 et 20h00 UTC sur la VM

    30 13 * * * SENDER_EMAIL="votre_email@gmail.com" SENDER_PASSWORD="votre_mot_de_passe_app" RECEIVER_EMAIL="votre_email_dest@example.com" /home/xxxx/myenv/bin/python /home/xxxx/iron/main_portfolio.py >> /home/xxxx/cron_output.log 2>&1
    0 20 * * * SENDER_EMAIL="votre_email@gmail.com" SENDER_PASSWORD="votre_mot_de_passe_app" RECEIVER_EMAIL="votre_email_dest@example.com" /home/xxxx/myenv/bin/python /home/xxxx/iron/main_portfolio.py >> /home/xxxx/cron_output.log 2>&1
    ```

* **Suivi et débogage :** La sortie des exécutions Cron est redirigée vers `/home/nolhanmas/cron_output.log`. Vous pouvez le consulter pour vérifier le bon déroulement ou diagnostiquer des erreurs :
    ```bash
    cat /home/xxxx/cron_output.log
    # ou pour un suivi en temps réel :
    tail -f /home/xxxx/cron_output.log
    ```

---

## Exécution (Manuelle)

Pour exécuter le script manuellement depuis l'environnement virtuel activé sur la VM ou votre machine locale :

```bash
python main_portfolio.py
```

**Affichage (en console ou dans le log si automatisé) :**

* Volatilité implicite (IV) et Rendements de dividende des sous-jacents
* Valorisation par position
* P&L total et par actif
* Répartition ETF vs dérivés
* Durée de vie moyenne des calls

---

## Limitations

* Utilisation du modèle de Black-Scholes sur des options américaines (le modèle est théoriquement pour les options européennes).
* Dépendance des données à l'API de Yahoo Finance.

---

## Objectif du projet

Fournir une base robuste et automatisée pour suivre des portefeuilles avec une analyse détaillée des options et des ETF.

---

## Améliorations Possibles

* Ajouter la possibilité de changer dynamiquement la composition du portefeuille via un fichier de configuration externe (ex : JSON, CSV).
* Intégrer d'autres modèles d'évaluation d'options (ex: Monte Carlo pour les options américaines).
* Gérer les erreurs d'API de manière plus robuste (ex: retries, backoff).

---
