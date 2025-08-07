import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import os
import requests
import google.generativeai as genai

app = Flask(__name__)

BOT_TOKEN = os.environ['BOT_TOKEN']
bot = Bot(token=BOT_TOKEN)

genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-2.5-flash')

CITY = "Gevgelija"
COUNTRY_CODE = "MK"

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&units=metric&appid={os.environ['OPENWEATHER_KEY']}"
    resp = requests.get(url).json()
    if 'main' not in resp:
        return "Failed to get weather"
    temp = resp['main']['temp']
    desc = resp['weather'][0]['description']
    return f"Weather in {CITY}: {temp}°C, {desc}"

def summarize_ai(info):
    prompt = f"Summarize this in Macedonian SMS style: {info}"
    response = model.generate_content(prompt)
    return response.text.strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send 'weather' to get weather info.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "weather":
        await update.message.reply_text("Checking weather...")
        weather = get_weather()
        summary = summarize_ai(weather)
        await update.message.reply_text(summary)
    else:
        await update.message.reply_text("Send 'weather' to get weather info.")

# Create Application
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Initialize application once before first request
@app.before_first_request
def initialize_app():
    asyncio.get_event_loop().run_until_complete(application.initialize())

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
