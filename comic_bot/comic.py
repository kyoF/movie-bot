import requests
from bs4 import BeautifulSoup
import json
import datetime


def main():
    tomorrow = get_tomorrow_date()
    year = tomorrow.year
    month = tomorrow.month
    day = tomorrow.day

    target_url = get_url_from_json('target_scraped_url').format(year, month)
    comics = get_comic_info_from_html(target_url)
    comics_list = comics.find_all('tr')
    for day_index, comic in enumerate(comics_list):
        if day_index+1 == day:
            comics_of_day = comic.find(
                'div', class_='products-td').find_all('div', class_='div-wrap')

            break


def get_tomorrow_date():
    return datetime.date.today() + datetime.timedelta(days=1)


def get_url_from_json(key):
    with open('url_info.json') as f:
        json_data = json.load(f)
        return json_data[key]


def get_comic_info_from_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find('div', id='content-inner')


def slack_notify(text, month, day, day_of_week):
    slack_url = get_url_from_json('incoming_webhook_url')
    slack_url.notify(
        f'今日 ( {str(month)}/{str(day)} {str(day_of_week)} ) のマンガ情報', attachments=text)


if __name__ == '__main__':
    main()
