# src/main.py
import os

import discord
import openai
from discord.ext import commands

from common import logger

# Set Discord bot token and access permissions
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Set bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    activity = discord.Activity(
        type=discord.ActivityType.watching, name="translation requests | @translator"
    )
    await bot.change_presence(activity=activity)
    if len(bot.guilds) > 1:
        logger.info(f"Running on {len(bot.guilds)} servers")
    else:
        logger.info(f"Running on {len(bot.guilds)} server")

    for guild in bot.guilds:
        # target_channel_names = ["discord-test", "novel-translation"]
        target_channel_names = ["discord-test"]
        target_channels = []

        for channel_name in target_channel_names:
            channel = discord.utils.get(
                guild.channels, name=channel_name, type=discord.ChannelType.text
            )
            if channel and channel.permissions_for(guild.me).send_messages:
                target_channels.append(channel)
        if target_channels:
            for channel in target_channels:
                try:
                    await channel.send(
                        "```ini\n[POLYGLOT TRANSLATOR BOT]\n```\n"
                        "🌐 **Hello! I'm Polyglot, your AI-powered translator bot!** 🌐\n\n"
                        "✨ I specialize in seamless translations between **English** and **Japanese**.\n\n"
                        "## **How to Use Me:**\n"
                        "① **Reply** to any message you want to translate\n"
                        "② Type one of these commands:\n"
                        "   • `@translator en` - to translate to English 🇬🇧\n"
                        "   • `@translator jp` - to translate to Japanese 🇯🇵\n\n"
                        "🔍 **Examples:**\n"
                        "> Reply to a Japanese message with `@translator en`\n"
                        "> Reply to an English message with `@translator jp`\n\n"
                        "💫 Powered by state-of-the-art AI for accurate and natural translations!\n"
                        "⭐ I'm here whenever you need language assistance! ⭐"
                    )
                    logger.info(
                        f"Sent introduction message to {channel.name} in {guild.name}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send introduction message to {channel.name} in {guild.name}: {e}"
                    )
        else:
            logger.info(
                f"No target channels found in {guild.name} with the specified names."
            )


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.reference and message.content.strip().startswith("@translator"):
        command = message.content.strip().split()
        if len(command) > 1:
            language = command[1].lower()

            try:
                referenced_message = await message.channel.fetch_message(
                    message.reference.message_id
                )
                original_text = referenced_message.content
                if not original_text:
                    await message.channel.send(
                        "No text to translate found. Please reply to a message containing text."
                    )
                    return

                if language in ["en", "jp"]:
                    async with message.channel.typing():
                        translated_text = await translate_text(original_text, language)
                        thread_name = f"Translation: {language.upper()}"
                        if len(original_text) > 20:
                            thread_name = f"Translation of '{original_text[:20]}...' to {language.upper()}"
                        else:
                            thread_name = f"Translation of '{original_text}' to {language.upper()}"
                        thread = await message.create_thread(name=thread_name)
                        if len(translated_text) > 2000:
                            chunks = [
                                translated_text[i : i + 2000]
                                for i in range(0, len(translated_text), 2000)
                            ]
                            for i, chunk in enumerate(chunks):
                                if i == 0:
                                    await thread.send(
                                        f"Translation result (1/{len(chunks)}):\n{chunk}"
                                    )
                                else:
                                    await thread.send(
                                        f"Translation result ({i + 1}/{len(chunks)}):\n{chunk}"
                                    )
                            logger.info(
                                f"Translation requested by {message.author} and sent successfully in a thread."
                            )
                        else:
                            await thread.send(f"Translation result:\n{translated_text}")
                            logger.info(
                                f"Translation requested by {message.author} and sent successfully in a thread."
                            )
                else:
                    await message.channel.send(
                        "Supported languages are 'en' (English) or 'jp' (Japanese)."
                    )
            except discord.NotFound:
                await message.channel.send("The referenced message was not found.")
                logger.info(
                    f"Translation requested by {message.author} but the referenced message was not found."
                )
            except discord.Forbidden:
                await message.channel.send("I don't have permission to read messages.")
                logger.info(
                    f"Translation requested by {message.author} but I don't have permission to read messages."
                )
            except Exception as e:
                logger.error(f"Error: {e}")
                await message.channel.send(f"An error occurred: {e}")
                logger.info(
                    f"Translation requested by {message.author} but an error occurred: {e}"
                )
    await bot.process_commands(message)


async def translate_text(text, target_language):
    """
    Function to translate text using the OpenAI API
    """
    language_map = {"en": "English", "jp": "Japanese"}

    target_lang_name = language_map[target_language]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an excellent translator. Please translate the following text to {target_lang_name}. Preserve the original nuance and meaning.",
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
    except openai.RateLimitError:
        return "OpenAI API rate limit reached. Please try again later."
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return f"An OpenAI API error occurred: {e}"
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return f"An error occurred during translation: {e}"


if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("Failed to log in. Please check if the Discord TOKEN is correct.")
    except Exception as e:
        logger.error(f"An error occurred while starting the bot: {e}")
