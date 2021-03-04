from __future__ import annotations

import discord
from discord.member import Member
from discord.message import Message
import asyncio
import random
import re


def is_reply_to(moto):
    def predicate(message):
        return bool(
            not message.author.bot
            and message.reference
            and message.reference.message_id == moto.id
        )

    return predicate


def is_menthion_to(user):
    def is_menthion_to_core(message):

        if message.author.bot:
            return False

        # ユーザ指定
        if user in message.mentions:
            return True

        bot_member: Member = message.guild.get_member(user.id)
        a = set(r for r in bot_member.roles if r.is_bot_managed())
        b = set(r for r in message.role_mentions if r.is_bot_managed())

        # ロール指定
        return a & b

    return is_menthion_to_core


def one_line(s: str) -> str:
    return re.sub("@\w+", "", s.replace("\n", " ")).strip()


async def soup_taikai(client: discord.Client, request_msg: Message):

    await request_msg.reply("よし、じゃあ始めるよ！")
    channel: discord.TextChannel = request_msg.channel

    # 原因
    recruit_msg = await channel.send("まず、何が原因？リプライしてね！先着を採用するよ")
    causes = await client.wait_for("message", check=is_reply_to(recruit_msg))

    # 結果
    recruit_msg = await channel.send("そして、何が起こった？リプライしてね！先着を採用するよ")
    conseq = await client.wait_for("message", check=is_reply_to(recruit_msg))

    # ゲーム開始
    await channel.send(f"今回のスープのレシピが決まりました……")
    await asyncio.sleep(1)
    await channel.send(
        f"""「{causes.content}」の結果、「{conseq.content}」が起こった！さあ推理しましょう！
コマンド一覧は 「 **こまんど** 」と {client.user.mention} にメンションしてください。
では、始め！"""
    )

    list_qa: list[tuple[Message, str]] = []

    while True:
        menthion_msg = await client.wait_for(
            "message", check=is_menthion_to(client.user)
        )
        text = menthion_msg.content

        if "こまんど" in text:
            await menthion_msg.reply(embed=create_command_embed(client))

        elif "しつもん" in text:
            yes = random.randint(0, 1)
            reply = "はい、そうです！" if yes else "いいえ、ちがいます！"

            await menthion_msg.reply(reply)
            list_qa.append((menthion_msg, reply))

        elif "れしぴ" in text:
            await menthion_msg.reply(
                f"「{causes.content}」の結果、「{conseq.content}」が起こった、です！"
            )

        elif "まとめて" in text:
            summary = "\n".join(
                f"__{one_line(m.clean_content)}__\n\t\t→**{r}**" for m, r in list_qa
            )
            await menthion_msg.reply(summary)

        elif "かいとう" in text:
            rand = random.randint(0, 1)
            if rand == 0:
                await menthion_msg.reply("正解です！お見事！")
                await asyncio.sleep(3)
                break
            else:
                await menthion_msg.reply("残念！はずれ！")
                list_qa.append((menthion_msg, "残念！はずれ！"))

        elif "ぎぶあっぷ" in text:
            break

        else:
            await menthion_msg.reply("コマンド一覧は 「 **こまんど** 」とリプってください！")

    await channel.send("以上、ご参加ありがとうございました！")


def create_command_embed(client: discord.Client):
    embed = discord.Embed(
        title="無限うみがめのコマンド",
        description=f"下記の言葉をつけて、 {client.user.mention} にメンションください。",
        color=0x9E2429,
    )
    embed.add_field(name="「しつもん」", value="質問に答えます。前の質問との矛盾に注意！")
    embed.add_field(name="「かいとう」", value="謎が解けたら教えてください")
    embed.add_field(name="「れしぴ」", value="原因と、何が起こったかを再掲します")
    embed.add_field(name="「まとめて」", value="今までの質問と解答を再掲します。どばっと出すよ！")
    embed.add_field(name="「ぎぶあっぷ」", value="大会をやめます")

    return embed