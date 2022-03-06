import requests
from bs4 import BeautifulSoup
import datetime
import slackweb
import json

sinjuku_toho_theater = 'https://eiga.com/theater/13/130201/3263/'
toho_reservation_url = 'https://hlo.tohotheater.jp/net/movie/TNPI3060J01.do?sakuhin_cd='

# slackへの通知設定
json_f = open('slack_info.json', 'r')
json_data = json.load(json_f)
slack = slackweb.Slack(url=json_data["incoming_webhook_url"])
json_f.close()

response = requests.get(sinjuku_toho_theater)
soup = BeautifulSoup(response.content, 'html.parser')

content_container_info = soup.find_all('div', class_='content-container')
# 映画情報部分のみを取得
eiga_info = content_container_info[1].find_all('section')

# today = str(datetime.date.today())
today = str(datetime.date.today() + datetime.timedelta(days=1)) # test用（明日の日付で取得）

sakuhin_code = []
title = []
image_url = []
today_time_schedule = []
loop_index = 0

for eiga in eiga_info:
    # 今日放映する作品を取得
    tmp_schedule = eiga.find('div', class_='movie-schedule').find('td', attrs={'data-date':today.replace('-', '')})

    if tmp_schedule:
        today_time_schedule.append([])
        
        today_schedule_info_list = tmp_schedule.find_all(['span', 'a'])
        # 初めの要素は曜日情報なので削除
        today_schedule_info_list.pop(0)
        for time in today_schedule_info_list:
            # 時間とそれに対応する席予約のURLを辞書型で取得
            toho_seat_url = time['href']
            today_time_schedule[loop_index] = { 'schedule_time':time.get_text(), 'reservation_url':toho_seat_url }
            
            # 東宝のURLから作品コードを取得
            if len(sakuhin_code) != loop_index+1:
                first_target_str = 'sakuhin_cd='
                second_target_str = '&screen_cd='
                first_idx = toho_seat_url.find(first_target_str)
                second_idx = toho_seat_url.find(second_target_str)
                tmp_sakuhin_code = toho_seat_url[first_idx+len(first_target_str):second_idx]
                sakuhin_code.append(tmp_sakuhin_code)

        # 作品タイトルを取得
        title.append(eiga.find('h2', class_='title-xlarge margin-top20').find('a').get_text())
        # 作品の画像を取得
        image_url.append(eiga.find('div', class_='movie-image').find('img')['src'])
        loop_index += 1

for i in range(len(title)):
#     print(f'title : {title[i]}')
    print(f'image : {image_url[i]}')
#     print(f'schedule : {today_time_schedule[i]}')
#     print(f'reservation : {toho_reservation_url}{sakuhin_code[i]}')
#     print('------------------------------')

attachments = [
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alternative hotel options*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{sinjuku_toho_theater}|Bates Motel> :star::star:"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View",
                        "emoji": True
                    },
                    "value": "view_alternate_1"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "<https://example.com|The Great Northern Hotel> :star::star::star::star:"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View",
                        "emoji": True
                    },
                    "value": "view_alternate_2"
                }
            }
        ]
    },
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alternative hotel options*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "<https://example.com|Bates Motel> :star::star:"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View",
                        "emoji": True
                    },
                    "value": "view_alternate_1"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "<https://example.com|The Great Northern Hotel> :star::star::star::star::star:"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View",
                        "emoji": True
                    },
                    "value": "view_alternate_2"
                }
            }
        ]
    }
]

slack.notify(text='python to slack', attachments=attachments)
