from functools import wraps
from traceback import format_exc as err

from pyrogram.errors.exceptions.forbidden_403 import \
    ChatWriteForbidden
from pyrogram.types import Message
from pyrogram import Client as app

from DaisyXMusic.config import SUDO_USERS
from DaisyXMusic.helpers.perms import member_permissions


async def authorised(
    func, subFunc2, client, message, *args, **kwargs
):
    chatID = message.chat.id
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    except Exception as e:
        await message.reply_text(str(e.MESSAGE))
        e = err()
        print(str(e))
    return subFunc2


async def unauthorised(message: Message, permission, subFunc2):
    chatID = message.chat.id
    text = (
        "You don't have the required permission to perform this action."
        + f"\n**Permission:** __{permission}__"
    )
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    return subFunc2


def adminsOnly(permission):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id
            if not message.from_user:
                # For anonymous admins
                if message.sender_chat:
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                        *args,
                        **kwargs,
                    )
                return await unauthorised(
                    message, permission, subFunc2
                )
            # For admins and sudo users
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID)
            if (
                userID not in SUDO_USERS
                and permission not in permissions
            ):
                return await unauthorised(
                    message, permission, subFunc2
                )
            return await authorised(
                func, subFunc2, client, message, *args, **kwargs
            )

        return subFunc2

    return subFunc
