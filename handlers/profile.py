from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import database as db
from faceit_api import get_faceit_player
from keyboards import refresh_profile_kb

router = Router()


def _profile_text(user: dict) -> str:
    role = user.get("role") or "Tanlanmagan"
    mic = "Bor ✅" if user.get("has_mic") else "Yo'q ❌"
    return (
        f"👤 Profilingiz\n\n"
        f"🎮 Faceit nik: {user['faceit_nickname']}\n"
        f"⭐ Level: {user['level']}\n"
        f"📊 Elo: {user['elo']}\n"
        f"🧩 Sevimli rol: {role}\n"
        f"🎤 Mikrofon: {mic}"
    )


@router.message(Command("profile"))
@router.message(F.text == "👤 Profil")
async def show_profile(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("Siz hali ro'yxatdan o'tmagansiz. /start ni bosing.")
        return
    await message.answer(_profile_text(user), reply_markup=refresh_profile_kb())


@router.callback_query(F.data == "profile_refresh")
async def refresh_profile(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Avval ro'yxatdan o'ting: /start", show_alert=True)
        return

    player = await get_faceit_player(user["faceit_nickname"])
    if not player:
        await callback.answer("Faceit'dan ma'lumot olib bo'lmadi.", show_alert=True)
        return

    db.upsert_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        faceit_nickname=player["nickname"],
        faceit_id=player["faceit_id"],
        level=player["level"],
        elo=player["elo"],
    )
    updated = db.get_user(callback.from_user.id)
    await callback.message.edit_text(_profile_text(updated), reply_markup=refresh_profile_kb())
    await callback.answer("Yangilandi ✅")
