# email_reporter.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_email(subject, body, to_email, from_email, password, smtp_server='smtp.gmail.com', smtp_port=587, is_html=False):
    """
    Envoie un e-mail avec le contenu spécifié.

    Paramètres:
    subject (str): Sujet de l'e-mail.
    body (str): Contenu de l'e-mail.
    to_email (str): Adresse e-mail du destinataire.
    from_email (str): Adresse e-mail de l'expéditeur.
    password (str): Mot de passe de l'expéditeur (ou mot de passe d'application).
    smtp_server (str): Serveur SMTP de l'expéditeur.
    smtp_port (int): Port SMTP de l'expéditeur.
    is_html (bool): Indique si le corps de l'e-mail est en HTML (True) ou en texte brut (False).
    """
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # --- Modification clé : Spécifier le type de contenu et l'encodage UTF-8 ---
    if is_html:
        msg.attach(MIMEText(body, 'html', 'utf-8')) # Corps en HTML avec encodage UTF-8
    else:
        msg.attach(MIMEText(body, 'plain', 'utf-8')) # Corps en texte brut avec encodage UTF-8

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Mettre en place le cryptage TLS
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False



if __name__ == "__main__":
    # --- Configuration pour le test (ces valeurs sont à des fins de test du module) ---
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "abcdef@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "xxxxxxxxxx")  # Utilisez un mot de passe d'application pour Gmail si l'authentification à deux facteurs est activée
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "abcdef@gmail.com")


    # --- Modification : Vérifier si les identifiants ont été renseignés ---
    if not SENDER_EMAIL or not SENDER_PASSWORD: 
        print("Veuillez configurer SENDER_EMAIL et SENDER_PASSWORD pour envoyer l'email de test.")
        print("Pour Gmail, utilisez un 'mot de passe d'application' si vous avez l'authentification à deux facteurs.")
    else:
        test_subject = "Test d'envoi d'email depuis Iron Dome avec accents €"
        test_body_plain = "Ceci est un email de test en texte brut avec des accents : éàçüö€£¥."
        test_body_html = "<h1>Test HTML</h1><p>Ceci est un <b>email HTML</b> avec des accents : éàçüö€£¥ et un symbole Euro : <b>123.45€</b>.</p>"
        
        print("\nTentative d'envoi d'email en texte brut...")
        send_email(test_subject + " (texte brut)", test_body_plain, RECEIVER_EMAIL, SENDER_EMAIL, SENDER_PASSWORD, is_html=False)

        print("\nTentative d'envoi d'email en HTML...")
        send_email(test_subject + " (HTML)", test_body_html, RECEIVER_EMAIL, SENDER_EMAIL, SENDER_PASSWORD, is_html=True)
