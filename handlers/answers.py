import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.state import get_user
from handlers.menu import update_menu

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if user.waiting_accusation:
        user.waiting_accusation = False
        if user.menu_message_id:
            try:
                await context.bot.delete_message(update.effective_chat.id, user.menu_message_id)
            except:
                pass
            user.menu_message_id = None
        accusation = update.message.text.strip()
        config = context.bot_data["config"]
        culprit = config.get("culprit", "Алексей Владимирович Ковалёв")
        elapsed = time.time() - user.game_start_time if user.game_start_time else 0
        if elapsed < 1:
            await update.message.reply_text("⏱️ *Обвинение пока недоступно.*", parse_mode="Markdown")
            await update_menu(update, context, user)
            return
        if accusation.lower() == culprit.lower():
            # Победная гифка
            try:
                with open("images/victory.gif", "rb") as gif:
                    await update.message.reply_animation(
                        animation=gif,
                        caption="🎉 *Поздравляем!* Вы верно назвали преступника! Дело раскрыто!",
                        parse_mode="Markdown"
                    )
            except:
                await update.message.reply_text(
                    "🎉 *Поздравляем!* Вы верно назвали преступника! Дело раскрыто!",
                    parse_mode="Markdown"
                )

            # Финальный текст развязки
            final_text = (
                "После тщательного расследования правда наконец была раскрыта.\n\n"
                "Выяснилось, что за попыткой незаконной продажи секретного проекта стояли Максим Беляев и вторая личность Алексея Ветрова. "
                "В ходе следствия было установлено, что Алексей долгое время страдал диссоциативным расстройством личности. "
                "Его вторая личность действовала независимо от него, скрывая свои поступки и вступив в сговор с Максимом Беляевым.\n\n"
                "Злоумышленники планировали продать проект конкурентам, чтобы получить крупную сумму денег. "
                "Однако благодаря собранным уликам и работе следственной группы их удалось выследить. "
                "Решающая операция прошла в доме Максима Беляева, где оба были задержаны при подготовке сделки.\n\n"
                "Суд признал Максима Беляева виновным в промышленном шпионаже, мошенничестве и попытке незаконной продажи интеллектуальной собственности компании. "
                "Он был приговорён к длительному сроку лишения свободы.\n\n"
                "Медицинская экспертиза подтвердила, что Алексей Ветров страдает серьёзным психическим расстройством. "
                "Суд постановил направить его на принудительное лечение в специализированное медицинское учреждение.\n\n"
                "Несмотря на произошедшее, компания сумела сохранить проект. "
                "После устранения всех угроз разработка была успешно завершена и представлена инвесторам. "
                "Проект оказался крайне успешным, что привело к значительному росту стоимости акций компании и укреплению её позиций на рынке.\n\n"
                "Дело было закрыто. Тайна раскрыта, виновные понесли наказание, а справедливость восторжествовала."
            )
            await update.message.reply_text(final_text)

            user.game_active = False
        else:
            await update.message.reply_text(
                "❌ *Неверно.* Продолжайте расследование.",
                parse_mode="Markdown"
            )
        await update_menu(update, context, user)
        return

    if not user.waiting_answer:
        return

    text = update.message.text.strip()
    user.waiting_answer = False

    if user.task_message_id:
        try:
            await context.bot.delete_message(update.effective_chat.id, user.task_message_id)
        except:
            pass
        user.task_message_id = None

    correct = False
    ach = ""

    if user.is_code_task:
        if text.lower() == str(user.correct_answer).strip().lower():
            correct = True
            if user._current_task_type == "lore":
                user.solved_lore += 1
                if user.solved_lore >= 2 and not user.evidence_unlocked:
                    user.evidence_unlocked = True
                    ach += "\n🔍 Кнопка 'Улики' появилась в меню!"
    else:
        try:
            if abs(float(text.replace(",", ".")) - user.correct_answer) < 0.01:
                correct = True
                if user._current_task_type == "derivative":
                    user.solved_derivative += 1
                elif user._current_task_type == "logarithm":
                    user.solved_logarithm += 1
                elif user._current_task_type == "combinatorics":
                    user.solved_combinatorics += 1
        except:
            pass

    if not correct:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Попробовать ещё", callback_data="tasks_menu")],
            [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
        ])
        await update.message.reply_text("❌ *Неправильно!*", reply_markup=buttons, parse_mode="Markdown")
        return

    user.total_solved += 1
    user.last_task_type = user._current_task_type

    if user.solved_derivative >= 5 and not user.deriv_bonus_claimed:
        user.deriv_bonus_claimed = True
        user.interrogations_total += 1
        ach += "\n🔓 +1 ДОПРОС! (5/5 производных)"

    if user.solved_logarithm >= 5 and not user.log_bonus_claimed:
        user.log_bonus_claimed = True
        user.interrogations_total += 1
        ach += "\n🔓 +1 ДОПРОС! (5/5 логарифмов)"

    if user.solved_combinatorics >= 2 and not user.safe_unlocked:
        user.safe_unlocked = True
        user.total_solved += 1
        ach += "\n🔓 СЕЙФ ОТКРЫТ! +2 очка"

    completed = False
    if user.last_task_type == "derivative" and user.solved_derivative >= 5:
        completed = True
    elif user.last_task_type == "logarithm" and user.solved_logarithm >= 5:
        completed = True
    elif user.last_task_type == "combinatorics" and user.solved_combinatorics >= 2:
        completed = True
    elif user.last_task_type == "lore" and user.solved_lore >= 2:
        completed = True

    if completed:
        retry_text = "✅ Завершено"
        retry_callback = "tasks_menu"
        style = "success"
    else:
        type_names = {
            "derivative": "производную",
            "logarithm": "логарифм",
            "combinatorics": "комбинаторику",
            "lore": "лор"
        }
        retry_text = f"🔄 Ещё {type_names.get(user.last_task_type, 'задачу')}"
        retry_callback = f"retry_{user.last_task_type}"
        style = "primary"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(retry_text, callback_data=retry_callback, style=style)],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ])
    await update.message.reply_text(
        f"✅ *Правильно!*{ach}\n\n"
        f"✨ Всего решено: *{user.total_solved}*\n"
        f"🕵️ Допросов: *{user.interrogations_total}*",
        reply_markup=buttons,
        parse_mode="Markdown"
    )