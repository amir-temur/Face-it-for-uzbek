import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
from config import CHANNEL_ID, LOBBY_COOLDOWN_MINUTES
from keyboards import (
    role_select_kb,
    level_range_kb,
    mic_kb,
    confirm_lobby_kb,
    lobby_channel_kb,
    lobby_owner_kb,
    main_menu_kb,
)

router = Router()
logger = logging.getLogger(__name__)


class LobbyStates(StatesGroup):
    choosing_role = State()
    choosing_level_range = State()
    choosing_mic = State()
    confirming = State()


@router.message(Command("find"))
@router.message(F.text == "🎮 Sherik toping")
async def start_lobby(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("Avval ro'yxatdan o'ting: /start")
        return
    if db.is_blocked(message.from_user.id):
        await message.answer("⛔ Siz bloklangansiz, e'lon bera olmaysiz.")
        return
    if not db.can_create_lobby(message.from_user.id):
        await message.answer(
            f"⏳ Siz yaqinda e'lon berdingiz. Har {LOBBY_COOLDOWN_MINUTES} daqiqada "
            "faqat bitta e'lon berish mumkin (spamning oldini olish uchun)."
        )
        return

    await state.set_state(LobbyStates.choosing_role)
    await message.answer(
        "Sizga qaysi rolda o'yinchi kerak?", reply_markup=role_select_kb()
    )


@router.callback_query(LobbyStates.choosing_role, F.data.startswith("role:"))
async def choose_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":", 1)[1]
    await state.update_data(role_needed=role)
    await state.set_state(LobbyStates.choosing_level_range)
    await callback.message.edit_text(
        "Qanday darajadagi (level) o'yinchilar bilan o'ynashni istaysiz?",
    )
    await callback.message.answer("Tanlang:", reply_markup=level_range_kb())
    await callback.answer()


@router.callback_query(LobbyStates.choosing_level_range, F.data.startswith("lvl:"))
async def choose_level(callback: CallbackQuery, state: FSMContext):
    spread = int(callback.data.split(":", 1)[1])
    user = db.get_user(callback.from_user.id)
    my_level = user["level"]

    if spread >= 99:
        level_min, level_max = 1, 10
    else:
        level_min = max(1, my_level - spread)
        level_max = min(10, my_level + spread)

    await state.update_data(level_min=level_min, level_max=level_max)
    await state.set_state(LobbyStates.choosing_mic)
    await callback.message.edit_text(f"Level oralig'i: {level_min}–{level_max}")
    await callback.message.answer("Mikrofon shartmi?", reply_markup=mic_kb())
    await callback.answer()


@router.callback_query(LobbyStates.choosing_mic, F.data.startswith("mic:"))
async def choose_mic(callback: CallbackQuery, state: FSMContext):
    mic_required = callback.data.split(":", 1)[1] == "1"
    await state.update_data(mic_required=mic_required)
    data = await state.get_data()
    user = db.get_user(callback.from_user.id)

    preview = (
        f"📋 E'lon ko'rinishi:\n\n"
        f"🎮 {user['faceit_nickname']} (Level {user['level']}, {user['elo']} Elo)\n"
        f"🧩 Kerakli rol: {data['role_needed']}\n"
        f"⭐ Level oralig'i: {data['level_min']}–{data['level_max']}\n"
        f"🎤 Mikrofon: {'Shart' if mic_required else 'Farqi yo\u2019q'}"
    )
    await state.set_state(LobbyStates.confirming)
    await callback.message.edit_text(preview)
    await callback.message.answer("E'lon qilaymi?", reply_markup=confirm_lobby_kb())
    await callback.answer()


