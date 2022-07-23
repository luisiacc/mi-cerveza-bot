import logging

from config import get_config
from db import remove_user, save_user
from job import TheArmagedon
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

allowed_users = ["luisiacc"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello papi")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = update.effective_user.id
    username = update.effective_user.username

    if username not in allowed_users:
        await update.message.reply_text("No tienes permiso para usar este bot, pirate de aqui anda")
        return

    save_user(id)
    await update.message.reply_text("Comienza la salsa")
    for i in range(5):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello")
        time.sleep(1)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remove_user(update.effective_user.id)
    await update.message.reply_text("Bye papi")


token = get_config().get("token", "")

job = TheArmagedon(Bot(token=token))
job.start_the_circus()

app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.run_polling()
