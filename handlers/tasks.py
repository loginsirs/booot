from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.state import get_user
from data.tasks import TASK_MAP, get_random_task

async def give_task(update: Update, context: ContextTypes.DEFAULT_TYPE, user, task_type: str):
    query = update.callback_query
    if task_type == "derivative" and user.deriv_bonus_claimed:
        await query.answer("✅ Бонус уже получен!"); return
    if task_type == "logarithm" and user.log_bonus_claimed:
        await query.answer("✅ Бонус уже получен!"); return
    if task_type == "combinatorics" and user.safe_unlocked:
        await query.answer("✅ Сейф уже открыт!"); return
    if task_type == "lore" and user.solved_lore >= 2:
        await query.answer("✅ Все лор-вопросы решены!"); return

    tasks, special = TASK_MAP[task_type]
    task = get_random_task(user, tasks, getattr(user, f"used_{task_type}"))
    user._current_task_type = task_type
    user.waiting_answer = True
    user.is_code_task = (special == "string")

    if user.task_message_id:
        try: await context.bot.delete_message(update.effective_chat.id, user.task_message_id)
        except: pass
        user.task_message_id = None
    if user.menu_message_id:
        try: await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
        except: pass
        user.menu_message_id = None

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В меню", callback_data="menu")]])

    if special == "string":
        user.correct_answer = task[1]
        msg = await update.effective_chat.send_message(
            f"📜 *Вопрос по сюжету:*\n\n{task[0]}\n\nВведи ответ (имя или слово):",
            reply_markup=keyboard, parse_mode="Markdown")
    else:
        user.correct_answer = task[1]
        prefix = "🧮"
        msg = await update.effective_chat.send_message(
            f"{prefix} *Задача:*\n\n{task[0]}\n\nВведи ответ:",
            reply_markup=keyboard, parse_mode="Markdown")
    user.task_message_id = msg.message_id
    await query.answer()