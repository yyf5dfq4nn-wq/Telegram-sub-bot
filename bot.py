import os
import datetime
import json
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater, JobQueue

TOKEN = os.environ.get("BOT_TOKEN")
DATA_FILE = "members.json"

bot = Bot(token=TOKEN)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def add_member(update: Update, context):
    user = context.args[0]
    data = load_data()
    now = datetime.date.today().isoformat()
    expiry = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()

    data[user] = {"start": now, "expiry": expiry, "reminded": False}
    save_data(data)
    update.message.reply_text(f"{user} added. Subscription expires {expiry}.")

def paid(update: Update, context):
    user = context.args[0]
    data = load_data()
    if user in data:
        expiry = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        data[user]["expiry"] = expiry
        data[user]["reminded"] = False
        save_data(data)
        update.message.reply_text(f"{user} payment confirmed. New expiry {expiry}.")
    else:
        update.message.reply_text("User not found.")

def check_reminders(context):
    data = load_data()
    today = datetime.date.today()
    for user, info in data.items():
        expiry = datetime.date.fromisoformat(info["expiry"])
        diff = (expiry - today).days
        if diff == 2 and not info.get("reminded"):
            try:
                context.bot.send_message(chat_id=user,
                                         text=f"⚠️ Your subscription expires in 2 days.")
                data[user]["reminded"] = True
            except:
                pass
    save_data(data)

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("add", add_member))
    dispatcher.add_handler(CommandHandler("paid", paid))

    jq = updater.job_queue
    jq.run_daily(check_reminders, time=datetime.time(hour=9, minute=0))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
