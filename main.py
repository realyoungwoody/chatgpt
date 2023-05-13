import os
import pickle
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import openai

openai.api_key = "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"

bot = Bot(token="6160671331:AAHKUVz-e4qDEIxnXTgX4y51qec_xkDFsr4")
dp = Dispatcher(bot)

admin_id = 1041950401
txt = [
    os.path.join(os.getcwd(), "dts_for_bot") + "/data_simple.txt",
    os.path.join(os.getcwd(), "dts_for_bot") + "/time_1.txt"
]
pickles = [
    "ankets.pickle"
]
history = {"message.from_user.id": "old_messages"}

if not os.path.exists(pickles[0]):
    with open(pickles[0], "wb") as f:
        pickle.dump(history, f)
else:
    with open(pickles[0], "rb") as f:
        history = pickle.load(f)


async def compare_pickle(variable, file_path: str):
    with open(file_path, 'rb') as pickle_file_compare:
        data_time_compare = pickle.load(pickle_file_compare)

    for key, value in variable.items():
        if key not in data_time_compare:
            data_time_compare[key] = value
        elif data_time_compare[key] != value:
            data_time_compare[key] = value

    with open(file_path, 'wb') as pickle_file_compare:
        pickle.dump(data_time_compare, pickle_file_compare)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(text="Добро пожаловать!\nЯ CHAT-GPT и готов вам помочь!\nВведите ваш запрос:")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Ты бот в телеграмме"},
                {"role": "user", "content": "Расскажи что ты умеешь и какие команды (то что начинается через /) ты знаешь?"}])
        result = ''
        for choice in completion.choices:
            result += choice.message.content
        await message.answer(text=result)
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text=str(e))


@dp.message_handler(commands=['clear'])
async def clear(message: types.Message):
    history[message.from_user.id] = ""
    await compare_pickle(history, pickles[0])
    await message.answer(text="История пепреписки очищена!")


@dp.message_handler()
async def process_message(message: types.Message):
    try:
        oldmes = history[message.from_user.id]
    except KeyError:
        history[message.from_user.id] = oldmes = ""
    try:
        send_message = await bot.send_message(chat_id=message.chat.id, text="Запрос отправлен, думаю!")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"История нашей переписки:\n{oldmes}\n\nТы телеграм бот, способный писать сообщения и должен мне помогать"},
                {"role": "user", "content": message.text}])
        result = ''
        for choice in completion.choices:
            result += choice.message.content
        await bot.edit_message_text(text=result, chat_id=message.from_user.id, message_id=send_message.message_id)
        history[message.from_user.id] = history[message.from_user.id] + "\n\nЗапрос:\n" + message.text + "\nОтвет:\n   " + result
        await compare_pickle(history, pickles[0])
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text=str(e))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
