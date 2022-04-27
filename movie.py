import requests
from bs4 import BeautifulSoup
import datetime
import slackweb
import os
from dotenv import load_dotenv


def main(response, context):
    load_dotenv()

    target_url = get_url_from_dotenv('target_scraped_url')

    movies = []

    html = get_movies_from_html(target_url)
    all_movies = html.find_all(
        'div', class_='content-container')[1].find_all('section')

    for movie in all_movies:
        movie_info = {
            'code': '',
            'title': '',
            'details': [],
            'image_url': '',
            'schedules': [],
        }

        movie_info['code'] = get_code(movie)
        movie_info['title'] = get_title(movie)
        movie_info['details'] = get_details(movie)
        movie_info['image_url'] = get_image_url(movie)
        movie_info['schedules'] = get_schedules(movie)

        movies.append(movie_info)

    slack_text = create_slack_text(movies)

    slack_notify(slack_text)


def get_today():
    return datetime.date.today()


def get_url_from_dotenv(value):
    return os.getenv(value)


def get_movies_from_html(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


def get_title(movie):
    title = movie.find('h2', class_='title-xlarge margin-top20')
    if '<a href' in title:
        return title.find('a').get_text()
    return title.get_text()


def get_details(movie):
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


def get_schedules(movie):
    all_schedule = movie.find_all('div', class_='movie-schedule')
    schedule_list = []
    for schedule_info in all_schedule:
        schedule_info_dict = {
            'type': '',
            'time_and_reservation_url': []
        }

        schedule_info_dict['type'] \
            = get_type(schedule_info)
        schedule_info_dict['time_and_reservation_url'] \
            = get_time_and_reservation_url(schedule_info)

        schedule_list.append(schedule_info_dict)

    return schedule_list


def get_type(movie_schedule):
    movie_type = movie_schedule.find('div', class_='movie-type')
    try:
        return movie_type.get_text()
    except:
        return '通常'


def get_time_and_reservation_url(schedule_info):
    today = get_today()
    time_and_reservation_url_list = []
    schedule = schedule_info.find(
        'td', attrs={'data-date': str(today).replace('-', '')})

    try:
        all_time_and_reservation_url = schedule.find_all('a')
    except:
        all_time_and_reservation_url = None

    if all_time_and_reservation_url:
        for time_and_reservation_url in all_time_and_reservation_url:
            time_and_reservation_url_dict = {
                'time': '',
                'reservation_url': ''
            }

            time_and_reservation_url_dict['time'] \
                = get_time(time_and_reservation_url)
            time_and_reservation_url_dict['reservation_url'] \
                = get_reservation_url(time_and_reservation_url)

            time_and_reservation_url_list.append(time_and_reservation_url_dict)

    else:
        time_and_reservation_url_dict = {
            'time': '',
            'reservation_url': ''
        }
        time_and_reservation_url_list.append(time_and_reservation_url_dict)

    return time_and_reservation_url_list


def get_time(time):
    return time.get_text()


def get_reservation_url(reservation_url):
    if 'href' in str(reservation_url):
        return reservation_url['href']
    return ''


def get_code(movie):
    try:
        url = str(movie.find('a', class_='btn ticket2')['href'])
        first_target_str = 'sakuhin_cd='
        second_target_str = '&screen_cd='
        first_idx = url.find(first_target_str)
        second_idx = url.find(second_target_str)
        code = url[first_idx + len(first_target_str):second_idx]
        return code
    except:
        return ""


def create_slack_text(all_movies):
    slack_text_list = []
    toho_reservation_url = get_url_from_dotenv(
        'toho_reservation_url_without_sakuhin_cd')
    sinjuku_toho_theater_url = get_url_from_dotenv('target_scraped_url')
    today = get_today()
    month = today.month
    day = today.day

    for movie_index, movie in enumerate(all_movies):
        slack_text_list.append(
            {
                "blocks": [
                    {
                        'type': 'divider'
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'<{toho_reservation_url}{movie.get("code")}|{movie.get("title")}> \n \n {" ".join(movie.get("details"))}'
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": movie.get("image_url"),
                            "alt_text": movie.get("title")
                        }
                    }
                ]
            }
        )
        for schedule_index, schedule in enumerate(movie['schedules']):
            if movie['schedules'][schedule_index]['time_and_reservation_url'][0]['time'] == '':
                slack_text_list[movie_index]['blocks'].append(
                    {
                        'type': "section",
                        'text': {
                            'type': 'plain_text',
                            'text': f'- - - - - {schedule.get("type")} - - - - -'
                        },
                    }
                )
                slack_text_list[movie_index]['blocks'].append(
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'{str(month)}/{str(day)}の上映情報なし\n 別日のスケジュールは<{sinjuku_toho_theater_url}|こちら>から'
                        }
                    }
                )
            else:
                slack_text_list[movie_index]['blocks'].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": f'- - - - - {schedule.get("type")} - - - - -'
                        }
                    }
                )
                slack_text_list[movie_index]['blocks'].append(
                    {
                        "type": "actions",
                        "elements": []
                    }
                )
                for time_and_reservation_url in schedule['time_and_reservation_url']:
                    slack_text_list[movie_index]['blocks'][2+(schedule_index*2+1)]['elements'].append(
                        {
                            'type': 'button',
                            'text': {
                                'type': 'plain_text',
                                'text': time_and_reservation_url.get('time')
                            },
                            'url': time_and_reservation_url.get('reservation_url')
                        }
                    )

    return slack_text_list


def slack_notify(slack_text):
    today = get_today()
    month = today.month
    day = today.day
    day_of_week = today.strftime('%a')

    slack_url = slackweb.Slack(get_url_from_dotenv('incoming_webhook_url'))
    slack_url.notify(
        text=f'明日 ( {str(month)}/{str(day)} {str(day_of_week)} ) の映画情報',
        attachments=slack_text
    )


if __name__ == '__main__':
    main('', '')
