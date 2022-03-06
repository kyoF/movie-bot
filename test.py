from tkinter import N
import requests
from bs4 import BeautifulSoup
import datetime

sinjuku_toho_theater = 'https://eiga.com/theater/13/130201/3263/'
main_url_path = 'https://eiga.com/'

response = requests.get(sinjuku_toho_theater)
soup = BeautifulSoup(response.content, 'html.parser')

content_container_info = soup.find_all('div', class_='content-container')
eiga_info = content_container_info[1].find_all('section')

today = datetime.date.today()
day_info = str(today).replace('-', '')
# day_of_week_info = str(today.strftime('%A').lower())

title = []
image_url = []
today_time_schedule = []
detail_url = []

for index, eiga in eiga_info:
    title.appned(eiga.find('h2', class_='title-xlarge margin-top20').find('a').get_text())
    image_url.append(eiga.find('div', class_='movie-image').find('img', class_='lazyloaded')['src'])
    today_time_schedule.append([])
    today_schedule_info_list = eiga.find('td', attrs={ 'data-date':day_info }).find_all('span', class_='btn ticket2')
    for time in today_schedule_info_list:
        today_time_schedule[index].append(time.get_text())
    tmp = eiga.find('a', class_='btn inline-block')['href']
    detail_url.append(f'{main_url_path}{tmp}')

for i in len(title):
    print(title[i])
    print(image_url[i])
    print(today_time_schedule[i])
    print(detail_url[i])
