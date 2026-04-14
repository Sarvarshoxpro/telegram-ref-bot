import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiosqlite

TOKEN = os.getenv("8678480649:AAH24bm4SEOZ1dpJT-3UjKcF6v4g2VneCys")
GROUP_ID = -3739344843
ADMIN_ID = 8024670294  # o'zingni ID

bot = Bot(8678480649:AAH24bm4SEOZ1dpJT-3UjKcF6v4g2VneCys)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# DATABASE
async def init_db():
    async with aiosqlite.connect("db.sqlite3") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            referrer INTEGER,
            referrals INTEGER DEFAULT 0
        )
        """)
        await db.commit()

# CHECK USER VALID
async def is_valid_user(user: types.User):
    if not user.username:
        return False
    return True

# START
@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    user_id = user.id
    username = user.username
    args = message.text.split()

    if not await is_valid_user(user):
        await message.answer("❌ Username qo‘ying (@username) keyin qatnashing.")
        return

    async with aiosqlite.connect("db.sqlite3") as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        existing = await cursor.fetchone()

        if not existing:
            referrer = None

            if len(args) > 1:
                referrer = int(args[1])
                if referrer == user_id:
                    referrer = None

            await db.execute(
                "INSERT INTO users (user_id, username, referrer) VALUES (?, ?, ?)",
                (user_id, username, referrer)
            )

            # faqat guruhda bo‘lsa
            try:
                member = await bot.get_chat_member(GROUP_ID, user_id)
                if member.status in ["member", "administrator", "creator"]:
                    if referrer:
                        await db.execute(
                            "UPDATE users SET referrals = referrals + 1 WHERE user_id=?",
                            (referrer,)
                        )
            except:
                pass

            await db.commit()

    link = f"https://t.me/{(await bot.get_me()).username}?start={user_id}"

    await message.answer(
        f"👋 Salom @{username}\n\n"
        f"🔗 Sening referal linking:\n{link}\n\n"
        f"📊 Odamlar guruhga kirsa hisoblanadi!"
    )

# TOP
@dp.message(Command("top"))
async def top(message: types.Message):
    async with aiosqlite.connect("db.sqlite3") as db:
        cursor = await db.execute(
            "SELECT username, referrals FROM users ORDER BY referrals DESC LIMIT 10"
        )
        users = await cursor.fetchall()

    text = "🏆 TOP 10:\n\n"
    for i, (username, ref) in enumerate(users, 1):
        text += f"{i}. @{username} — {ref} ta\n"

    await message.answer(text)

# WINNER
@dp.message(Command("winner"))
async def winner(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    async with aiosqlite.connect("db.sqlite3") as db:
        cursor = await db.execute(
            "SELECT username, referrals FROM users ORDER BY referrals DESC LIMIT 3"
        )
        winners = await cursor.fetchall()

    text = "🏆 G‘OLIBLAR:\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (username, ref) in enumerate(winners):
        text += f"{medals[i]} @{username} — {ref} ta\n"

    await message.answer(text)

# RESET
@dp.message(Command("reset"))
async def reset(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    async with aiosqlite.connect("db.sqlite3") as db:
        await db.execute("DELETE FROM users")
        await db.commit()

    await message.answer("✅ Baza tozalandi")

# CHECK LEFT USERS
async def check_members():
    while True:
        async with aiosqlite.connect("db.sqlite3") as db:
            cursor = await db.execute("SELECT user_id, referrer FROM users WHERE referrer IS NOT NULL")
            users = await cursor.fetchall()

            for user_id, referrer in users:
                try:
                    member = await bot.get_chat_member(GROUP_ID, user_id)
                    if member.status == "left":
                        await db.execute("UPDATE users SET referrer=NULL WHERE user_id=?", (user_id,))
                        await db.execute("UPDATE users SET referrals = referrals - 1 WHERE user_id=?", (referrer,))
                except:
                    pass

            await db.commit()

        await asyncio.sleep(300)

# RUN
async def main():
    await init_db()
    asyncio.create_task(check_members())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
