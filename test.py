from email.mime import image
import requests
from bs4 import BeautifulSoup
import datetime

response = requests.get('https://eiga.com/theater/13/130201/3263/')
soup = BeautifulSoup(response.content, 'html.parser')

content_container_info = soup.find_all('div', class_='content-container')
eiga_info = content_container_info[1].find_all('section')

today = datetime.date.today()
day_info = today.replace('-', '')
day_of_week_info = today.strftime('%A').lower()

for eiga in eiga_info:
    title = eiga.find('h2', class_='title-xlarge margin-top20').find('a').get_text()
    image_url = eiga.find('div', class_='movie-image').find('img', class_='lazyloaded')['src']
    schedule = eiga.find('td', )
    #detail_url

