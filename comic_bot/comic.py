import requests
from bs4 import BeautifulSoup
import json

def main():
    # target_url = get_url_from_json('scraping_target_url')
    target_url = 'https://calendar.gameiroiro.com/manga.php?year=2022&month=3'
    comics = get_comic_info_from_html(target_url)

def get_url_from_json(key):
    with open('url_info.json') as f:
        json_data = json.load(f)
        return json_data[key]

def get_comic_info_from_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find('div', id='content-inner')

def slack_notify(text):
    slack_url = get_url_from_json('incoming_webhook_url')
    slack_url.notify(f'今日 ( {str(month)}/{str(day)} {str(day_of_week)} ) のマンガ情報', attachments=text)

if __name__ == '__main__':
    main()
