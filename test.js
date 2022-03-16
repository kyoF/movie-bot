let payload = {
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

const pick_up_title_test = () => {
  const targetUrl = "https://eiga.com/theater/13/130201/3263/";
  var html = UrlFetchApp.fetch(targetUrl).getContentText("UTF-8");
  var title = Parser.data(html).from("<title>").to("</title>").build();
  return title;
};

function slack_notify() {
  payload.blocks.push({
    type: "section",
    text: {
      type: "mrkdwn",
      text: pick_up_title_test(),
    },
  });
  var options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(payload),
  };
  UrlFetchApp.fetch(postUrl, options);
}
