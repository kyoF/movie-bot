import requests
from bs4 import BeautifulSoup
import datetime
import slackweb
import json

# 取得先のページ
json_file = open('slack_info.json', 'r')
json_data = json.load(json_file)
sinjuku_toho_theater = json_data['target_url_scraping_sinjuku_toho_theater']
toho_reservation_url = json_data['toho_reservation_url_without_sakuhin_cd']
json_file.close()

# 明日の日付と曜日情報を取得する
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
month = tomorrow.month
day = tomorrow.day
day_of_week = tomorrow.strftime('%a')

all_movies = []  # 全ての映画情報を入れる
loop_index = 0
slack_notify_info = [
    {
        "blocks": []
    }
]  # slackに通知するときに渡すリッチテキスト

response = requests.get(sinjuku_toho_theater)
soup = BeautifulSoup(response.content, 'html.parser')
content_container_info = soup.find_all('div', class_='content-container')
# 映画情報部分のみを取得
movies = content_container_info[1].find_all('section')

for movie in movies:
    movie_info = {
        'code': '',
        'title': '',
        'details': [],
        'image_url': '',
        'time_schedules': [],
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
    movie_schedules = movie.find_all('div', class_='movie-schedule')
    for movie_schedule in movie_schedules:
        time_schedules_dict = {
            'type': '',
            'time_and_reservation': []
        }
        movie_type = movie_schedule.find('div', class_='movie-type')
        try:
            time_schedules_dict['type'] = movie_type.get_text()
        except:
            time_schedules_dict['type'] = '通常'

        tomorrow_movie_schedules = movie_schedule.find(
            'td', attrs={'data-date': str(tomorrow).replace('-', '')})
        try:
            tomorrow_time_and_reservation = tomorrow_movie_schedules.find_all(
                'a')
        except:
            tomorrow_time_and_reservation = None

        if tomorrow_time_and_reservation:
            for time_schedule in tomorrow_time_and_reservation:
                time_and_reservation_dict = {
                    'time': '',
                    'reservation': ''
                }
                # タイムスケジュールを取得
                if 'href' in str(time_schedule):
                    tmp_reservation_url = time_schedule['href']
                    time_and_reservation_dict['reservation'] = tmp_reservation_url
                    time_and_reservation_dict['time'] = time_schedule.get_text(
                    )
                    # 東宝のURLから作品コードを取得
                    if movie_info['code'] == '':
                        first_target_str = 'sakuhin_cd='
                        second_target_str = '&screen_cd='
                        first_idx = tmp_reservation_url.find(first_target_str)
                        second_idx = tmp_reservation_url.find(
                            second_target_str)
                        tmp_code = tmp_reservation_url[first_idx +
                                                       len(first_target_str):second_idx]
                        movie_info['code'] = tmp_code
                else:
                    time_and_reservation_dict['reservation'] = ''
                    time_and_reservation_dict['time'] = time_schedule.get_text(
                    )
                time_schedules_dict['time_and_reservation'].append(
                    time_and_reservation_dict)
        else:
            time_and_reservation_dict = {
                'time': '',
                'reservation': ''
            }
            time_schedules_dict['time_and_reservation'].append(
                time_and_reservation_dict)

        movie_info['time_schedules'].append(time_schedules_dict)

    all_movies.append(movie_info)

for movie in all_movies:
    slack_notify_info[0]['blocks'].append(
        {
            "type": "divider"
        }
    )
    slack_notify_info[0]['blocks'].append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f'<{toho_reservation_url}{movie["code"]}|{movie["title"]}> \n \n {"  ".join(movie["details"])}'
            },
            "accessory": {
                "type": "image",
                "image_url": movie["image"],
                "alt_text": movie["title"]
            }
        }
    )
    for time_schedule_index, time_schedule in enumerate(movie['time_schedules']):
        if movie['time_schedules'][0]['time_and_reservation'][0]['time'] == '':
            slack_notify_info[0]['blocks'].append(
                {
                    'type': "section",
                    'text': {
                        'type': 'plain_text',
                        'text': f'- - - - - {time_schedule["type"]} - - - - -'
                    },
                }
            )
            slack_notify_info[0]['blocks'].append(
                {
                    'type': 'section',
                    'text': {
                        'type': 'plain_text',
                        'text': '上映情報なし'
                    }
                }
            )
        else:
            slack_notify_info[0]['blocks'].append(
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f'- - - - - {time_schedule["type"]} - - - - -'
                    }
                }
            )
            slack_notify_info[0]['blocks'].append(
                {
                    "type": "actions",
                    "elements": []
                }
            )
            for time_and_reservation in time_schedule['time_and_reservation']:
                slack_notify_info[0]['blocks'][len(slack_notify_info[0]['blocks'])-1]['elements'].append(
                    {
                        'type': 'button',
                        'text': {
                            'type': 'plain_text',
                            'text': time_and_reservation['time']
                        },
                        'url': time_and_reservation['reservation']
                    }
                )

# slackへの通知設定
json_file = open('slack_info.json', 'r')
json_data = json.load(json_file)
slack = slackweb.Slack(url=json_data['incoming_webhook_url'])
json_file.close()
with open('testdata.py', 'w') as f:
    print(slack_notify_info, file=f)
slack.notify(
    text=f'明日 ( {str(month)}/{str(day)} {str(day_of_week)} ) の映画情報', attachments=slack_notify_info)
