import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from MoonXMusic import app
from MoonXMusic.misc import _boot_
from MoonXMusic.plugins.sudo.sudoers import sudoers_list
from MoonXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from MoonXMusic.utils.decorators.language import LanguageStart
from MoonXMusic.utils.formatters import get_readable_time
from MoonXMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string
from config import START_IMG_URL, SUPPORT_CHAT, OWNER_ID

# Buttons
buttons = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            text="➕ Add Me",
            url=f"https://t.me/{app.username}?startgroup=true",
        )
    ],
    [InlineKeyboardButton(text="⚙️ Settings", url="https://t.me/{app.username}?startgroup=true")],
    [
        InlineKeyboardButton(text="👤 Owner", url="https://t.me/{app.username}?startgroup=true"),
        InlineKeyboardButton(text="💬 Support", url="https://t.me/{app.username}?startgroup=true"),
    ],
    [
        InlineKeyboardButton(text="🌐 Language", url="https://t.me/{app.username}?startgroup=true"),
    ],
])


@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = InlineKeyboardMarkup(help_pannel(_))
            return await message.reply_photo(
                photo=START_IMG_URL,
                caption=_["help_1"].format(SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} just started the bot to check sudo list.\n\nUser ID: <code>{message.from_user.id}</code>\nUsername: @{message.from_user.username or 'None'}",
                )
            return

        elif name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "", 1)
            results = VideosSearch(f"https://www.youtube.com/watch?v={query}", limit=1)
            video = (await results.next())["result"][0]

            title = video["title"]
            duration = video["duration"]
            views = video["viewCount"]["short"]
            thumbnail = video["thumbnails"][0]["url"].split("?")[0]
            channellink = video["channel"]["link"]
            channel = video["channel"]["name"]
            link = video["link"]
            published = video["publishedTime"]

            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text=_["S_B_8"], url=link),
                    InlineKeyboardButton(text=_["S_B_9"], url=SUPPORT_CHAT),
                ],
            ])
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} started the bot to check track info.\n\nUser ID: <code>{message.from_user.id}</code>\nUsername: @{message.from_user.username or 'None'}",
                )
            return

    await message.reply_photo(
        photo=START_IMG_URL,
        caption="👋 Welcome to the bot!",
        reply_markup=buttons,
    )

    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOGGER_ID,
            text=f"{message.from_user.mention} just started the bot.\n\nUser ID: <code>{message.from_user.id}</code>\nUsername: @{message.from_user.username or 'None'}",
        )


@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = InlineKeyboardMarkup(start_panel(_))
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=out,
    )
    await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    await app.leave_chat(message.chat.id)
                    return

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    await app.leave_chat(message.chat.id)
                    return

                out = InlineKeyboardMarkup(start_panel(_))
                await message.reply_photo(
                    photo=START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=out,
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
