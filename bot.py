from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

import requests
import google.generativeai as genai

app = Flask(__name__)

BOT_TOKEN = "8237322664:AAHR6KACOcvbdCfRVNADDm1wnTy5HjHaWVE_BOT_TOKEN"
bot = telegram.Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Gemini setup
genai.configure(api_key="AIzaSyDc3OcW5hh8LxgSQ9JZd4q4VlehVJqDnbY")
model = genai.GenerativeModel('gemini-2.5-flash')

CITY = "Gevgelija"
COUNTRY_CODE = "MK"

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&units=metric&appid=0b5942798413f81e19a38cb8838001e1"
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

def start(update, context):
    update.message.reply_text("Hi! Send 'weather' to get weather info.")

def handle_message(update, context):
    text = update.message.text.lower()
    if text == "weather":
        update.message.reply_text("Checking weather...")
        weather = get_weather()
        summary = summarize_ai(weather)
        update.message.reply_text(summary)
    else:
        update.message.reply_text("Send 'weather' to get weather info.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    # On Render, bind to 0.0.0.0 and port from env var PORT
    import os
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
