# MOVIE-BOT
slackに明日の映画情報を出力

## 環境構築
1. リポジトリのclone
    ```
    $ git clone
    $ cd movie-bot
    ```

2. 環境変数の設定
    ```
    $ touch .env
    ```
    .envファイルに下記を追記
    ```
    incoming_webhook_url={incoming webhookのURL}
    target_scraped_url=https://eiga.com/theater/13/130201/3263/ # 好きな映画館の場所のリンク
    toho_reservation_url_without_sakuhin_cd=https://hlo.tohotheater.jp/net/movie/TNPI3060J01.do?sakuhin_cd=
    ```

3. モジュールの追加
    ```
    $ pip install requests
    $ pip install beautifulsoup4
    $ pip install slackweb
    $ pip install python-dotenv
    ```

4. 実行
   ```
   $ python3 movie.py
   ```

## 実行結果
slackの該当チャンネルに下記が表示されます
```
映画タイトル
イメージ画像
公開日と上映時間
明日の公開タイムスケジュール
予約リンク
```