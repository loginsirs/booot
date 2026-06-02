import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.state import get_user, get_all_users

def menu_text(user):
    d, l, c = user.solved_derivative, user.solved_logarithm, user.solved_combinatorics
    leaders = get_all_users()
    leaderboard = "🏆 *Таблица лидеров:*\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(leaders[:5]):
        medal = medals[i] if i < 3 else f"{i+1}."
        leaderboard += f"{medal} {u.username}: *{u.total_solved}* очк.\n"

    timer_text = ""
    if user.game_active and user.game_start_time:
        elapsed = time.time() - user.game_start_time
        remaining = max(0, 3600 - elapsed)
        if remaining > 0:
            mins, secs = int(remaining // 60), int(remaining % 60)
            timer_text = f"⏱️ *Осталось времени:* {mins:02d}:{secs:02d}\n\n"
        else:
            timer_text = "⏱️ *Время истекло!*\n\n"

    return (
        f"✨ *Всего решено:* {user.total_solved}\n\n"
        f"📐 Производные: {d}/5 {'✅' if d>=5 else f'({5-d} ост.)'}\n"
        f"📊 Логарифмы: {l}/5 {'✅' if l>=5 else f'({5-l} ост.)'}\n"
        f"🔢 Комбинаторики: {c}/2 {'✅' if c>=2 else f'({2-c} ост.)'}\n"
        f"📜 Лор-вопросы: {user.solved_lore}/2 {'✅' if user.solved_lore >= 2 else f'({2 - user.solved_lore} ост.)'}\n\n"
        f"🕵️ Допросов доступно: *{user.interrogations_total}*\n\n"
        f"{timer_text}"
        f"{leaderboard}\n"
        f"*Выбери действие:*"
    )

def menu_keyboard(user):
    buttons = [
        [InlineKeyboardButton("📝 Задачи", callback_data="tasks_menu", style="primary")],
        [InlineKeyboardButton("🕵️ Допрос", callback_data="interrogate", style="primary")],
        [InlineKeyboardButton("⚖️ Обвинить", callback_data="accuse", style="danger")],
    ]
    if user.evidence_unlocked:
        buttons.insert(2, [InlineKeyboardButton("🕵️‍♂️ Улики", callback_data="evidence_menu", style="primary")])
    return InlineKeyboardMarkup(buttons)

async def update_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    text = menu_text(user)
    keyboard = menu_keyboard(user)
    if user.menu_message_id:
        try:
            await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
        except:
            pass
    msg = await update.effective_chat.send_message(text, reply_markup=keyboard, parse_mode="Markdown")
    user.menu_message_id = msg.message_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or update.effective_user.first_name or "детектив"
    user = get_user(update.effective_user.id, username)
    config = context.bot_data["config"]
    if not user.game_active:
        user.game_start_time = time.time()
        user.game_active = True
    d, l, c = user.solved_derivative, user.solved_logarithm, user.solved_combinatorics
    leaders = get_all_users()
    leaderboard = "🏆 *Таблица лидеров:*\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(leaders[:5]):
        medal = medals[i] if i < 3 else f"{i+1}."
        leaderboard += f"{medal} {u.username}: *{u.total_solved}* очк.\n"
    elapsed = time.time() - user.game_start_time
    remaining = max(0, 3600 - elapsed)
    if remaining > 0:
        mins, secs = int(remaining // 60), int(remaining % 60)
        timer_text = f"⏱️ *Осталось времени:* {mins:02d}:{secs:02d}\n\n"
    else:
        timer_text = "⏱️ *Время истекло!*\n\n"
    text = (
        f"🕵️ *Привет, {username}!*\n\n"
        f"🎭 *Создатели:* {config['creator1']} & {config['creator2']}\n\n"
        f"*Сюжет:*\n"
        f"Вы независимое детективное агентство «Аудит-Контроль», нанятое руководством высокотехнологичной корпорации «Сингулярность». Ночью из охраняемой лаборатории был украден «Проект Эпсилон» революционный алгоритмический код, способный изменить IT-индустрию.\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 *Правила:*\n"
        f"⚠️ Желательно не списывать.\n"
        f"⏱️ У вас ровно 1.5 часа, чтобы найти преступника!\n"
        f"Обвинение можно выдвинуть только после истечения времени.\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ *Твой прогресс:*\n"
        f"Всего решено: {user.total_solved}\n"
        f"📐 Производные: {d}/5 {'✅' if d>=5 else f'({5-d} ост.)'}\n"
        f"📊 Логарифмы: {l}/5 {'✅' if l>=5 else f'({5-l} ост.)'}\n"
        f"🔢 Комбинаторики: {c}/2 {'✅' if c>=2 else f'({2-c} ост.)'}\n"
        f"📜 Лор-вопросы: {user.solved_lore}/2 {'✅' if user.solved_lore >= 2 else f'({2 - user.solved_lore} ост.)'}\n\n"
        f"{timer_text}"
        f"{leaderboard}\n"
        f"*Выбери действие:*"
    )
    msg = await update.message.reply_text(text, reply_markup=menu_keyboard(user), parse_mode="Markdown")
    user.menu_message_id = msg.message_id