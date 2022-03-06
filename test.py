from asyncore import loop
import requests
from bs4 import BeautifulSoup
import datetime

sinjuku_toho_theater = 'https://eiga.com/theater/13/130201/3263/'
toho_detail_url = 'https://hlo.tohotheater.jp/net/movie/TNPI3060J01.do?sakuhin_cd='

response = requests.get(sinjuku_toho_theater)
soup = BeautifulSoup(response.content, 'html.parser')

content_container_info = soup.find_all('div', class_='content-container')
eiga_info = content_container_info[1].find_all('section')

# today = str(datetime.date.today())
today = '2022-03-07' # テスト用

sakuhin_code = []
title = []
# image_url = []
today_time_schedule = []
loop_index = 0

for eiga in eiga_info:
    tmp_schedule = eiga.find('div', class_='movie-schedule').find('td', attrs={'data-date':today.replace('-', '')})
    if tmp_schedule:
        today_time_schedule.append([])
        today_schedule_info_list = tmp_schedule.find_all(['span', 'a'])
        today_schedule_info_list.pop(0)
        for time in today_schedule_info_list:
            today_time_schedule[loop_index] = { 'schedule_time':time.get_text(), 'reservation_url':'' }
            toho_seat_url = time['href']
            today_time_schedule[loop_index]['reservation_url'] = toho_seat_url
            if len(sakuhin_code) != loop_index+1:
                first_target_str = 'sakuhin_cd='
                second_target_str = '&screen_cd='
                first_idx = toho_seat_url.find(first_target_str)
                second_idx = toho_seat_url.find(second_target_str)
                tmp_sakuhin_code = toho_seat_url[first_idx+len(first_target_str):second_idx]
                sakuhin_code.append(tmp_sakuhin_code)

        title.append(eiga.find('h2', class_='title-xlarge margin-top20').find('a').get_text())
        # image_url.append(eiga.find('div', class_='movie-image').find('img', attrs={'alt':title[loop_index]})['src'])
        loop_index += 1

for i in range(len(title)):
    print(f'title : {title[i]}')
    # print(f'image : {image_url[i]}')
    # print(f'image : {type(image_url[i])}')
    print(f'schedule : {today_time_schedule[i]}')
    print(f'reservation : {toho_detail_url}{sakuhin_code[i]}')
    print('------------------------------')
