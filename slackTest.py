import slackweb
import json

json_open = open('slack_info.json', 'r')
json_load = json.load(json_open)

slack = slackweb.Slack(url=json_load["incoming_webhook_url"])
slack.notify(text="pythonからslackへ通知テスト")
