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
    logger.info(f"Running on {len(bot.guilds)} servers")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message is a reply and contains the command
    if message.reference and message.content.strip().startswith("@translator"):
        # Parse the command
        command = message.content.strip().split()
        if len(command) > 1:
            language = command[1].lower()

            try:
                # Get the referenced message
                referenced_message = await message.channel.fetch_message(
                    message.reference.message_id
                )
                original_text = referenced_message.content

                # Check if the text is empty
                if not original_text:
                    await message.channel.send(
                        "No text to translate found. Please reply to a message containing text."
                    )
                    return

                if language in ["en", "jp"]:
                    # Show typing indicator
                    async with message.channel.typing():
                        # Translate the text
                        translated_text = await translate_text(original_text, language)

                        # Split long messages and send them separately
                        if len(translated_text) > 2000:
                            chunks = [
                                translated_text[i : i + 2000]
                                for i in range(0, len(translated_text), 2000)
                            ]
                            for i, chunk in enumerate(chunks):
                                if i == 0:
                                    await message.channel.send(
                                        f"Translation result (1/{len(chunks)}):\n{chunk}"
                                    )
                                else:
                                    await message.channel.send(
                                        f"Translation result ({i + 1}/{len(chunks)}):\n{chunk}"
                                    )
                        else:
                            await message.channel.send(
                                f"Translation result:\n{translated_text}"
                            )
                else:
                    await message.channel.send(
                        "Supported languages are 'en' (English) or 'jp' (Japanese)."
                    )
            except discord.NotFound:
                await message.channel.send("The referenced message was not found.")
            except discord.Forbidden:
                await message.channel.send("I don't have permission to read messages.")
            except Exception as e:
                logger.error(f"Error: {e}")
                await message.channel.send(f"An error occurred: {e}")

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
