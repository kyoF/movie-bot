function movieBot() {
  const incommingWebhookUrl = "incomming webhookのURL";
  const targetUrl = "https://eiga.com/theater/13/130201/3263/";
  const toho =
    "https://hlo.tohotheater.jp/net/movie/TNPI3060J01.do?sakuhin_cd=";
  const payload = {
    unfurl_links: false,
    username: "MOVIE BOT",
    icon_emoji: ":movie_camera:",
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: "映画情報テスト",
        },
      },
    ],
  };
  const html = UrlFetchApp.fetch(targetUrl).getContentText("UTF-8");

  // タイトルを取得
  const title = pickUpTitleTest(html);
  // titleをslackフォーマットのテキストに格納
  payload.blocks.push(outputTextFormOfSlack(title));
  // slackに通知
  slackNotify(incommingWebhookUrl, payload);
}

const pickUpTitleTest = (html) =>
  Parser.data(html).from("<title>").to("</title>").build();

const outputTextFormOfSlack = (title) => {
  return {
    type: "section",
    text: {
      type: "mrkdwn",
      text: title,
    },
  };
};

const slackNotify = (incommingWebhookUrl, payload) => {
  const options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(payload),
  };
  UrlFetchApp.fetch(incommingWebhookUrl, options);
};
