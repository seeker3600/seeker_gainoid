import asyncio
import random

VOCABULARY = [
    "あーもうこの鈍感！",
    "ばか！あほ！おたんこなす！",
    "このすかたん！こんこんちきのすっとこどっこい！",
    "えっとえっと、あんぽんたん！",
    "お、おとといきやがれ！",
]


async def abusive(message):

    idx = random.randrange(len(VOCABULARY))
    rep = await message.reply(VOCABULARY[idx])

    if idx == 0:
        await asyncio.sleep(2)
        rep2 = await message.channel.send("あっ")
        await asyncio.sleep(2)

        retry_msg = VOCABULARY[random.randrange(1, len(VOCABULARY))]
        await rep.edit(content=retry_msg[0] * 3 + retry_msg)
        await rep2.delete()
