import requests
from bs4 import BeautifulSoup
import datetime
import slackweb
import json


def main():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    target_url = get_url_from_json('target_scraped_url')

    all_movies = []

    html = get_movies_from_html(target_url)
    movies_list_form_html = html.find_all(
        'div', class_='content-container')[1].find_all('section')

    for movie in movies_list_form_html:
        movie_info = {
            'code': '',
            'title': '',
            'details': [],
            'image_url': '',
            'time_schedules': [],
        }

        movie_info['code'] = get_code(movie)
        movie_info['title'] = get_title(movie)
        movie_info['details'] = get_details_list(movie)
        movie_info['image_url'] = get_image_url(movie)
        movie_info['time_schedules'] = get_time_schedules_list(movie, tomorrow)

        all_movies.append(movie_info)

    slack_notify_text = adjust_slack_notify_text(all_movies)

    slack_notify(tomorrow, slack_notify_text)


def get_url_from_json(key):
    with open('url_info.json') as f:
        json_data = json.load(f)
        return json_data[key]


def get_movies_from_html(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


def get_title(movie):
    title = movie.find('h2', class_='title-xlarge margin-top20')
    if '<a href' in title:
        return title.find('a').get_text()
    return title.get_text()


def get_details_list(movie):
    details = movie.find('div', class_='movie-image').find('p', class_='data')
    details_list = []
    for elem in details:
        details_list.append(elem.get_text())
    return details_list


def get_image_url(movie):
    image = str(movie.find('div', class_='movie-image').find('noscript'))
    first_target_str = 'src="'
    second_target_str = '" width='
    first_idx = image.find(first_target_str)
    second_idx = image.find(second_target_str)
    image_url = image[first_idx+len(first_target_str):second_idx]
    return image_url


def get_time_schedules_list(movie, tomorrow):
    movie_schedules = movie.find_all('div', class_='movie-schedule')
    time_schedules_list = []
    for movie_schedule in movie_schedules:
        time_schedules_dict = {
            'type': '',
            'time_and_reservation': []
        }

        time_schedules_dict['type'] = get_type(movie_schedule)
        time_schedules_dict['time_and_reservation'] = get_time_and_reservation_list(
            movie_schedule, tomorrow)

        time_schedules_list.append(time_schedules_dict)

    return time_schedules_list


def get_type(movie_schedule):
    movie_type = movie_schedule.find('div', class_='movie-type')
    try:
        return movie_type.get_text()
    except:
        return '通常'


def get_time_and_reservation_list(movie_schedule, tomorrow):
    time_and_reservation = []
    tomorrow_movie_schedules = movie_schedule.find(
        'td', attrs={'data-date': str(tomorrow).replace('-', '')})
    try:
        tomorrow_time_and_reservation = tomorrow_movie_schedules.find_all('a')
    except:
        tomorrow_time_and_reservation = None
    if tomorrow_time_and_reservation:
        for time_schedule in tomorrow_time_and_reservation:
            time_and_reservation_dict = {
                'time': '',
                'reservation': ''
            }

            time_and_reservation['time'] = get_time(time_schedule)
            time_and_reservation['reservation'] = get_reservation(
                time_schedule)

            time_and_reservation.append(time_and_reservation_dict)

    else:
        time_and_reservation_dict = {
            'time': '',
            'reservation': ''
        }
        time_and_reservation.append(time_and_reservation_dict)

    return time_and_reservation


def get_time(time_schedule):
    return time_schedule.get_text()


def get_reservation(time_schedule):
    if 'href' in str(time_schedule):
        return time_schedule['href']
    return ''


def get_code(movie):
    url = str(movie.find('a', class_='btn ticket2')['href'])
    first_target_str = 'sakuhin_cd='
    second_target_str = '&screen_cd='
    first_idx = url.find(first_target_str)
    second_idx = url.find(second_target_str)
    code = url[first_idx + len(first_target_str):second_idx]
    return code


def adjust_slack_notify_text(all_movies):
    slack_notify_text = create_slack_text_blocks(all_movies)
    return slack_notify_text


def create_slack_text_blocks(all_movies, slack_text_list):
    toho_reservation_url = get_url_from_json(
        'toho_reservation_url_without_sakuhin_cd')
    for movie_index, movie in enumerate(all_movies):
        slack_text_list.append(
            {
                "blicks": [
                    {
                        'type': 'divider'
                    },
                    {
                        'type': 'section',
                        'type': {
                            'type': 'mrkdwn',
                            'text': f'<{toho_reservation_url}{movie["code"]}|{movie["title"]}> \n \n {" ".join(movie["details"])}'
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": movie["image"],
                            "alt_text": movie["title"]
                        }
                    }
                ]
            }
        )
        slack_text_list.append()
    return slack_text_list


def slack_notify(tomorrow, slack_notify_text):
    month = tomorrow.month
    day = tomorrow.day
    day_of_week = tomorrow.strftime('%a')
    slack_url = get_url_from_json('incomming_webhook_url')
    slack_url.notify(
        text=f'明日 ( {str(month)}/{str(day)} {str(day_of_week)} ) の映画情報',
        attachments=slack_notify_text
    )
# for movie_index, movie in enumerate(all_movies):
#     slack_notify_info.append(
#         {
#             "blocks": [
#                 {
#                     "type": "divider"
#                 },
#                 {
#                     "type": "section",
#                     "text": {
#                         "type": "mrkdwn",
#                         "text": f'<{toho_reservation_url}{movie["code"]}|{movie["title"]}> \n \n {" ".join(movie["details"])}'
#                     },
#                     "accessory": {
#                         "type": "image",
#                         "image_url": movie["image"],
#                         "alt_text": movie["title"]
#                     }
#                 }
#             ]
#         }
#     )
#     for time_schedule_index, time_schedule in enumerate(movie['time_schedules']):
#         if movie['time_schedules'][time_schedule_index]['time_and_reservation'][0]['time'] == '':
#             slack_notify_info[movie_index]['blocks'].append(
#                 {
#                     'type': "section",
#                     'text': {
#                         'type': 'plain_text',
#                         'text': f'- - - - - {time_schedule["type"]} - - - - -'
#                     },
#                 }
#             )
#             slack_notify_info[movie_index]['blocks'].append(
#                 {
#                     'type': 'section',
#                     'text': {
#                         'type': 'mrkdwn',
#                         'text': f'{str(month)}/{str(day)}の上映情報なし\n 別日のスケジュールは<{sinjuku_toho_theater}|こちら>から'
#                     }
#                 }
#             )
#         else:
#             slack_notify_info[movie_index]['blocks'].append(
#                 {
#                     "type": "section",
#                     "text": {
#                         "type": "plain_text",
#                         "text": f'- - - - - {time_schedule["type"]} - - - - -'
#                     }
#                 }
#             )
#             slack_notify_info[movie_index]['blocks'].append(
#                 {
#                     "type": "actions",
#                     "elements": []
#                 }
#             )
#             for time_and_reservation_index, time_and_reservation in enumerate(time_schedule['time_and_reservation']):
#                 slack_notify_info[movie_index]['blocks'][2+(time_schedule_index*2+1)]['elements'].append(
#                     {
#                         'type': 'button',
#                         'text': {
#                             'type': 'plain_text',
#                             'text': time_and_reservation['time']
#                         },
#                         'url': time_and_reservation['reservation']
#                     }
#                 )


if __name__ == '__main__':
    main()
