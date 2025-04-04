# src/main.py
import discord
import openai
from discord.ext import commands

from src.common import SUPPORTED_LANGUAGES, logger
from src.utils import get_env_var

# Set Discord bot token and access permissions
TOKEN = get_env_var("DISCORD_TOKEN")
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")

# Set up OpenAI API
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Set bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(("0.0.0.0", 8080), HealthCheckHandler)
    logger.info("Started health check server on port 8080")
    server.serve_forever()


async def get_introduction_message():
    language_commands = "\n".join(
        [
            f"   • `@translator {lang_code}` - {lang_info['description']} {lang_info['emoji']}"
            for lang_code, lang_info in SUPPORTED_LANGUAGES.items()
        ]
    )

    return (
        "```ini\n[POLYGLOT TRANSLATOR BOT]\n```\n"
        "🌐 **Hello! I'm Polyglot, your AI-powered translator bot!** 🌐\n\n"
        "✨ I specialize in seamless translations between **English** and **Japanese**.\n\n"
        "## **How to Use Me:**\n"
        "① **Reply** to any message you want to translate\n"
        "② Type one of these commands:\n"
        f"{language_commands}\n\n"
        "🔍 **Examples:**\n"
        "> Reply to a Japanese message with `@translator en`\n"
        "> Reply to an English message with `@translator jp`\n\n"
        "💫 Powered by state-of-the-art AI for accurate and natural translations!\n"
        "⭐ I'm here whenever you need language assistance! ⭐\n\n"
        "📝 **Want more languages added?** Please contact Yamato to request additional languages."
    )


@bot.command(name="introduce")
async def introduce_command(ctx):
    """Display bot introduction and usage instructions"""
    try:
        intro_message = await get_introduction_message()
        await ctx.send(intro_message)
        logger.info(
            f"Introduction message sent to {ctx.channel.name} requested by {ctx.author}"
        )
    except Exception as e:
        logger.error(f"Failed to send introduction message: {e}")
        await ctx.send("Sorry, I couldn't display my introduction message.")


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
        target_channel_names = ["discord-test"]
        # target_channel_names = ["novel-translation", "discord-test"]
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
                    intro_message = await get_introduction_message()
                    await channel.send(intro_message)
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
        if not message.reference:
            await message.channel.send(
                "⚠️ **Error**: Please use this command as a reply to the message you want to translate.\n"
                "For example, reply to a message with `@translator en` to translate it to English."
            )
            logger.info(
                f"Translation incorrectly requested by {message.author} without replying to a message."
            )
            return

        command = message.content.strip().split()

        if len(command) <= 1:
            supported_langs = ", ".join(
                [
                    f"'{code}' ({info['name']})"
                    for code, info in SUPPORTED_LANGUAGES.items()
                ]
            )
            await message.channel.send(
                f"⚠️ **Error**: No language specified. Please use the format: `@translator [language code]`\n"
                f"Available language codes: {supported_langs}"
            )
            logger.info(
                f"Translation requested by {message.author} but no language was specified."
            )
            return

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

            if language in SUPPORTED_LANGUAGES:
                async with message.channel.typing():
                    translated_text = await translate_text(original_text, language)
                    thread_name = f"Translation: {language.upper()}"
                    if len(original_text) > 20:
                        thread_name = f"Translation of '{original_text[:20]}...' to {language.upper()}"
                    else:
                        thread_name = (
                            f"Translation of '{original_text}' to {language.upper()}"
                        )
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
                supported_langs = ", ".join(
                    [
                        f"'{code}' ({info['name']})"
                        for code, info in SUPPORTED_LANGUAGES.items()
                    ]
                )
                await message.channel.send(
                    f"Unsupported language code. Supported languages are: {supported_langs}."
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
    if target_language not in SUPPORTED_LANGUAGES:
        return f"Unsupported language code: {target_language}"

    target_lang_name = SUPPORTED_LANGUAGES[target_language]["name"]

    try:
        response = client.chat.completions.create(
            model=get_env_var("OPENAI_AI_MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": f"You are an excellent translator. Please translate the following text to {target_lang_name}. Preserve the original nuance and meaning. Read everything before translating.",
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
        # Run the health check server in a separate thread
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("Failed to log in. Please check if the Discord TOKEN is correct.")
    except Exception as e:
        logger.error(f"An error occurred while starting the bot: {e}")
