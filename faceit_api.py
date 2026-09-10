import aiohttp

from config import FACEIT_API_KEY, FACEIT_GAME_KEY

FACEIT_BASE = "https://open.faceit.com/data/v4"


async def get_faceit_player(nickname: str) -> dict | None:
    """
    Faceit nikini API orqali tekshiradi.
    Topilsa: {"faceit_id", "nickname", "avatar", "level", "elo", "country"}
    Topilmasa yoki xato bo'lsa: None
    """
    if not FACEIT_API_KEY:
        raise RuntimeError(
            "FACEIT_API_KEY sozlanmagan. .env faylida FACEIT_API_KEY ni to'ldiring."
        )

    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    params = {"nickname": nickname}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{FACEIT_BASE}/players", headers=headers, params=params, timeout=10
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

    games = data.get("games", {})
    game_data = games.get(FACEIT_GAME_KEY) or games.get("cs2") or games.get("csgo")
    if not game_data:
        return None

    return {
        "faceit_id": data.get("player_id"),
        "nickname": data.get("nickname"),
        "avatar": data.get("avatar"),
        "level": game_data.get("skill_level"),
        "elo": game_data.get("faceit_elo"),
        "country": data.get("country"),
    }
