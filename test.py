import requests
from bs4 import BeautifulSoup
import datetime
import slackweb
import json

# 取得先のページ
sinjuku_toho_theater = 'https://eiga.com/theater/13/130201/3263/'
toho_reservation_url = 'https://hlo.tohotheater.jp/net/movie/TNPI3060J01.do?sakuhin_cd='

# slackへの通知設定
json_f = open('slack_info.json', 'r')
json_data = json.load(json_f)
slack = slackweb.Slack(url=json_data['incoming_webhook_url'])
json_f.close()

response = requests.get(sinjuku_toho_theater)
soup = BeautifulSoup(response.content, 'html.parser')

content_container_info = soup.find_all('div', class_='content-container')
# 映画情報部分のみを取得
movies = content_container_info[1].find_all('section')

tomorrow = datetime.date.today() + datetime.timedelta(days=1)
month = tomorrow.month
day = tomorrow.day
day_of_week = tomorrow.strftime('%a')

all_movies = []
loop_index = 0

slack_notify_info = []

for movie in movies:
    movie_info = {
        'code' : '',
        'title' : '',
        'details' : [],
        'image_url' : '',
        'time_schedules' : [],
    }
    time_schedules_dict = {
        'type' : '',
        'time_and_reservation' : []
    }
    time_and_reservation_dict = {
        'time' : '',
        'reservation' : ''
    }

    # タイトルを取得
    tmp_title = movie.find('h2', class_='title-xlarge margin-top20')
    if '<a href' in tmp_title:
        movie_info['title'] = tmp_title.find('a').get_text()
    else:
        movie_info['title'] = tmp_title.get_text()

    # 詳細情報（公開日・上映時間・レイティング）を取得
    tmp_image_and_details = movie.find('div', class_='movie-image')
    tmp_details = tmp_image_and_details.find('p', class_='data')
    for detail in tmp_details:
        movie_info['details'].append(detail.get_text())

    # 参考画像を取得
    tmp_image_info = str(tmp_image_and_details.find('noscript'))
    first_target_str = 'src="'
    second_target_str = '" width='
    first_idx = tmp_image_info.find(first_target_str)
    second_idx = tmp_image_info.find(second_target_str)
    tmp_image_url = tmp_image_info[first_idx+len(first_target_str):second_idx]
    movie_info['image'] = tmp_image_url

    # 上映方法（通常・字幕・4DX等）を取得
    screening_way_list = movie.find_all('div', class_='movie-schedule').find('td', attrs={'data-date':str(tomorrow).replace('-', '')})
    for time_schedules in screening_way_list:
        # 上映方法を取得
        movie_type = time_schedules.find('div', class_='movie-type')
        time_schedules_dict['type'] = movie_type.get.text()
        # タイムスケジュールを取得
        tmp_time_and_reservation_url = time_schedules.find_all(['span', 'a'])
        tmp_time_and_reservation_url.pop(0)
        for time_and_url in tmp_time_and_reservation_url:
            if 'href' in str(time_and_url):
                tmp_reservation_url = time_and_url['href']
                time_and_reservation_dict['reservation'] = tmp_reservation_url
                time_and_reservation_dict['time'] = time_and_url.get_text()
                # 東宝のURLから作品コードを取得
                if movie_info['code'] == '':
                    first_target_str = 'sakuhin_cd='
                    second_target_str = '&screen_cd='
                    first_idx = tmp_reservation_url.find(first_target_str)
                    second_idx = tmp_reservation_url.find(second_target_str)
                    tmp_code = tmp_reservation_url[first_idx+len(first_target_str):second_idx]
                    movie_info['code'] = tmp_code
            else:
                time_and_reservation_dict['reservation'] = ''
                time_and_reservation_dict['time'] = time_and_url.get_text()
            time_schedules_dict['time_and_reservation'].append(time_and_reservation_dict)
        movie_info['time_schedules'].append(time_schedules_dict)

    all_movies.append(movie_info)

for i in range(len(all_movies)):
    slack_notify_info.append(
        {
            'blocks': [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f'<{toho_reservation_url}{sakuhin_code[i]}|{title[i]}> \n \n {"  ".join(release_info[i])}'
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": image_url[i],
                        "alt_text": title[i]
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "- - - - - 通常 - - - - -"
                    }
                },
                {
                    "type": "section",
                    "fields": []
                }
            ]
        }
    )
    for j in range(len(today_time_schedule[i])):
        if today_time_schedule[i][j]["reservation_url"] == '':
            reserve_link = f'{today_time_schedule[i][j]["schedule_time"]}'
        else:
            reserve_link = f'<{today_time_schedule[i][j]["reservation_url"]}|{today_time_schedule[i][j]["schedule_time"]}>'
        
        slack_notify_info[i]['blocks'][3]['fields'].append(
            {
                "type": "mrkdwn",
                "text": reserve_link
            }
        )

try:
    slack.notify(text=f'明日 ( {str(month)}/{str(day)} {str(day_of_week)} ) の映画情報', attachments=slack_notify_info)
    # slack.notify(text=f'明日 ( {str(month)}/{str(day)} {str(day_of_week)} ) の映画情報')
except Exception as e:
    print('エラー')
    print(e)
    raise Exception(e)
