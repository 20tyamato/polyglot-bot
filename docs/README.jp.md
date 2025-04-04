# Discord翻訳ボット

- [English](README.md)
- [Japanese](README.jp.md)

## 概要

Polyglotは、OpenAI APIを使用してDiscord上のメッセージを英語と日本語の間でシームレスに翻訳するAI駆動のボットです。ユーザーは翻訳コマンドでメッセージに返信するだけで、Discord内で直接メッセージを翻訳できます。

## 機能

- 英語と日本語の間の迅速な翻訳
- 直感的に使用できる返信ベースのコマンドインターフェース
- 整理された翻訳のためのスレッド作成
- 翻訳テキストの書式保持（太字、斜体、メンション）
- 信頼性のためのヘルスモニタリングシステム

## セットアップ

1. このリポジトリをクローンします

   ```bash
   git clone https://github.com/20tyamato/polyglot-bot.git
   cd polyglot-translator-bot
   ```

2. 必要なパッケージをインストールします

   ```bash
   pip install -r requirements.txt
   ```

3. `.env`ファイルを作成し、以下の環境変数を設定します

   ```plain
   OPENAI_AI_MODEL="gpt-4o-2024-11-20"
   DISCORD_TOKEN=あなたのDiscordボットトークン
   OPENAI_API_KEY=あなたのOpenAI APIキー
   ```

4. Discord Developer Portalでボットを作成します
   - `https://discord.com/developers/applications` にアクセス
   - 新しいアプリケーションを作成
   - 「Bot」タブでボットを作成
   - 「MESSAGE CONTENT INTENT」を有効化
   - ボットトークンを取得し、`.env`ファイルに追加（`.env.example`をテンプレートとして使用）

5. ボットをあなたのサーバーに招待します
   - 「OAuth2」→「URL Generator」を使用
   - スコープとして「bot」を選択
   - 必要な権限を選択:
     - メッセージを読む/チャンネルを見る
     - メッセージを送信
     - 公開スレッドを作成
     - スレッドでメッセージを送信
   - 生成されたURLを使用してボットを招待

## 使用方法

1. ボットを起動します

   ```bash
   python src/main.py
   ```

2. Discordサーバー内で、翻訳したいメッセージに返信します
   - 英語から日本語: `@translator jp`と返信
   - 日本語から英語: `@translator en`と返信

3. ボットが翻訳結果を含むスレッドを作成します

## コマンド一覧

- `@translator en` - 英語に翻訳 🇺🇸🇬🇧
- `@translator jp` - 日本語に翻訳 🇯🇵
- `!introduce` - ボットの紹介と使用方法の説明を表示

## 使用例

1. ユーザー1が「こんにちは、元気ですか？」とメッセージを送信します
2. ユーザー2がそのメッセージに返信し、「@translator en」と入力します
3. ボットが「Hello, how are you?」という翻訳結果を含むスレッドを作成します

## トラブルシューティング

- **ボットが反応しない場合**: ボットが正しく起動しているか、適切な権限を持っているか確認してください
- **翻訳エラーが発生する場合**: OpenAI APIキーが正しいか、APIの利用制限に達していないか確認してください
- **「メッセージを読み取る権限がありません」エラー**: ボットに適切な権限が付与されているか確認してください
- **空の翻訳結果**: OpenAI APIがリクエストを処理できない場合に発生することがあります。後でもう一度お試しください

## 注意事項

- このボットはOpenAI APIを使用しているため、APIの利用料金が発生する場合があります
- APIキーは厳重に管理し、公開リポジトリにアップロードしないようにしてください
- 翻訳には4000文字の制限があります

## ライセンス

MITライセンスの下で公開されています。詳細は[LICENSE](LICENSE.txt)ファイルを参照してください。
