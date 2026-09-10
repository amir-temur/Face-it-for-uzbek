# Faceit Lobbi Bot (O'zbekiston CS2 hamjamiyati uchun)

Hujjatda tasvirlangan g'oya asosida qurilgan Telegram bot: foydalanuvchilar Faceit
nikini ro'yxatdan o'tkazadi, bot ularning darajasini (level/elo) Faceit API orqali
tekshiradi, so'ng ular kerakli rol/level/mikrofon filtrlari bilan "sherik kerak"
e'lonini kanalga chiqaradi.

## Imkoniyatlar
- `/start` — Faceit nikini kiritib, avtomatik tekshirish va ro'yxatdan o'tish
- `/profile` — saqlangan Faceit ma'lumotini ko'rish va yangilash
- `/find` (yoki "🎮 Sherik toping" tugmasi) — rol, level oralig'i va mikrofon
  bo'yicha filtr tanlab, kanalga e'lon joylash
- E'londagi "🤝 Qo'shilaman" tugmasi bosilganda, e'lon egasiga qo'shiluvchining
  Faceit va Telegram ma'lumoti shaxsiy xabarda yuboriladi
- E'lon egasi "✅ Lobbi to'ldi" tugmasini bossa, kanaldagi post yopiq deb belgilanadi
- Spamning oldini olish uchun cooldown (standart: 15 daqiqada 1 ta e'lon)
- `/report` — toksik/aldovchi o'yinchi haqida shikoyat qoldirish
- `/block`, `/unblock`, `/reports` — faqat adminlar uchun moderatsiya buyruqlari

## O'rnatish
1. Python 3.10+ o'rnatilganiga ishonch hosil qiling.
2. Kutubxonalarni o'rnating:
   ```
   pip install -r requirements.txt
   ```
3. `.env.example` faylidan nusxa oling va `.env` deb saqlang, so'ng qiymatlarni
   to'ldiring:
   - `BOT_TOKEN` — @BotFather dan olinadi
   - `FACEIT_API_KEY` — https://developers.faceit.com saytida "Server-side" (App
     kaliti) yarating
   - `CHANNEL_ID` — e'lonlar chiqadigan kanal yoki guruh ID'si (botni o'sha
     kanalga admin qilib qo'shing va xabar yuborish huquqini bering)
   - `ADMIN_IDS` — botni boshqaradigan adminlarning Telegram ID raqamlari
4. Botni ishga tushiring:
   ```
   python main.py
   ```

## Fayl tuzilishi
```
faceit_lobby_bot/
  config.py          # .env dan sozlamalarni o'qiydi
  database.py         # SQLite: users, lobbies, reports jadvallari
  faceit_api.py        # Faceit Data API bilan ishlash
  keyboards.py         # Inline/reply tugmalar
  handlers/
    registration.py    # /start va Faceit nikini tasdiqlash
    profile.py          # /profile va yangilash
    lobby.py            # /find — e'lon yaratish, qo'shilish, yopish
    admin.py            # /report, /block, /unblock, /reports
  main.py              # botni ishga tushiruvchi fayl
```

## Muhim eslatmalar va keyingi qadamlar
- Bu — ishlaydigan, sinash uchun tayyor asos (MVP). "100% xatosiz" degani —
  hech qanday dastur, jumladan bu ham, real foydalanuvchilar va tarmoq
  sharoitida sinovdan o'tmaguncha to'liq kafolatlanmaydi. Ishga tushirishdan
  oldin o'zingiz test qilib ko'rishingizni tavsiya qilaman.
- Faceit API kaliti — bu shaxsiy (server-side) kalit, uni hech qachon ochiq
  repozitoriyga yoki botga yubormang.
- Hozirgi versiyada guruh ichidagi "thread" (mavzu) funksiyasi va Faceit
  Webhooks integratsiyasi (level o'zgarganda avtomatik yangilash) qo'shilmagan
  — bular hujjatda "ixtiyoriy" deb belgilangan kengaytmalar, keyinroq qo'shish
  mumkin.
- SQLite kichik/o'rta yuklama uchun yetarli; foydalanuvchilar soni juda
  ko'payib ketsa, PostgreSQL'ga o'tish tavsiya etiladi (hujjatda ham shu
  aytilgan).
