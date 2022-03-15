var payload = {
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

function slack_notify() {
  var options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(payload),
  };
  UrlFetchApp.fetch(postUrl, options);
}