@router.callback_query(LobbyStates.confirming, F.data == "lobby_cancel")
async def cancel_lobby(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Bekor qilindi.")
    await callback.answer()


@router.callback_query(LobbyStates.confirming, F.data == "lobby_confirm")
async def confirm_lobby(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = db.get_user(callback.from_user.id)

    if not db.can_create_lobby(callback.from_user.id):
        await callback.answer("Cooldown vaqti tugamadi.", show_alert=True)
        await state.clear()
        return

    lobby_id = db.create_lobby(
        owner_id=callback.from_user.id,
        level_min=data["level_min"],
        level_max=data["level_max"],
        role_needed=data["role_needed"],
        mic_required=data["mic_required"],
    )

    mention = f"@{callback.from_user.username}" if callback.from_user.username else user["faceit_nickname"]
    post_text = (
        f"🆕 Yangi sherik qidiruvi!\n\n"
        f"🎮 Faceit: {user['faceit_nickname']} (Level {user['level']}, {user['elo']} Elo)\n"
        f"🧩 Kerakli rol: {data['role_needed']}\n"
        f"⭐ Level oralig'i: {data['level_min']}–{data['level_max']}\n"
        f"🎤 Mikrofon: {'Shart' if data['mic_required'] else 'Farqi yo\u2019q'}\n"
        f"👤 Bog'lanish: {mention}"
    )

    if not CHANNEL_ID:
        await callback.message.edit_text(
            "⚠️ CHANNEL_ID sozlanmagan, e'lon faqat sizga ko'rsatildi:\n\n" + post_text
        )
        await state.clear()
        await callback.answer()
        return

    sent = await bot.send_message(CHANNEL_ID, post_text, reply_markup=lobby_channel_kb(lobby_id))
    db.set_lobby_message(lobby_id, str(CHANNEL_ID), sent.message_id)

    await callback.message.edit_text("✅ E'loningiz kanalga joylandi!")
    await callback.message.answer(
        "Odam topilgach yoki lobbi to'lgach, quyidagi tugmani bosing:",
        reply_markup=lobby_owner_kb(lobby_id),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("lobby_join:"))
async def join_lobby(callback: CallbackQuery, bot: Bot):
    lobby_id = int(callback.data.split(":", 1)[1])
    lobby = db.get_lobby(lobby_id)

    if not lobby or lobby["status"] != "active":
        await callback.answer("Bu lobbi endi faol emas.", show_alert=True)
        return

    if db.is_blocked(callback.from_user.id):
        await callback.answer("Siz bloklangansiz.", show_alert=True)
        return

    joiner = db.get_user(callback.from_user.id)
    if not joiner:
        await callback.answer("Avval botda /start orqali ro'yxatdan o'ting.", show_alert=True)
        return

    owner_id = lobby["owner_id"]
    mention = f"@{callback.from_user.username}" if callback.from_user.username else joiner["faceit_nickname"]
    try:
        await bot.send_message(
            owner_id,
            f"🤝 Sizning e'loningizga qo'shilmoqchi:\n\n"
            f"🎮 {joiner['faceit_nickname']} (Level {joiner['level']}, {joiner['elo']} Elo)\n"
            f"👤 {mention}",
        )
        await callback.answer("So'rovingiz e'lon egasiga yuborildi!", show_alert=True)
    except Exception:
        logger.exception("Failed to notify lobby owner")
        await callback.answer("Xabar yuborib bo'lmadi, keyinroq urinib ko'ring.", show_alert=True)


@router.callback_query(F.data.startswith("lobby_close:"))
async def close_lobby(callback: CallbackQuery, bot: Bot):
    lobby_id = int(callback.data.split(":", 1)[1])
    lobby = db.get_lobby(lobby_id)

    if not lobby:
        await callback.answer("Lobbi topilmadi.", show_alert=True)
        return
    if lobby["owner_id"] != callback.from_user.id:
        await callback.answer("Bu sizning e'loningiz emas.", show_alert=True)
        return

    db.close_lobby(lobby_id)

    if lobby["chat_id"] and lobby["message_id"]:
        try:
            await bot.edit_message_text(
                chat_id=lobby["chat_id"],
                message_id=lobby["message_id"],
                text="✅ Lobbi to'ldi / yopildi.",
            )
        except Exception:
            logger.exception("Failed to edit channel message on close")

    await callback.message.edit_text("Lobbi yopildi. Omad tilaymiz! 🎯")
    await callback.answer()
