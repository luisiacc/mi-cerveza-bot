import logging
import os

from db import db
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

allowed_users = ["luisiacc", "Demonge"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = update.effective_user.id
    username = update.effective_user.username

    if username not in allowed_users:
        await update.message.reply_text("No tienes permiso para usar este bot, pirate de aqui anda")
        return

    db.add_user(id)
    await update.message.reply_text("Comienza la salsa")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db.remove_user(update.effective_user.id)
    await update.message.reply_text("Bye papi")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hellooooo")


token = os.environ.get("TOKEN")

db.setup()

app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.run_polling()
