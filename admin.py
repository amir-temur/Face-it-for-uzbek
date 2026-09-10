from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import database as db
from config import ADMIN_IDS

router = Router()


class ReportStates(StatesGroup):
    waiting_target = State()
    waiting_reason = State()


def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


# ---------- Foydalanuvchi: shikoyat qilish ----------

@router.message(F.text == "🚫 Shikoyat")
@router.message(Command("report"))
async def start_report(message: Message, state: FSMContext):
    await state.set_state(ReportStates.waiting_target)
    await message.answer(
        "Shikoyat qilmoqchi bo'lgan o'yinchining Telegram ID raqamini yuboring.\n"
        "(Telegram username emas, raqamli ID kerak — buni e'londagi profildan yoki "
        "@userinfobot orqali bilib olishingiz mumkin.)"
    )


@router.message(ReportStates.waiting_target)
async def report_target(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("Iltimos, faqat raqamli ID yuboring.")
        return
    await state.update_data(reported_id=int(message.text.strip()))
    await state.set_state(ReportStates.waiting_reason)
    await message.answer("Sababini qisqacha yozing (masalan: toksik, aldash va h.k.):")


@router.message(ReportStates.waiting_reason)
async def report_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_report(
        reporter_id=message.from_user.id,
        reported_id=data["reported_id"],
        reason=message.text.strip(),
    )
    await state.clear()
    await message.answer("✅ Shikoyatingiz qabul qilindi, adminlar ko'rib chiqishadi.")


# ---------- Admin buyruqlari ----------

@router.message(Command("block"))
async def cmd_block(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: /block <telegram_id>")
        return
    db.block_user(int(parts[1]))
    await message.answer(f"⛔ {parts[1]} bloklandi.")


@router.message(Command("unblock"))
async def cmd_unblock(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: /unblock <telegram_id>")
        return
    db.unblock_user(int(parts[1]))
    await message.answer(f"✅ {parts[1]} blokdan chiqarildi.")


@router.message(Command("reports"))
async def cmd_reports(message: Message):
    if not is_admin(message.from_user.id):
        return
    reports = db.get_reports()
    if not reports:
        await message.answer("Hozircha shikoyatlar yo'q.")
        return
    lines = [
        f"#{r['id']} | {r['created_at'][:16]} | "
        f"Shikoyatchi: {r['reporter_id']} → Nishon: {r['reported_id']}\n"
        f"Sabab: {r['reason']}"
        for r in reports
    ]
    await message.answer("\n\n".join(lines))
