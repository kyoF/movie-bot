import requests
from bs4 import BeautifulSoup

response = requests.get("https://hlo.tohotheater.jp/net/schedule/076/TNPI2000J01.do")
# 画像付き
# response = requests.get("https://eiga.com/theater/13/130201/3263/")
soup = BeautifulSoup(response.content, "html.parser")
title = soup.find("title").get_text()
print(title)