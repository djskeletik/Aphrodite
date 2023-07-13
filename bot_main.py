# import logging
#
# from aiogram import Bot, Dispatcher, types
# from aiogram import executor
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
#
# import config
# from DataBase import DB
# from config import DB_CONFIG
# from utils import ST
#
# # Define menu options
# MENU_START_OPTIONS = ["Продавец", "Покупатель"]
# MENU_SALESMAN_OPTIONS = ["Посмотреть заказы", "Профиль", "Выйти"]
# MENU_BUYER_OPTIONS = ["Зарегать заявку", "Профиль", "Выйти"]
# MENU_APPLICATIONS_OPTIONS = ["Выйти"]
#
# bot = Bot(token=config.BOT_TOKEN)
# dp = Dispatcher(bot, storage=MemoryStorage())
# dp.middleware.setup(LoggingMiddleware())
# logging.basicConfig(level=logging.INFO)
# db = DB(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['db'])
#
#
# # Create reply keyboard markup for menus
# def create_menu_markup(options):
#     menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     menu_markup.add(*options)
#     return menu_markup
#
#
# # Create menus
# MENU_START = create_menu_markup(MENU_START_OPTIONS)
# MENU_SALESMAN = create_menu_markup(MENU_SALESMAN_OPTIONS)
# MENU_BUYER = create_menu_markup(MENU_BUYER_OPTIONS)
# MENU_APPLICATIONS = create_menu_markup(MENU_APPLICATIONS_OPTIONS)
#
#
# @dp.message_handler(commands="start")
# async def start(message: types.Message):
#     if db.get_user_by_param("username", message.from_user.username):
#         await message.reply(f"С возвращением, {message.from_user.username}", reply_markup=MENU_START)
#     else:
#         db.add_user(message.from_user.full_name, message.from_user.id, message.from_user.username)
#         await message.reply(f"Мы рады вас приветствовать, {message.from_user.username}", reply_markup=MENU_START)
#
#     await ST.Menu.set()
#
#
# @dp.message_handler(state=ST.Menu)
# async def menu(message: types.Message):
#     text = message.text
#
#     if text == "Продавец":
#         await message.answer("Вы зашли в раздел 'Продавец'", reply_markup=MENU_SALESMAN)
#         await ST.Salesman.set()
#     elif text == "Покупатель":
#         await message.reply("Вы зашли в раздел 'Покупатель'", reply_markup=MENU_BUYER)
#         await ST.Buyer.set()
#     else:
#         await message.reply("Что-то непонятное вводишь", reply_markup=MENU_START)
#         await ST.Menu.set()
#
#
# @dp.message_handler(state=ST.Buyer)
# async def menu_buyer(message: types.Message):
#     text = message.text
#     if text == "Зарегать заявку":
#         await message.reply("Скиньте ссылку на товар")
#         await ST.Application_register.set()
#     elif text == "Выйти":
#         await message.reply("Вы вышли из раздела 'Покупатель'", reply_markup=MENU_START)
#         await ST.Menu.set()
#     else:
#         await message.reply("Что-то непонятное вводишь", reply_markup=MENU_BUYER)
#         await ST.Buyer.set()
#
#
# @dp.message_handler(state=ST.Salesman)
# async def menu_salesman(message: types.Message):
#     text = message.text
#     if text == "Посмотреть заказы":
#         await message.reply("Заявок пока нет", reply_markup=MENU_SALESMAN)
#         await ST.Salesman.set()
#     elif text == "Выйти":
#         await message.reply("Вы вышли из раздела 'Продавец'", reply_markup=MENU_START)
#         await ST.Menu.set()
#     else:
#         await message.reply("Что-то непонятное вводишь", reply_markup=MENU_SALESMAN)
#         await ST.Salesman.set()
#
#
# # @dp.message_handler(state=ST.Application_register)
# # async def menu_applications(message: types.Message):
# #     text = message.text
# #     token = secrets.token_hex(16)
# #     db.add_thing(token, "item_type", "item_name", "manufacturer", 100, "delivery_markup", customer, item_link, description=None)
#
# executor.start_polling(dp, skip_updates=True)


import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from utils import ST


