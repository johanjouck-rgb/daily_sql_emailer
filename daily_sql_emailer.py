import smtplib
import ssl
import json
import random
import datetime
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATIE ---
# Vul hier je Gmail App Password in (NIET je gewone wachtwoord)
# Als je GitHub Actions gebruikt, haal dit dan uit os.environ["GMAIL_APP_PASSWORD"]
SENDER_EMAIL = "ambrasdata@gmail.com"
SENDER_PASSWORD = "tgek ruin jbte vlpf" 
RECEIVER_EMAIL = "Johan.jouck@hotmail.com"

# Bestandsnaam van je vragen database
DB_FILE = "sql_vragen.json"

def load_questions(filename):
    """Laad de vragen uit het JSON bestand."""
    # Check eerst of het bestand bestaat
    if not os.path.exists(filename):
        print(f"FATALE FOUT: Bestand {filename} niet gevonden in {os.getcwd()}")
        return []
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Succesvol {len(data)} vragen geladen.")
        return data
    except json.JSONDecodeError:
        print(f"FOUT: {filename} is geen geldig JSON bestand.")
        return []
    except Exception as e:
        print(f"Onverwachte fout bij laden bestand: {e}")
        return []

def select_random_questions(questions, count=3):
    """Kiest willekeurige vragen."""
    if not questions:
        return []
    
    # Als we minder vragen hebben dan gevraagd, geven we ze allemaal terug (maar geschud)
    if len(questions) < count:
        random.shuffle(questions)
        return questions
        
    return random.sample(questions, count)

def create_html_email(questions):
    """Maakt de HTML opmaak voor de e-mail."""
    today = datetime.date.today().strftime("%d-%m-%Y")
    
    # Header van de mail
    html_content = f"""
    <html>
      <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
          <div style="text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 15px; margin-bottom: 20px;">
            <h2 style="color: #2c3e50; margin: 0;">🧠 Je Dagelijkse SQL Prikkel</h2>
            <p style="color: #7f8c8d; margin-top: 5px;">Datum: {today}</p>
          </div>
          
          <h3 style="color: #34495e;">De Uitdagingen van Vandaag:</h3>
    """

    # Deel 1: De Vragen
    for index, item in enumerate(questions, 1):
        # Iconen kiezen op basis van type
        icon = "❓"
        bg_color = "#f9f9f9"
        border_color = "#bdc3c7"
        
        if item.get('type') == 'Flashcard': 
            icon = "💡"
            bg_color = "#fff8e1" # Zacht geel
            border_color = "#f1c40f"
        elif item.get('type') == 'Query Challenge': 
            icon = "💻"
            bg_color = "#e8f6f3" # Zacht groen/blauw
            border_color = "#1abc9c"
        elif item.get('type') == 'Theorie':
            icon = "📚"
            bg_color = "#eaf2f8" # Zacht blauw
            border_color = "#3498db"
        
        html_content += f"""
          <div style="background-color: {bg_color}; padding: 15px; margin-bottom: 20px; border-left: 5px solid {border_color}; border-radius: 4px;">
            <strong style="color: {border_color}; text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px;">{icon} {item.get('type', 'Vraag')}</strong>
            <p style="font-size: 16px; margin-top: 8px; font-weight: 600;">{item['question']}</p>
          </div>
        """

    # Deel 2: De Spoiler Sectie (Antwoorden)
    html_content += """
          <div style="text-align: center; padding: 30px 0;">
            <p style="font-style: italic; color: #95a5a6; font-size: 0.9em;">Denk eerst na! Scrol dan voor de antwoorden...</p>
            <p style="font-size: 24px; animation: bounce 2s infinite;">⬇️</p>
          </div>
          
          <div style="background-color: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 10px;">
          <h3 style="color: #2ecc71; border-bottom: 1px solid #7f8c8d; padding-bottom: 10px; margin-top: 0;">✅ De Antwoorden</h3>
    """

    for index, item in enumerate(questions, 1):
        html_content += f"""
          <div style="margin-bottom: 20px;">
            <strong style="color: #bdc3c7; font-size: 0.9em;">Antwoord op vraag {index}:</strong>
            <div style="background-color: #34495e; padding: 12px; border-radius: 5px; margin-top: 5px; font-family: 'Courier New', monospace; border-left: 3px solid #2ecc71;">
              {item['answer']}
            </div>
          </div>
        """

    html_content += """
          </div>
          <p style="font-size: 11px; color: #bdc3c7; text-align: center; margin-top: 30px;">
            Gegenereerd door Ambras Data Bot 🤖
          </p>
        </div>
      </body>
    </html>
    """
    return html_content

def send_email():
    """De hoofdfunctie die alles aanstuurt."""
    print("🚀 Script gestart...")
    
    # Wachtwoord check (voor veiligheid)
    if SENDER_PASSWORD == "vul_hier_je_app_password_in":
        print("❌ LET OP: Je hebt het wachtwoord nog niet ingevuld in het script!")
        return

    all_questions = load_questions(DB_FILE)
    
    if not all_questions:
        print("❌ Geen vragen gevonden. Script stopt.")
        return

    selected_questions = select_random_questions(all_questions, 3)
    html_body = create_html_email(selected_questions)

    # E-mail object samenstellen
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"SQL Prikkel {datetime.date.today().strftime('%d/%m')}: Test je Kennis!"
    msg.attach(MIMEText(html_body, 'html'))

    # Verzenden via Gmail SMTP
    try:
        context = ssl.create_default_context()
        print(f"📧 Verbinding maken met Gmail voor {SENDER_EMAIL}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ Succes! De SQL-prikkel is verstuurd.")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authenticatie Fout: Check je e-mailadres en App Password.")
    except Exception as e:
        print(f"❌ Fout bij verzenden: {e}")

if __name__ == "__main__":
    send_email()