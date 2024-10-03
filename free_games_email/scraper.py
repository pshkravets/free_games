import os
import requests

from free_games_email.models import Game
from free_games_email.database import get_db, Base, engine

db = next(get_db())

Base.metadata.create_all(bind=engine)

url = "https://zylalabs.com/api/2649/complimentary+epic+games+api/2671/free+games"

headers = {
    'Authorization': f'Bearer {os.environ.get("ZLABS_TOKEN")}'
}

response = requests.request("GET", url, headers=headers)

games = response.json()

db.query(Game).delete()

images_path = os.path.join('/app', 'free_games_email', 'media', 'img')
os.makedirs(images_path, exist_ok=True)


def download_image(image_url):
    img_response = requests.get(image_url)
    with open(os.path.join(images_path, os.path.basename(image_url)), 'wb') as file:
        file.write(img_response.content)


def add_game_to_db(game):
    created_game = Game(
        name=game['title'],
        description=game['description'],
        start_date=game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['startDate'],
        end_date=game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate'],
        img=os.path.join(images_path, os.path.basename(game['keyImages'][0]['url']))
    )
    db.add(created_game)
    db.commit()


for game in games['freeGames']['current']:
    if game['price']['totalPrice']['discountPrice'] == 0:
        download_image(game['keyImages'][0]['url'])
        add_game_to_db(game)