class AphBot:
    MENU_START_OPTIONS = ["Продавец", "Покупатель"]
    MENU_SALESMAN_OPTIONS = ["Посмотреть заказы", "Профиль", "Выйти"]
    MENU_BUYER_OPTIONS = ["Зарегать заявку", "Профиль", "Выйти"]
    MENU_APPLICATIONS_OPTIONS = ["Выйти"]

    def __init__(self, token, db):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.dp.middleware.setup(LoggingMiddleware())
        logging.basicConfig(level=logging.INFO)
        self.db = db
        self.setup_handlers()
        self.menu_markups = self.create_menu_markups()

    def create_menu_markups(self):
        def create_menu_markup(options):
            menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            menu_markup.add(*options)
            return menu_markup

        menu_markups = {
            "start": create_menu_markup(self.MENU_START_OPTIONS),
            "salesman": create_menu_markup(self.MENU_SALESMAN_OPTIONS),
            "buyer": create_menu_markup(self.MENU_BUYER_OPTIONS),
            "applications": create_menu_markup(self.MENU_APPLICATIONS_OPTIONS),
        }
        return menu_markups

    def setup_handlers(self):
        self.dp.message_handler(commands="start")(self.start)
        self.dp.message_handler(state=ST.Menu)(self.menu)
        self.dp.message_handler(state=ST.Buyer)(self.menu_buyer)
        self.dp.message_handler(state=ST.Salesman)(self.menu_salesman)
        # Uncomment the following line when you implement `menu_applications` function
        # self.dp.message_handler(state=ST.Application_register)(self.menu_applications)

    async def start(self, message: types.Message):
        if self.db.get_user_by_param("username", message.from_user.username):
            await message.reply(f"С возвращением, {message.from_user.username}",
                                reply_markup=self.menu_markups["start"])
        else:
            self.db.add_user(message.from_user.full_name, message.from_user.id, message.from_user.username)
            await message.reply(f"Мы рады вас приветствовать, {message.from_user.username}",
                                reply_markup=self.menu_markups["start"])
        await ST.Menu.set()

    async def menu(self, message: types.Message):
        text = message.text
        if text == "Продавец":
            await message.answer("Вы зашли в раздел 'Продавец'", reply_markup=self.menu_markups["salesman"])
            await ST.Salesman.set()
        elif text == "Покупатель":
            await message.reply("Вы зашли в раздел 'Покупатель'", reply_markup=self.menu_markups["buyer"])
            await ST.Buyer.set()
        else:
            await message.reply("Что-то непонятное вводишь", reply_markup=self.menu_markups["start"])
            await ST.Menu.set()

    async def menu_buyer(self, message: types.Message):
        text = message.text
        if text == "Зарегать заявку":
            await message.reply("Скиньте ссылку на товар")
            await ST.Application_register.set()
        elif text == "Профиль":
            user_info = self.db.get_user_by_param("username", message.from_user.username)
            if user_info is not None:

                await message.answer("*Профиль* \n"
                                                "Имя: *" + message.from_user.full_name + "*\n"
                                                "Username: *" + "@"+ str(user_info["username"]) + "*\n"                                        
                                                "Дата присоединения: _" + str(user_info["join_date"]) + "_\n"
                                                "Рейтинг: _" + str(user_info["ratings"]) + "_\n"                                                        
                                                "*Успешных сделок, как покупатель*: _" + str(user_info["orders_as_buyer"]) + "_\n", parse_mode="Markdown", reply_markup=self.menu_markups["buyer"])

            else:
                await message.reply("Ошибка при получении данных профиля", reply_markup=self.menu_markups["buyer"])
            await ST.Buyer.set()
        elif text == "Выйти":
            await message.reply("Вы вышли из раздела 'Покупатель'", reply_markup=self.menu_markups["start"])
            await ST.Menu.set()
        else:
            await message.reply("Что-то непонятное вводишь", reply_markup=self.menu_markups["buyer"])
            await ST.Buyer.set()

    async def menu_salesman(self, message: types.Message):
        text = message.text
        if text == "Посмотреть заказы":
            await message.reply("Заявок пока нет", reply_markup=self.menu_markups["salesman"])
            await ST.Salesman.set()
        elif text == "Профиль":
            user_info = self.db.get_user_by_param("username", message.from_user.username)
            if user_info is not None:
                # user_info_str = "\n".join([f"{k}: {v}" for k, v in user_info.items()])
                # await message.reply(f"Ваш профиль:\n{user_info_str}", reply_markup=self.menu_markups["buyer"])

                await message.answer("*Профиль* \n"
                                                "Имя: *" + message.from_user.full_name + "*\n"
                                                "Username: *" + "@"+ str(user_info["username"]) + "*\n"                                        
                                                "Дата присоединения: _" + str(user_info["join_date"]) + "_\n"
                                                "Рейтинг: _" + str(user_info["ratings"]) + "_\n"    
                                                "*Успешных сделок, как продавец*: _" + str(user_info["orders_as_seller"]) + "_\n", parse_mode="Markdown", reply_markup=self.menu_markups["salesman"])

            else:
                await message.reply("Ошибка при получении данных профиля", reply_markup=self.menu_markups["buyer"])
            await ST.Salesman.set()
        elif text == "Выйти":
            await message.reply("Вы вышли из раздела 'Продавец'", reply_markup=self.menu_markups["start"])
            await ST.Menu.set()
        else:
            await message.reply("Что-то непонятное вводишь", reply_markup=self.menu_markups["salesman"])
            await ST.Salesman.set()

    def run(self):
        from aiogram import executor
        executor.start_polling(self.dp, skip_updates=True)
