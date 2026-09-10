from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

ROLES = ["Entry Fragger", "AWPer", "Support", "Lurker", "IGL", "Farqi yo'q"]


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Sherik toping")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🚫 Shikoyat")],
        ],
        resize_keyboard=True,
    )


def confirm_nickname_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="reg_confirm")],
            [InlineKeyboardButton(text="🔁 Qayta kiritish", callback_data="reg_retry")],
        ]
    )


def role_select_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=r, callback_data=f"role:{r}")] for r in ROLES]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def level_range_kb() -> InlineKeyboardMarkup:
    options = [
        ("Faqat mening levelim", "0"),
        ("± 1 daraja", "1"),
        ("± 2 daraja", "2"),
        ("Barcha darajalar", "99"),
    ]
    rows = [[InlineKeyboardButton(text=label, callback_data=f"lvl:{val}")] for label, val in options]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def mic_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎤 Ha, shart", callback_data="mic:1")],
            [InlineKeyboardButton(text="🔇 Farqi yo'q", callback_data="mic:0")],
        ]
    )


def confirm_lobby_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ E'lon qilish", callback_data="lobby_confirm")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="lobby_cancel")],
        ]
    )


def lobby_channel_kb(lobby_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤝 Qo'shilaman", callback_data=f"lobby_join:{lobby_id}")]
        ]
    )


def lobby_owner_kb(lobby_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Lobbi to'ldi", callback_data=f"lobby_close:{lobby_id}")]
        ]
    )


def refresh_profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="profile_refresh")]
        ]
    )
