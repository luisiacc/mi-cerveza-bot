import logging
import os

from db import db
from job import TheArmagedon
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

allowed_users = ["luisiacc"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = update.effective_user.id
    username = update.effective_user.username

    if username not in allowed_users:
        await update.message.reply_text("No tienes permiso para usar este bot, pirate de aqui anda")
        return

    db.save_user(id)
    await update.message.reply_text("Comienza la salsa")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db.remove_user(update.effective_user.id)
    await update.message.reply_text("Bye papi")


token = os.environ.get("TOKEN")

job = TheArmagedon(Bot(token=token))
job.start_the_circus()

app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.run_polling()
