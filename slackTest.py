import slackweb
import json

json_open = open('slack_info.json', 'r')
json_load = json.load(json_open)

attachments = [
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alternative hotel o,ptions*"
                },
                'image_url': 'https://eiga.k-img.com/images/movie/95553/photo/32dcca0a088e09cd/320.jpg?1639527702'
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
    }
]


slack = slackweb.Slack(url=json_load["incoming_webhook_url"])
slack.notify(text="pythonからslackへ通知テスト", attachments=attachments)
