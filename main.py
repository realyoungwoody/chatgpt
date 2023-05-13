import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import openai

openai.api_key = "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"

bot = Bot(token="6160671331:AAHKUVz-e4qDEIxnXTgX4y51qec_xkDFsr4")
dp = Dispatcher(bot)

if not os.path.exists("users"):
    os.mkdir("users")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if f"{message.chat.id}.txt" not in os.listdir("users"):
        with open(f"users/{message.chat.id}.txt", "w") as f:
            f.write("")
    await message.answer(text="Добро пожаловать!\nЯ CHAT-GPT и готов вам помочь!\nВведите ваш запрос:")


@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    with open(f"users/{message.chat.id}.txt", "w") as file:
        file.write("")
    await message.answer(text="История пепреписки очищена!")


@dp.message_handler()
async def process_message(message: types.Message):
    with open(f"users/{message.chat.id}.txt", "r") as file:
        oldmes = file.read()
    try:
        send_message = await bot.send_message(chat_id=message.chat.id, text="Ща, пару сек!")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Это наша страя переписка:\n{oldmes}"},
                {"role": "user", "content": message.text}])
        result = ''
        for choice in completion.choices:
            result += choice.message.content
        await bot.edit_message_text(
            text=result,
            chat_id=message.chat.id,
            message_id=send_message.message_id,
        )

        with open(f"users/{message.chat.id}.txt", "a+") as file:
            file.write(
                message.text
                + "\n"
                + result
                + "\n"
            )
    except Exception as e:
        await bot.send_message(chat_id=message.chat.id, text=str(e))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
