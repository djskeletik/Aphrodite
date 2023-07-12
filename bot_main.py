from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram import executor
from utils import ST
import logging
import config

# Define menu options
MENU_START_OPTIONS = ["Продавец", "Покупатель"]
MENU_SALESMAN_OPTIONS = ["Посмотреть заказы", "Профиль", "Выйти"]
MENU_BUYER_OPTIONS = ["Зарегать заявку", "Профиль", "Выйти"]
MENU_APPLICATIONS_OPTIONS = ["Выйти"]

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)

# Create reply keyboard markup for menus
def create_menu_markup(options):
    menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_markup.add(*options)
    return menu_markup

# Create menus
MENU_START = create_menu_markup(MENU_START_OPTIONS)
MENU_SALESMAN = create_menu_markup(MENU_SALESMAN_OPTIONS)
MENU_BUYER = create_menu_markup(MENU_BUYER_OPTIONS)
MENU_APPLICATIONS = create_menu_markup(MENU_APPLICATIONS_OPTIONS)

@dp.message_handler(commands="start")
async def start(message: types.Message, state: FSMContext):
    await message.reply("Привет", reply_markup=MENU_START)
    await ST.Menu.set()

@dp.message_handler(state=ST.Menu)
async def menu(message: types.Message, state: FSMContext):
    text = message.text

    if text == "Продавец":
        await message.answer("Вы зашли в раздел 'Продавец'", reply_markup=MENU_SALESMAN)
        await ST.Salesman.set()
    elif text == "Покупатель":
        await message.reply("Вы зашли в раздел 'Покупатель'", reply_markup=MENU_BUYER)
        await ST.Buyer.set()
    else:
        await message.reply("Что-то непонятное вводишь", reply_markup=MENU_START)
        await ST.Menu.set()

@dp.message_handler(state=ST.Buyer)
async def menu_buyer(message: types.Message):
    text = message.text

    if text == "Зарегать заявку":
        await message.reply("Скиньте ссылку на товар", reply_markup=MENU_BUYER)
        await ST.Applications.set()
    elif text == "Выйти":
        await message.reply("Вы вышли из раздела 'Покупатель'", reply_markup=MENU_START)
        await ST.Menu.set()
    else:
        await message.reply("Что-то непонятное вводишь", reply_markup=MENU_BUYER)
        await ST.Buyer.set()

@dp.message_handler(state=ST.Salesman)
async def menu_salesman(message: types.Message):
    text = message.text
    if text == "Посмотреть заказы":
        await message.reply("Заявок пока нет", reply_markup=MENU_SALESMAN)
        await ST.Salesman.set()
    elif text == "Выйти":
        await message.reply("Вы вышли из раздела 'Продавец'", reply_markup=MENU_START)
        await ST.Menu.set()
    else:
        await message.reply("Что-то непонятное вводишь", reply_markup=MENU_SALESMAN)
        await ST.Salesman.set()

@dp.message_handler(state=ST.Applications)
async def menu_applications(message: types.Message):
    text = message.text
    if text == "Выйти":
        await message.reply("Вы вышли из раздела 'Покупатель'", reply_markup=MENU_START)
        await ST.Menu.set()

executor.start_polling(dp, skip_updates=True)
