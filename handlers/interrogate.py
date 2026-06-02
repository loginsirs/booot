from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.state import get_user
from data.characters import ALL_CHARACTERS, CHARACTER_INFO

async def interrogate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    if user.interrogations_total <= 0:
        await query.answer("❌ Нет допросов!", show_alert=True)
        return
    
    buttons = [[InlineKeyboardButton(f"🎙 {char}", callback_data=f"int_{char}")] for char in ALL_CHARACTERS]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="menu")])
    
    await query.message.edit_text(
        f"🕵️ *ДОПРОС*\nДоступно: *{user.interrogations_total}*\nВыберите персонажа:",
        reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
    )

async def interrogate_character(update: Update, context: ContextTypes.DEFAULT_TYPE, user, char: str):
    query = update.callback_query
    
    if user.interrogations_total <= 0:
        await query.answer("❌ Нет допросов!"); return
    
    user.interrogations_total -= 1
    user.interrogations_used.append(char)
    user.total_solved += 1
    
    await query.message.edit_text(
        f"🎙 *Допрос: {char}*\n"
        f"Допросов этого персонажа: {user.interrogations_used.count(char)}\n\n"
        f"📋 *Информация:*\n{CHARACTER_INFO[char]}\n\n"
        f"✨ +1 очко (всего: {user.total_solved})\n"
        f"⚠️ Покажите ведущему!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]),
        parse_mode="Markdown"
    )