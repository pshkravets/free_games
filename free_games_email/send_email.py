import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from free_games_email.models import User, Game
from free_games_email.database import get_db

db = next(get_db())

def send_game_email():
    games = get_games_list()
    emails = get_user_emails()
    for game in games:
        for email in emails:
            message = create_email(game)
            message['To'] = email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(message['From'], os.environ.get('APP_PASSWORD'))
                server.sendmail(message['From'], email, message.as_string())
                server.quit()

def get_games_list():
    return db.query(Game).all()


def get_user_emails():
    users = db.query(User).filter_by(email_notifications=True).all()
    return [user.email for user in users]


def create_email(game):
    sender = os.environ.get('YOUR_EMAIL')
    html = '''
        <html>
            <body>
                <p>Hi, here is free game of the week<br>
                Game "{game}" will be avaliable {start_date} to {end_date} for free.<br>
                <img src="cid:image" alt="image" width="500">.</p>
            </body>
        </html>
    '''.format(game=game.name, start_date=game.start_date, end_date=game.end_date)

    message = MIMEMultipart()
    message['Subject'] = 'New free games avaliable in EpicGames'
    message['From'] = sender

    message.attach(MIMEText(html, 'html'))

    image_path = os.path.join('/app', 'free_games_email', 'media', 'img', game.img)

    with open(image_path, 'rb') as img:
        msg_img = MIMEImage(img.read(), name=os.path.basename(image_path))
        msg_img.add_header('Content-iD', '<image>')
        message.attach(msg_img)
    return message

send_game_email()
