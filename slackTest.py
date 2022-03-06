import slackweb

slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
slack.notify(text="pythonからslackへ通知テスト")
