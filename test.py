import requests
from bs4 import BeautifulSoup

# response = requests.get("https://hlo.tohotheater.jp/net/schedule/076/TNPI2000J01.do")
# 画像付き
response = requests.get("https://eiga.com/theater/13/130201/3263/")
soup = BeautifulSoup(response.content, "html.parser")

content_container_info = soup.find_all("div", class_="content-container")
eiga_info = content_container_info[1].find_all("section")

for eiga in eiga_info:
    title = eiga.find("h2", class_="title-xlarge margin-top20").find("a").get_text()
    
