from __future__ import annotations

import discord
from discord.message import Message
import asyncio
from datetime import datetime
from twitter_util import TwitterUtil
from ogiri_gen import OgiriGenerator
from io import BytesIO
from os import getenv

SELENIUM_REMOTE_URL = getenv("SELENIUM_REMOTE_URL")

tweets = TwitterUtil()
tweets.load_dumps()

generator = (
    OgiriGenerator.new_by_remote(SELENIUM_REMOTE_URL)
    if SELENIUM_REMOTE_URL
    else OgiriGenerator.new_by_local()
)


def generate_odai_file():
    begin_dt = datetime.now()

    html = tweets.load_random_embed_html()
    png = generator.gen(html)
    file = discord.File(BytesIO(png), filename="odai.png")

    print(datetime.now() - begin_dt)

    return file


async def load_presented_replys(
    odai: Message, deadline: datetime
) -> list[tuple[Message, int]]:

    channel: discord.TextChannel = odai.channel
    presents: list[Message] = []

    async for message in channel.history(after=odai.created_at, before=deadline):
        if (
            not message.author.bot
            and message.reference
            and message.reference.message_id == odai.id
        ):
            presents.append((message, sum(r.count for r in message.reactions)))

    presents.sort(key=lambda m: m[1])
    presents.reverse()

    return presents


async def ogiri_taikai(message: Message):

    await message.reply("準備するよ、ちょっとまってね")
    channel: discord.TextChannel = message.channel

    file = generate_odai_file()
    odai: Message = await channel.send("大喜利大会はーじまーるよー！今回のお題はこちら！", file=file)
    await channel.send(
        "制限時間は7分、お題の発言↑に返信して発表してね！\n投票は各発表にリアクションをつけてね！一番多い人の勝ち！それじゃあ始め！"
    )

    await asyncio.sleep(60 * 7)
    deadline: Message = await channel.send("そこまで！\n今から3分間は投票タイム！各発表にリアクションをつけてね！")

    await asyncio.sleep(60 * 3)
    await channel.send("結果発表ぉぉぉぉぉ！")

    presents = await load_presented_replys(odai, deadline.created_at)

    for (i, (pres, reactions)) in enumerate(presents[:3], 1):
        await channel.send(
            f"{i}位: {pres.author.mention} 「{pres.content}」\n\t{pres.jump_url}"
        )

    await channel.send("以上、閉会！ご参加ありがとうございました！")
