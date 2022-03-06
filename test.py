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

title = []
# image_url = []
today_time_schedule = []
detail_url = []
loop_index = 0

for eiga in eiga_info:
    tmp_schedule = eiga.find('div', class_='movie-schedule').find('td', attrs={'data-date':day_info})
    if tmp_schedule:
        today_time_schedule.append([])
        today_schedule_info_list = tmp_schedule.find_all(['span', 'a'])
        for time in today_schedule_info_list:
            today_time_schedule[loop_index].append(time.get_text())

        title.append(eiga.find('h2', class_='title-xlarge margin-top20').find('a').get_text())
        # image_url.append(eiga.find('div', class_='movie-image').find('img', attrs={'alt':title[loop_index]})['src'])
        relative_path = eiga.find('a', class_='btn inline-block')['href']
        detail_url.append(f'{main_url_path}{relative_path}')
        loop_index += 1

for i in range(len(title)):
    print(f'title : {title[i]}')
    # print(f'image : {image_url[i]}')
    # print(f'image : {type(image_url[i])}')
    print(f'schedule : {today_time_schedule[i]}')
    print(f'url : {detail_url[i]}')
    print('------------------------------')
