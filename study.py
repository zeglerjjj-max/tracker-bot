import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8608575100:AAHh2-GOFZD_MLT25Y1w8wg5lsM557TQRGE"

logging.basicConfig(level=logging.INFO)

users = {}

# ================== CORE ==================

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "time": 0,
            "target": 60,
            "notes": [],
            "xp": 0,
            "level": 1,
            "state": None
        }
    return users[user_id]

def add_xp(user_id, amount):
    user = get_user(user_id)
    user["xp"] += amount

    while user["xp"] >= user["level"] * 100:
        user["xp"] -= user["level"] * 100
        user["level"] += 1

# ================== UI ==================

def main_menu():
    keyboard = [
        ["📚 Belajar", "📊 Statistik"],
        ["👤 Profil", "📝 Catatan"],
        ["🎯 Target"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================== START ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)

    await update.message.reply_text(
        "📚 *Tracker Belajar*\n\nPilih menu di bawah:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ================== MAIN HANDLER ==================

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    text = update.message.text

    # ===== MENU =====
    if text == "📚 Belajar":
        user["state"] = "study"
        await update.message.reply_text("Masukkan durasi belajar (menit):")
        return

    elif text == "📊 Statistik":
        await update.message.reply_text(
            f"📊 Statistik\n⏱ Total: {user['time']} menit\n🎯 Target: {user['target']} menit"
        )
        return

    elif text == "👤 Profil":
        xp_needed = user["level"] * 100
        await update.message.reply_text(
            f"👤 Profil\n\n🏆 Level: {user['level']}\n⭐ XP: {user['xp']} / {xp_needed}\n⏱ Total: {user['time']} menit"
        )
        return

    elif text == "📝 Catatan":
        user["state"] = "note"
        await update.message.reply_text("Kirim catatan belajar:")
        return

    elif text == "🎯 Target":
        user["state"] = "target"
        await update.message.reply_text("Masukkan target (menit):")
        return

    # ===== INPUT =====
    if user["state"] == "study":
        if text.isdigit():
            minutes = int(text)
            user["time"] += minutes

            xp = minutes * 2
            add_xp(user_id, xp)

            await update.message.reply_text(
                f"✅ Belajar {minutes} menit\n⭐ +{xp} XP",
                reply_markup=main_menu()
            )
            user["state"] = None
        else:
            await update.message.reply_text("❌ Masukkan angka!")
        return

    elif user["state"] == "target":
        if text.isdigit():
            user["target"] = int(text)
            await update.message.reply_text(
                f"🎯 Target disimpan: {text} menit",
                reply_markup=main_menu()
            )
            user["state"] = None
        else:
            await update.message.reply_text("❌ Masukkan angka!")
        return

    elif user["state"] == "note":
        user["notes"].append(text)
        await update.message.reply_text(
            "📝 Catatan disimpan!",
            reply_markup=main_menu()
        )
        user["state"] = None
        return

    # ===== FALLBACK =====
    await update.message.reply_text(
        "Pilih menu dulu ya 👇",
        reply_markup=main_menu()
    )

# ================== MAIN ==================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()