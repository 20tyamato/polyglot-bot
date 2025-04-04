# src/main.py

import os

import discord
import openai
from discord.ext import commands

from common import logger

# Discordボットのトークンとアクセス権限の設定
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI APIの設定
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ボットのインテントを設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"{bot.user} としてログインしました")
    activity = discord.Activity(
        type=discord.ActivityType.watching, name="翻訳リクエスト | @translator"
    )
    await bot.change_presence(activity=activity)
    logger.info(f"合計 {len(bot.guilds)} のサーバーで稼働中")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # リファレンスがある（返信である）かつコマンドが含まれているかチェック
    if message.reference and message.content.strip().startswith("@translator"):
        # コマンドの解析
        command = message.content.strip().split()
        if len(command) > 1:
            language = command[1].lower()

            try:
                # 返信先のメッセージを取得
                referenced_message = await message.channel.fetch_message(
                    message.reference.message_id
                )
                original_text = referenced_message.content

                # テキストが空かチェック
                if not original_text:
                    await message.channel.send(
                        "翻訳するテキストが見つかりません。テキストを含むメッセージに返信してください。"
                    )
                    return

                if language in ["en", "jp"]:
                    # 入力中表示
                    async with message.channel.typing():
                        # 翻訳を実行
                        translated_text = await translate_text(original_text, language)

                        # 長いメッセージを分割して送信
                        if len(translated_text) > 2000:
                            chunks = [
                                translated_text[i : i + 2000]
                                for i in range(0, len(translated_text), 2000)
                            ]
                            for i, chunk in enumerate(chunks):
                                if i == 0:
                                    await message.channel.send(
                                        f"翻訳結果 (1/{len(chunks)}):\n{chunk}"
                                    )
                                else:
                                    await message.channel.send(
                                        f"翻訳結果 ({i + 1}/{len(chunks)}):\n{chunk}"
                                    )
                        else:
                            await message.channel.send(f"翻訳結果:\n{translated_text}")
                else:
                    await message.channel.send(
                        "サポートされている言語は 'en'（英語）または 'jp'（日本語）です。"
                    )
            except discord.NotFound:
                await message.channel.send("返信先のメッセージが見つかりませんでした。")
            except discord.Forbidden:
                await message.channel.send("メッセージを読み取る権限がありません。")
            except Exception as e:
                logger.error(f"エラー: {e}")
                await message.channel.send(f"エラーが発生しました: {e}")

    await bot.process_commands(message)


async def translate_text(text, target_language):
    """
    OpenAI APIを使用してテキストを翻訳する関数
    """
    language_map = {"en": "英語", "jp": "日本語"}

    target_lang_name = language_map[target_language]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"あなたは優れた翻訳者です。以下のテキストを{target_lang_name}に翻訳してください。元のニュアンスや意味を保持するよう心がけてください。",
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
    except openai.RateLimitError:
        return (
            "OpenAI APIのレート制限に達しました。しばらく待ってから再試行してください。"
        )
    except openai.APIError as e:
        logger.error(f"OpenAI APIエラー: {e}")
        return f"OpenAI APIエラーが発生しました: {e}"
    except Exception as e:
        logger.error(f"翻訳エラー: {e}")
        return f"翻訳中にエラーが発生しました: {e}"


if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error(
            "ログインに失敗しました。Discord TOKENが正しいか確認してください。"
        )
    except Exception as e:
        logger.error(f"ボットの起動中にエラーが発生しました: {e}")
