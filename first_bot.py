from __future__ import annotations

import discord
from discord.message import Message
import my_token
from twitter_util import TwitterUtil
from ogiri_gen import OgiriGenerator
import asyncio
from datetime import datetime

SCREENSHOT = "/tmp/screenshot.png"

tweets = TwitterUtil()
tweets.load_dumps()

generator = OgiriGenerator()

# 接続に必要なオブジェクトを生成
client = discord.Client()

# メッセージ受信時に動作する処理
@client.event
async def on_message(message: discord.Message):

    if message.author.bot or message.channel.name != my_token.DISCORD_TEST_CHANNEL:
        return

    if not message.mentions or message.mentions[0] != client.user:
        return

    text = message.content

    if "おおぎり" in text:
        await endless_ogiri(message)

    if "おだい" in text:
        await message.reply("ちょっとまってね")
        file = generate_odai_file()
        await message.reply("それっ", file=file)

    if "ののしって" in text:
        await message.reply("ばか！あほ！おたんこなす！")


def generate_odai_file():
    html = tweets.load_random_embed_html()
    generator.gen(html, SCREENSHOT)
    file = discord.File(SCREENSHOT)

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


async def endless_ogiri(message: discord.Message):

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


# Botの起動とDiscordサーバーへの接続
print("動くよ！")
client.run(my_token.DISCORD_TOKEN)

print("止まるよ！")
generator.quit()
