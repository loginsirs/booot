import json
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.menu import start, update_menu
from handlers.tasks import give_task
from handlers.answers import handle_answer
from utils.state import get_user
from data.evidence import EVIDENCE_ITEMS

DEBUG_USER_ID = 0  # заполняется из config.json

async def show_evidence_menu(update: Update, context, user, message=None):
    """Показывает меню улик. Если передан message, редактирует его, иначе создаёт новое."""
    if user.menu_message_id:
        try:
            await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
        except:
            pass
        user.menu_message_id = None

    buttons = []
    for item in EVIDENCE_ITEMS:
        if item["unlocked"](user):
            btn_text = item["name"]
            cb = f"evidence_show_{item['file']}"
        else:
            btn_text = f"??? ({item['hint']})"
            cb = "evidence_none"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=cb, style="primary")])
    buttons.append([InlineKeyboardButton("🔙 В меню", callback_data="menu")])

    if message:
        try:
            await message.edit_text(
                "🕵️‍♂️ *УЛИКИ*\nСобирайте доказательства:",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="Markdown"
            )
            return
        except:
            pass

    msg = await update.effective_chat.send_message(
        "🕵️‍♂️ *УЛИКИ*\nСобирайте доказательства:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )
    user.menu_message_id = msg.message_id

async def button_handler(update: Update, context):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass

    user = get_user(query.from_user.id)
    data = query.data

    if user.task_message_id:
        try:
            await context.bot.delete_message(update.effective_chat.id, user.task_message_id)
        except:
            pass
        user.task_message_id = None

    if data in ["derivative", "logarithm", "combinatorics", "lore"]:
        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None
        await give_task(update, context, user, data)
        return

    if data.startswith("retry_"):
        task_type = data.replace("retry_", "")
        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None
        await give_task(update, context, user, task_type)
        return

    user.waiting_answer = False

    if data == "tasks_menu":
        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None

        d, l, c = user.solved_derivative, user.solved_logarithm, user.solved_combinatorics
        text = (
            f"📝 *ЗАДАЧИ*\n\n"
            f"📐 Производные: {d}/5 {'✅' if d>=5 else f'({5-d} ост.)'}\n"
            f"📊 Логарифмы: {l}/5 {'✅' if l>=5 else f'({5-l} ост.)'}\n"
            f"🔢 Комбинаторики: {c}/2 {'✅' if c>=2 else f'({2-c} ост.)'}\n"
            f"📜 Лор-вопросы: {user.solved_lore}/2 {'✅' if user.solved_lore >= 2 else f'({2 - user.solved_lore} ост.)'}\n\n"
            f"*Выбери задачу:*"
        )
        deriv_text = f"📐 Производная {'✅' if user.solved_derivative >= 5 else ''}"
        log_text = f"📊 Логарифм {'✅' if user.solved_logarithm >= 5 else ''}"
        comb_text = f"🔢 Комбинаторика {'✅' if user.solved_combinatorics >= 2 else ''}"
        lore_text = f"📜 Лор {'✅' if user.solved_lore >= 2 else ''}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(deriv_text, callback_data="derivative",
                                  style="success" if user.solved_derivative >= 5 else "primary")],
            [InlineKeyboardButton(log_text, callback_data="logarithm",
                                  style="success" if user.solved_logarithm >= 5 else "primary")],
            [InlineKeyboardButton(comb_text, callback_data="combinatorics",
                                  style="success" if user.solved_combinatorics >= 2 else "primary")],
            [InlineKeyboardButton(lore_text, callback_data="lore",
                                  style="success" if user.solved_lore >= 2 else "primary")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ])
        try:
            await query.message.delete()
        except:
            pass
        msg = await update.effective_chat.send_message(text, reply_markup=keyboard, parse_mode="Markdown")
        user.menu_message_id = msg.message_id

    elif data == "interrogate":
        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None

        from data.characters import CHARACTERS

        if user.interrogations_total <= 0:
            try:
                await query.message.delete()
            except:
                pass
            msg = await update.effective_chat.send_message(
                "❌ *Нет доступных допросов!*\n\nРешите 5/5 производных или 5/5 логарифмов, чтобы получить допрос.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]),
                parse_mode="Markdown"
            )
            user.menu_message_id = msg.message_id
            return

        buttons = []
        for char in CHARACTERS:
            if user.interrogations_total > 0:
                btn_text = f"🎙 {char}"
                style = "success"
            else:
                btn_text = f"🔒 {char} (нет допросов)"
                style = "danger"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"int_{char}", style=style)])
        buttons.append([InlineKeyboardButton("🔙 В меню", callback_data="menu")])

        try:
            await query.message.delete()
        except:
            pass

        msg = await update.effective_chat.send_message(
            f"🕵️ *ДОПРОС*\n"
            f"Доступно допросов: *{user.interrogations_total}*\n"
            f"Выберите персонажа:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
        user.menu_message_id = msg.message_id

    elif data.startswith("int_"):
        char = data.replace("int_", "")
        from data.characters import CHARACTER_INFO

        if user.interrogations_total <= 0:
            try:
                await query.answer("❌ Нет допросов!")
            except:
                pass
            return

        user.interrogations_total -= 1
        user.interrogations_used.append(char)
        user.total_solved += 1

        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None

        try:
            await query.message.delete()
        except:
            pass

        msg = await update.effective_chat.send_message(
            f"🎙 *Допрос: {char}*\n"
            f"Допросов этого персонажа: {user.interrogations_used.count(char)}\n\n"
            f"📋 *Информация:*\n{CHARACTER_INFO[char]}\n\n"
            f"✨ +1 очко (всего: {user.total_solved})\n"
            f"⚠️ Покажите ведущему!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🕵️ Допросить ещё", callback_data="interrogate")],
                [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
            ]),
            parse_mode="Markdown"
        )
        user.menu_message_id = msg.message_id

    elif data == "accuse":
        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None

        if not user.game_active:
            try:
                await query.message.delete()
            except:
                pass
            msg = await update.effective_chat.send_message(
                "Игра ещё не началась. Напишите /start",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]),
                parse_mode="Markdown")
            user.menu_message_id = msg.message_id
            return
        elapsed = time.time() - user.game_start_time if user.game_start_time else 0
        if elapsed < 3600:
            remaining = 3600 - elapsed
            mins, secs = int(remaining // 60), int(remaining % 60)
            try:
                await query.message.delete()
            except:
                pass
            msg = await update.effective_chat.send_message(
                f"⏱️ *Обвинение будет доступно через {mins:02d}:{secs:02d}.*\nПродолжайте расследование!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]),
                parse_mode="Markdown")
            user.menu_message_id = msg.message_id
            return
        user.waiting_accusation = True
        try:
            await query.message.delete()
        except:
            pass
        msg = await update.effective_chat.send_message(
            "⚖️ *Введите полное имя подозреваемого (Фамилия Имя Отчество):*\nНапример: Алексей Владимирович Ковалёв",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена", callback_data="menu", style="danger")]]),
            parse_mode="Markdown")
        user.menu_message_id = msg.message_id

    elif data == "evidence_menu":
        await show_evidence_menu(update, context, user)

    elif data.startswith("evidence_show_"):
        file_path = data.replace("evidence_show_", "")
        if file_path == "none":
            await query.answer("Эта улика ещё не открыта.", show_alert=True)
        else:
            try:
                caption = ""
                for item in EVIDENCE_ITEMS:
                    if item["file"] == file_path:
                        caption = item.get("caption", "")
                        break
                with open(file_path, "rb") as photo:
                    await update.effective_chat.send_photo(
                        photo=photo,
                        caption=caption if caption else None,
                        parse_mode="Markdown"
                    )
            except:
                await query.answer("❌ Файл не найден.", show_alert=True)
        await show_evidence_menu(update, context, user, message=query.message)
        return

    elif data == "menu":
        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None
        try:
            await query.message.delete()
        except:
            pass
        await update_menu(update, context, user)

async def debug_all(update: Update, context):
    user = get_user(update.effective_user.id)
    config = context.bot_data["config"]
    if update.effective_user.id != config.get("debug_id", 0):
        await update.message.reply_text("❌ Команда только для разработчика.")
        return

    user.solved_derivative = 5
    user.solved_logarithm = 5
    user.solved_combinatorics = 2
    user.solved_lore = 2
    user.solved_code = 5
    user.safe_unlocked = True
    user.safe_opened = True
    user.deriv_bonus_claimed = True
    user.log_bonus_claimed = True
    user.evidence_unlocked = True
    user.interrogations_total = 2
    user.total_solved = 100
    # Сбрасываем таймер: теперь elapsed станет > 3600, обвинение доступно сразу
    user.game_start_time = time.time() - 3601  # 3601 секунда назад – час уже прошёл

    await update.message.reply_text("✅ Все улики, допросы, сейф и задачи разблокированы! Таймер сброшен.")
    await update_menu(update, context, user)

async def menu_command(update: Update, context):
    user = get_user(update.effective_user.id)
    if user.task_message_id:
        try:
            await context.bot.delete_message(update.effective_chat.id, user.task_message_id)
        except:
            pass
    user.task_message_id = None
    user.waiting_answer = False
    try:
        await update.message.delete()
    except:
        pass
    await update_menu(update, context, user)

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    app = Application.builder().token(config["bot_token"]).build()
    app.bot_data["config"] = config

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("debug_all", debug_all))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    print("🕵️ Бот запущен! Debug: /debug_all")
    app.run_polling()

if __name__ == "__main__":
    main()