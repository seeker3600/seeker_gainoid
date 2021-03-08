from __future__ import annotations

import discord
from discord.member import Member
from os import getenv
import traceback
from skills.endless_ogiri import ogiri_taikai, generate_odai_file, generator
from skills.nonoshiru import abusive
from skills.endless_umigame import soup_taikai

DISCORD_TOKEN = getenv("DISCORD_TOKEN")
DISCORD_TARGET_CHANNELS = getenv("DISCORD_TARGET_CHANNELS").split()

# 接続に必要なオブジェクトを生成
client = discord.Client()


def is_menthioned_me(message):

    # ユーザ指定
    if client.user in message.mentions:
        return True

    bot_member: Member = message.guild.get_member(client.user.id)
    a = set(r for r in bot_member.roles if r.is_bot_managed())
    b = set(r for r in message.role_mentions if r.is_bot_managed())

    # ロール指定
    return a & b


# メッセージ受信時に動作する処理
@client.event
async def on_message(message: discord.Message):

    if message.author.bot or not message.channel.name in DISCORD_TARGET_CHANNELS:
        return

    # ユーザでもロールでもメンションが無い
    if not is_menthioned_me(message):
        return

    text = message.content

    try:

        if "おおぎり" in text:
            await ogiri_taikai(message)

        elif "おだい" in text:
            await message.reply("ちょっとまってね")
            file = generate_odai_file()
            await message.reply("それっ", file=file)

        elif "ののしって" in text:
            await abusive(message)

        elif "うみがめ" in text:
            await soup_taikai(client, message)

        elif "いる？" in text or "わかった？" in text:
            await message.reply("はーい♪")

        elif "ぴーん！" in text:
            reply_msg = await message.reply("ぽーん！")

            piing = message.created_at
            catch = reply_msg.created_at
            await reply_msg.edit(content=f"ぽーん！{catch - piing}")

        elif "へるぷ" in text:
            await message.channel.send(embed=create_help_embed())

        elif "throw" in text:
            raise Exception("test")

        # else:
        #     await message.reply("何ができるか知りたいなら「へるぷ」のリプをください！")

    except Exception:
        traceback.print_exc()
        await message.reply("ぎゃん！？")


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
    embed.add_field(name="「うみがめ」", value="ウミガメのスープ大会を開きます。司会進行は私ががんばります")
    embed.add_field(name="「ののしって」", value="精一杯ののしります。ボキャ貧なんて言わないで！")
    embed.add_field(name="「いる？」「わかった？」", value="お返事します")
    embed.add_field(
        name="プロジェクトサイト",
        value="https://github.com/seeker3600/seeker_gainoid\nあんなところやこんなところが見れちゃいます",
        inline=False,
    )

    return embed


# ジェネレータをプリロード
# generate_odai_file()

# Botの起動とDiscordサーバーへの接続
print("動くよ！")
client.run(DISCORD_TOKEN)

print("止まるよ！")
generator.quit()
