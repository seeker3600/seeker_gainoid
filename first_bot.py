from __future__ import annotations

import discord
from discord.member import Member
from discord.message import Message
from twitter_util import TwitterUtil
from ogiri_gen import OgiriGenerator
import asyncio
from datetime import datetime
import random
from io import BytesIO
from os import getenv

DISCORD_TOKEN = getenv("DISCORD_TOKEN")
DISCORD_TARGET_CHANNELS = getenv("DISCORD_TARGET_CHANNELS").split()
SELENIUM_REMOTE_URL = getenv("SELENIUM_REMOTE_URL")

tweets = TwitterUtil()
tweets.load_dumps()

generator = (
    OgiriGenerator.new_by_remote(SELENIUM_REMOTE_URL)
    if SELENIUM_REMOTE_URL
    else OgiriGenerator.new_by_local()
)

# 接続に必要なオブジェクトを生成
client = discord.Client()

# メッセージ受信時に動作する処理
@client.event
async def on_message(message: discord.Message):

    if message.author.bot or not message.channel.name in DISCORD_TARGET_CHANNELS:
        return

    bot_member: Member = await message.guild.fetch_member(client.user.id)
    a = set(r for r in bot_member.roles if r.is_bot_managed())
    b = set(r for r in message.role_mentions if r.is_bot_managed())

    # ユーザでもロールでもメンションが無い
    if not client.user in message.mentions and not a & b:
        return

    text = message.content

    if "おおぎり" in text:
        await endless_ogiri(message)

    elif "おだい" in text:
        await message.reply("ちょっとまってね")
        file = generate_odai_file()
        await message.reply("それっ", file=file)

    elif "ののしって" in text:
        vocabulary = [
            "あーもうこの鈍感！",
            "ばか！あほ！おたんこなす！",
            "すかたん！こんこんちきのすっとこどっこい！",
            "えっとえっと、あんぽんたん！",
            "お、おとといきやがれ！",
        ]
        idx = random.randrange(len(vocabulary))
        rep = await message.reply(vocabulary[idx])

        if idx == 0:
            await asyncio.sleep(2)
            rep2 = await message.channel.send("あっ")
            await asyncio.sleep(2)

            retry_msg = vocabulary[random.randrange(1, len(vocabulary))]
            await rep.edit(content=retry_msg[0] * 3 + retry_msg)
            await rep2.delete()

    elif "いる？" in text or "わかった？" in text:
        await message.reply("はーい♪")

    elif "へるぷ" in text:
        await message.channel.send(embed=create_help_embed())

    else:
        await message.reply("何ができるか知りたいなら「へるぷ」のリプをください！")


def create_help_embed():
    embed = discord.Embed(
        title="seeker_gainoid(大喜利bot)",
        description="私はこんなことができます。遠慮なく話しかけてくださいね！",
        color=0x9E2429,
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/seeker3600/seeker_gainoid/master/face.png"
    )
    embed.add_field(name="「おだい」", value="大喜利のお題を出題します")
    embed.add_field(name="「おおぎり」", value="大喜利大会を開きます。司会進行は私ががんばります")
    embed.add_field(name="「ののしって」", value="精一杯ののりします。ボキャ貧なんて言わないで！")
    embed.add_field(name="「いる？」「わかった？」", value="お返事します")
    embed.add_field(
        name="プロジェクトサイト",
        value="https://github.com/seeker3600/seeker_gainoid\nあんなところやこんなところが見れちゃいます",
        inline=False,
    )

    return embed


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


# ジェネレータをプリロード
generate_odai_file()

# Botの起動とDiscordサーバーへの接続
print("動くよ！")
client.run(DISCORD_TOKEN)

print("止まるよ！")
generator.quit()
