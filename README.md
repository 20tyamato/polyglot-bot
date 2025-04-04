# Discord翻訳ボット

このDiscordボットは、Discord上のメッセージをOpenAI APIを使用して英語または日本語に翻訳する機能を提供します。

## 機能

- メッセージに返信して `@translator en` と入力すると、そのメッセージを英語に翻訳します
- メッセージに返信して `@translator jp` と入力すると、そのメッセージを日本語に翻訳します

## セットアップ

1. このリポジトリをクローンします

    ```bash
    git clone <リポジトリURL>
    cd discord-translator-bot
    ```

2. 必要なパッケージをインストールします

    ```bash
    pip install -r requirements.txt
    ```

3. `.env`ファイルを作成し、以下の環境変数を設定します

    ```plain
    DISCORD_TOKEN=あなたのDiscordボットトークン
    OPENAI_API_KEY=あなたのOpenAI APIキー
    ```

4. Discord Developer Portalでボットを作成し、適切な権限を付与します
   - `https://discord.com/developers/applications` にアクセス
   - 新しいアプリケーションを作成
   - 「Bot」タブでボットを作成
   - 「MESSAGE CONTENT INTENT」を有効化
   - ボットトークンを取得し、`.env`ファイルに設定

5. ボットをあなたのサーバーに招待します
   - 「OAuth2」→「URL Generator」を使用
   - スコープとして「bot」を選択
   - 必要な権限（少なくとも「Read Messages/View Channels」と「Send Messages」）を選択
   - 生成されたURLを使用してボットを招待

## 使用方法

1. ボットを起動します

```bash
python src/bot.py
```

1. Discordサーバー内で、翻訳したいメッセージに返信します
2. 返信内容に `@translator en` (英語に翻訳) または `@translator jp` (日本語に翻訳) と入力します
3. ボットが翻訳結果を送信します

## 使用例

1. ユーザー1が「こんにちは、元気ですか？」とメッセージを送信します
2. ユーザー2がそのメッセージに返信し、「@translator en」と入力します
3. ボットが「Hello, how are you?」と翻訳結果を送信します

## トラブルシューティング

- **ボットが反応しない場合**: ボットが正しく起動しているか、適切な権限を持っているか確認してください
- **翻訳エラーが発生する場合**: OpenAI APIキーが正しいか、APIの利用制限に達していないか確認してください
- **「メッセージを読み取る権限がありません」エラー**: ボットに適切な権限が付与されているか確認してください

## 注意事項

- このボットはOpenAI APIを使用しているため、APIの利用料金が発生する場合があります。
- APIキーは厳重に管理し、公開リポジトリにアップロードしないようにしてください。

## ライセンス

MITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
