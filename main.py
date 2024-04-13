import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from wish_list import games

TOKEN = '6866932813:AAEXhHj2fBIA4kgrS4kKSfhZwocDTLNqHrg'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
feed_back = ''

async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустити бота'),
            types.BotCommand('add_game', 'Додати гру до віш-ліста'),
            types.BotCommand('remove_game', 'Видалити гру з віш-ліста'),
            types.BotCommand(command='add_feedback', description='Додати відгук до гри'),
            types.BotCommand(command='watch_wishlist', description='Подивитись мій віш-ліст')
        ]
    )



@dp.message_handler(commands='start')
async def start(message: types.Message):
    game_choice = InlineKeyboardMarkup()
    for game in games.keys():
        button = InlineKeyboardButton(text=game, callback_data=game)
        game_choice.add(button)
    await message.answer(text='Привіт. Я твій віш-ліст ігор Steam/Epic. Обери гру з віш-ліста про яку ти хочеш дізнатись', reply_markup=game_choice)


@dp.callback_query_handler()
async def get_film_info(callback_query: types.CallbackQuery):
    if callback_query.data in games.keys():
        await bot.send_photo(callback_query.message.chat.id, games[callback_query.data]['photo'])
        url = games[callback_query.data]['link']
        price = games[callback_query.data]['price']
        size = games[callback_query.data]['size']
        year = games[callback_query.data]['year']
        feedback = games[callback_query.data]['feedback']
        message = f"<b>Посилання на магазин-сторінку гри: </b> {url}\n<b>Ціна: </b>{price}\n<b>Розмір гри: </b> {size}\n<b>Рік виходу: </b>{year}\n<b>Твій відгук: </b>{feedback}"
        await bot.send_message(callback_query.message.chat.id, message, parse_mode='html')
    else:
        await bot.send_message(callback_query.message.chat.id, 'Гру не знайдено. Спробуй ще раз!')


@dp.message_handler(commands='add_game')
async def add_game(message: types.Message, state: FSMContext):
    await state.set_state('set_game_name')
    await message.answer(text='Введіть назву гри, яку хочете додати до віш-ліста')


game_name = ''


@dp.message_handler(state='set_game_name')
async def set_game_name(message: types.Message, state: FSMContext):
    global game_name
    if len(message.text) > 30:
        message.answer(text='Назва гри занадто довга!')
    else:
        game_name = message.text
        games[game_name] = {}
        await state.set_state('set_site_url')
        await message.answer(text='Добре. Тепер введіть посилання на Steam/Epic-сторінку гри')


@dp.message_handler(state='set_site_url')
async def set_site_url(message: types.Message, state: FSMContext):
    global game_name
    game_url = message.text
    games[game_name]['link'] = game_url
    await state.set_state('set_price')
    await message.answer(text='Чудово. Скільки коштує твоя гра?(бажано в гривнях)\nЯкщо гра безкоштовна, напишіть Free')


@dp.message_handler(state='set_price')
async def set_description(message: types.Message, state: FSMContext):
    global game_name
    game_price = message.text
    games[game_name]['price'] = game_price
    await state.set_state('set_size')
    await message.answer(text='Чудово. Скільки важить твоя гра?(У GB)')


@dp.message_handler(state='set_size')
async def set_size(message: types.Message, state: FSMContext):
    global game_name
    game_size = message.text
    games[game_name]['size'] = game_size
    await state.set_state('set_year')
    await message.answer(text='Чудово. Коли вийшла твоя гра?')
@dp.message_handler(state='set_year')
async def set_year(message: types.Message, state: FSMContext):
    global game_name
    game_year = message.text
    games[game_name]['year'] = game_year
    await state.set_state('set_feedback')
    await message.answer(text='Чудово. Можеш написати відгук для цієї гри? Якщо ні, то просто напиши Відгуку немає')
@dp.message_handler(state='set_feedback')
async def set_feedback(message: types.Message, state: FSMContext):
    global game_name
    game_feedback = message.text
    games[game_name]['feedback'] = game_feedback
    await state.set_state('set_photo')
    await message.answer(text='Останній крок: дай посилання на фото-баннер гри')


@dp.message_handler(state='set_photo')
async def set_photo(message: types.Message, state: FSMContext):
    global game_name
    game_photo = message.text
    games[game_name]['photo'] = game_photo
    await state.finish()
    await message.answer(text='Супер! Нову гру додано до віш-ліста')

@dp.message_handler(commands="remove_game")
async def del_game(message: types.Message, state: FSMContext):
    await state.set_state('del_game')
    await message.answer(text='Напиши назву гри, яку хочеш видалити з віш-ліста')

@dp.message_handler(state='del_game')
async def del_game(message: types.Message, state: FSMContext):
    global game_name
    game_name = message.text
    await state.finish()
    if game_name in games.keys():
        del games[game_name]
        await message.answer(text=f'{game_name} було видалено з віш-ліста')
    else:
        await message.answer(text='Такої гри немає в твоєму віш-лісті')
@dp.message_handler(commands='watch_wishlist')
async def watch_wishlist(message: types.Message, state: FSMContext):
    game_choice = InlineKeyboardMarkup()
    for game in games.keys():
        button = InlineKeyboardButton(text=game, callback_data=game)
        game_choice.add(button)
    await message.answer('Ось ігри, що наразі знаходяться в твоєму вішл-лісті. Обери гру, щоб дізнатись більше', reply_markup=game_choice)
@dp.callback_query_handler()
async def watch_game(callback_query: types.CallbackQuery):
    if callback_query.data in games.keys():
        await bot.send_photo(callback_query.message.chat.id, games[callback_query.data]['photo'])
        url = games[callback_query.data]['link']
        price = games[callback_query.data]['price']
        size = games[callback_query.data]['size']
        year = games[callback_query.data]['year']
        feedback = games[callback_query.data]['feedback']
        message = f"<b>Посилання на магазин-сторінку гри: </b> {url}\n<b>Ціна: </b>{price}\n<b>Розмір гри: </b> {size}\n<b>Рік виходу: </b>{year}\n<b>Твій відгук: </b>{feedback}"
        await bot.send_message(callback_query.message.chat.id, message, parse_mode='html')
@dp.message_handler(commands='add_feedback')
async def add_feedback(message: types.Message, state: FSMContext):
    await state.set_state('find_game')
    await message.answer(text='Напиши назву гри для якої ти хочеш написати відгук')
@dp.message_handler(state='find_game')
async def add_feedback(message: types.Message, state: FSMContext):
    global game_name
    game_name = message.text
    if game_name in games:
        await state.set_state('add_feedback')
        await message.answer(text=f'{game_name} в твоєму вішлісті. Напиши відгук для цієї гри')
@dp.message_handler(state='add_feedback')
async def add_feedback(message: types.Message, state: FSMContext):
    global feed_back
    global game_name
    feed_back = message.text
    games[game_name]['feedback'] = feed_back
    await state.finish()
    await message.answer(text=f'Відгук до гри {game_name} було додано!')


async def on_startup(dp):
    await set_default_commands(dp)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)