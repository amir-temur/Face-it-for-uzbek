import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
from faceit_api import get_faceit_player
from keyboards import confirm_nickname_kb, main_menu_kb

router = Router()
logger = logging.getLogger(__name__)


class RegisterStates(StatesGroup):
    waiting_nickname = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user and user.get("faceit_id"):
        await message.answer(
            f"Salom, {message.from_user.first_name}! Siz allaqachon ro'yxatdan "
            f"o'tgansiz (Faceit: {user['faceit_nickname']}, Level {user['level']}).\n\n"
            "Quyidagi menyudan foydalaning 👇",
            reply_markup=main_menu_kb(),
        )
        return

    await state.set_state(RegisterStates.waiting_nickname)
    await message.answer(
        "👋 Salom! Bu bot Faceit'da CS2 uchun sherik (lobbi) topishga yordam beradi.\n\n"
        "Boshlash uchun o'zingizning Faceit nikingizni yozing:"
    )


@router.message(RegisterStates.waiting_nickname)
async def process_nickname(message: Message, state: FSMContext):
    nickname = message.text.strip()
    await message.answer("⏳ Faceit profilingiz tekshirilmoqda...")

    try:
        player = await get_faceit_player(nickname)
    except RuntimeError as e:
        await message.answer(f"⚠️ Bot sozlamasida xatolik: {e}")
        return

    if not player or player.get("level") is None:
        await message.answer(
            "❌ Bunday nik topilmadi yoki CS2 statistikasi mavjud emas.\n"
            "Nikni tekshirib, qaytadan yuboring:"
        )
        return

    await state.update_data(player=player)
    await message.answer(
        f"✅ Topildi!\n\n"
        f"🎮 Nik: {player['nickname']}\n"
        f"⭐ Level: {player['level']}\n"
        f"📊 Elo: {player['elo']}\n\n"
        "Ma'lumot to'g'rimi?",
        reply_markup=confirm_nickname_kb(),
    )


@router.callback_query(F.data == "reg_retry")
async def retry_nickname(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegisterStates.waiting_nickname)
    await callback.message.answer("Yangi Faceit nikingizni yozing:")
    await callback.answer()


@router.callback_query(F.data == "reg_confirm")
async def confirm_nickname(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    player = data.get("player")
    if not player:
        await callback.answer("Xatolik, qaytadan /start bosing.", show_alert=True)
        return

    db.upsert_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        faceit_nickname=player["nickname"],
        faceit_id=player["faceit_id"],
        level=player["level"],
        elo=player["elo"],
    )
    await state.clear()
    await callback.message.answer(
        "🎉 Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\n"
        "Endi quyidagi menyudan foydalanib sherik topishingiz mumkin 👇",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
