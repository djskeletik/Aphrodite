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
import secrets
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from datetime import timedelta, datetime
from utils import ST
class AphBot:
    MENU_START_OPTIONS = ["Продавец", "Покупатель"]
    MENU_SALESMAN_OPTIONS = ["Посмотреть заказы", "Мои заказы", "Профиль", "Выйти"]
    MENU_BUYER_OPTIONS = ["Зарегать заявку", "Мои заказы", "Профиль", "Выйти"]
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
        self.dp.message_handler(state=ST.Application_register)(self.application_register)
        self.dp.callback_query_handler()(self.application_interest)
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
            await message.answer("Вы зашли в раздел 'Покупатель'", reply_markup=self.menu_markups["buyer"])
            await ST.Buyer.set()
        else:
            await message.reply("Что-то непонятное вводишь", reply_markup=self.menu_markups["start"])
            await ST.Menu.set()

    async def menu_buyer(self, message: types.Message, state: FSMContext):
        text = message.text
        if text == "Зарегать заявку":
            await message.reply("Скиньте ссылку на товар", reply_markup = types.ReplyKeyboardRemove())
            await ST.Application_register.set()
        elif text == "Профиль":
            user_info = self.db.get_user_by_param("username", message.from_user.username)
            if user_info is not None:
                if user_info["number_of_ratings"] == 0:
                    a = 1
                else:
                    a = user_info["number_of_ratings"]
                await message.answer("*Профиль* \n"
                                                "Имя: *" + message.from_user.full_name + "*\n"
                                                "Username: *" + "@"+ str(user_info["username"]) + "*\n"                                        
                                                "Дата присоединения: _" + str(user_info["join_date"]) + "_\n"
                                                "Рейтинг: _" + str(round(user_info["sum_of_ratings"]/a,2)) + "_\n"                                                        
                                                "*Успешных сделок, как покупатель*: _" + str(user_info["orders_as_buyer"]) + "_\n", parse_mode="Markdown", reply_markup=self.menu_markups["buyer"])

            else:
                await message.reply("Ошибка при получении данных профиля", reply_markup=self.menu_markups["buyer"])
            await ST.Buyer.set()
        elif text == "Мои заказы":
            await message.answer("Ваши заказы:", reply_markup = types.ReplyKeyboardRemove())
            await state.reset_state(with_data=False)
            orders = self.db.get_orders_by_username(message.from_user.username)
            for order in orders:
                if order["status"] == 0:
                    button1 = types.InlineKeyboardButton(text='Удалить заказ', callback_data="delete" + "|" + order["order_token"]+ "|" + "buyer")
                    bet_markup = types.InlineKeyboardMarkup().add(button1)
                    await message.answer("*Заказ* \n"
                                                  "Цена товара: " + str(int(order["average_price"])) + " €\n"
                                                  "Дата оформления: " + str(order["add_date"]) + "\n"
                                                   "Статус: " + str(order["status"]) + "\n"                                                
                                                   "Ссылка: " + order["item_link"] + "\n",
                                                  parse_mode="Markdown", reply_markup=bet_markup)
                else:
                    user_info = self.db.get_user_by_param("username", order["salesman_username"])
                    await message.answer("*Полный Заказ* \n"
                                         "Цена товара: " + str(int(order["average_price"])) + " €\n"
                                         "Когда продавец должен отдать заказ: " + str( order["finish_date"]) + "\n"
                                         "Ссылка: " + order["item_link"] + "\n"
                                         "Статус: " + str(order["status"]) + "\n"                                    
                                         "-------------------------------------------\n"
                                         "*Продавец* \n"
                                         "Имя: *@" + order["salesman_username"] + "*\n",
                                         parse_mode="Markdown")
            button2 = types.InlineKeyboardButton(text='Выйти из просмотра моих заказов', callback_data="away"+"|"+"buyer")
            bet_markup_away = types.InlineKeyboardMarkup().add(button2)
            await message.answer("-------------------------------------------", reply_markup=bet_markup_away)
        elif text == "Выйти":
            await message.answer("Вы вышли из раздела 'Покупатель'", reply_markup=self.menu_markups["start"])
            await ST.Menu.set()
        else:
            await message.reply("Что-то непонятное вводишь", reply_markup=self.menu_markups["buyer"])
            await ST.Buyer.set()


    async def application_register(self, message: types.Message):
        text = message.text
        token = secrets.token_hex(16)
        self.db.add_thing(token, "clothes", "item_name", "manufacturer", 100, 0, message.from_user.id, message.from_user.username, text, salesman_username=None,  description=None)
        await message.reply("Заказ добавлен, ожидайте отклика продавцов", reply_markup=self.menu_markups["buyer"])
        await ST.Buyer.set()





    async def menu_salesman(self, message: types.Message, state: FSMContext):
        text = message.text
        if text == "Посмотреть заказы":
            await state.reset_state(with_data=False)
            await message.answer("Заказы:", reply_markup = types.ReplyKeyboardRemove())
            orders_info = self.db.get_orders()
            for order in orders_info:
                # if order["username"] == message.from_user.username:
                #     button1 = types.InlineKeyboardButton(text='Удалить заказ', callback_data="delete" + "|"  + order["order_token"])
                #     bet_markup = types.InlineKeyboardMarkup().add(button1)
                #     await message.answer("*Ваш заказ* \n"
                #                          "Цена товара: *" + str(int(
                #         order["average_price"])) + "* €\n",
                #                          parse_mode="Markdown", reply_markup=bet_markup)
                # else:
                button1 = types.InlineKeyboardButton(text='Интересно', callback_data="token" + "|" + order["order_token"])
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                await message.answer("*Заказ* \n" 
                                     "Цена товара: *" + str(int( order["average_price"])) + "* €\n", parse_mode="Markdown", reply_markup=bet_markup)

            button1 = types.InlineKeyboardButton(text='Ни один заказ не интересен', callback_data="away" + "|" + "salesman")
            bet_markup_away = types.InlineKeyboardMarkup().add(button1)
            await message.answer("-------------------------------------------", reply_markup=bet_markup_away)
        elif text == "Профиль":
            user_info = self.db.get_user_by_param("username", message.from_user.username)
            if user_info["number_of_ratings"] == 0:
                a = 1
            else:
                a = user_info["number_of_ratings"]
            if user_info is not None:
                await message.answer("*Профиль* \n"
                                                "Имя: *" + message.from_user.full_name + "*\n"
                                                "Username: *" + "@"+ str(user_info["username"]) + "*\n"                                        
                                                "Дата присоединения: " + str(user_info["join_date"]) + "\n"
                                                "Рейтинг: " + str(round(user_info["sum_of_ratings"]/a,2)) + "\n"    
                                                "Успешных сделок, как продавец: " + str(user_info["orders_as_seller"]) + "\n", parse_mode="Markdown", reply_markup=self.menu_markups["salesman"])

            else:
                await message.reply("Ошибка при получении данных профиля", reply_markup=self.menu_markups["buyer"])
            await ST.Salesman.set()
        elif text == "Мои заказы":
            await message.answer("Заказы, над которыми вы работаете:", reply_markup = types.ReplyKeyboardRemove())
            orders = self.db.get_order_by_salesman_username(message.from_user.username)
            await state.reset_state(with_data=False)
            for order in orders:
                if order["status"] == 1:
                    button1 = types.InlineKeyboardButton(text='Отказаться от доставки', callback_data="refusal" + "|" + order["order_token"])
                    button2 = types.InlineKeyboardButton(text='Заказ уже куплен !', callback_data="change_status" + "|" +order["order_token"])
                    bet_markup = types.InlineKeyboardMarkup().add(button1,button2)
                    await message.answer("*Заказ* \n"
                                         "Цена товара: " + str(int(order["average_price"])) + " €\n"
                                         "К какой дате вы должны отдать " + str(order["finish_date"]) + "\n"
                                         "Статус: " + str(order["status"]) + "\n"                                               
                                         "Ссылка: " + order["item_link"] + "\n"
                                         "-------------------------------------------\n"
                                         "*Покупатель* \n"
                                         "Username: *@" + order["username"] + "*\n", parse_mode="Markdown", reply_markup=bet_markup)
                else:
                    button3 = types.InlineKeyboardButton(text='Заказ передан', callback_data="кон" + "|" +order["order_token"])
                    bet_markup = types.InlineKeyboardMarkup().add(button3)
                    await message.answer("*Заказ* \n"
                                         "Цена товара: " + str(int(order["average_price"])) + " €\n"
                                         "Вы должны отдать через " + str(order["finish_date"]) + " дней\n"
                                         "Статус: " + str(order["status"]) + "\n"
                                         "Ссылка: " + order["item_link"] + "\n"
                                         "-------------------------------------------\n"
                                         "*Покупатель* \n"
                                         "Username: *@" + order["username"] + "*\n", parse_mode="Markdown", reply_markup=bet_markup)
            button4 = types.InlineKeyboardButton(text='Выйти из просмотра моих заказов',callback_data="away" + "|" + "salesman")
            bet_markup_away = types.InlineKeyboardMarkup().add(button4)
            await message.answer("-------------------------------------------", reply_markup=bet_markup_away)
        elif text == "Выйти":
            await message.answer("Вы вышли из раздела 'Продавец'", reply_markup=self.menu_markups["start"])
            await ST.Menu.set()
        else:
            await message.reply("Что-то непонятное вводишь", reply_markup=self.menu_markups["salesman"])
            await ST.Salesman.set()



    async def application_interest(self, callback: types.CallbackQuery, state: FSMContext):
        token = callback.data
        if "take" in token:
            print(callback.message.message_id)
            token = token.split("|")
            token = token[1]
            order = self.db.get_order_by_token(token)
            if order[0]["status"] == 0:
                print("п"+"|"+ token + "|" + "5")
                button1 = types.InlineKeyboardButton(text='5', callback_data="г"+"|"+ token + "|"  + "5")
                button2 = types.InlineKeyboardButton(text='10',callback_data="г" + "|" + token + "|" + "10")
                button3 = types.InlineKeyboardButton(text='20',callback_data="г" + "|" + token + "|" + "20")
                bet_markup = types.InlineKeyboardMarkup().add(button1,button2, button3)
                await callback.message.answer("Сколько процентов вы хотите взять сверху ?", reply_markup=bet_markup)
            else:
                await callback.message.answer("Извините, заказ уже нашел своего покупателя")

        elif "г" in token:
            token = token.split("|")
            percent = token[2]
            token = token[1]
            button1 = types.InlineKeyboardButton(text='1', callback_data="п" + "|" + token + "|" + "1"+ "|" + percent)
            button2 = types.InlineKeyboardButton(text='2', callback_data="п" + "|" + token + "|" + "2"+ "|" + percent)
            button3 = types.InlineKeyboardButton(text='3', callback_data="п" + "|" + token + "|" + "3"+ "|" + percent)
            button4 = types.InlineKeyboardButton(text='4', callback_data="п" + "|" + token + "|" + "4"+ "|" + percent)
            button5 = types.InlineKeyboardButton(text='5', callback_data="п" + "|" + token + "|" + "5"+ "|" + percent)
            button6 = types.InlineKeyboardButton(text='6', callback_data="п" + "|" + token + "|" + "6"+ "|" + percent)
            button7 = types.InlineKeyboardButton(text='7', callback_data="п" + "|" + token + "|" + "7"+ "|" + percent)
            button8 = types.InlineKeyboardButton(text='8', callback_data="п" + "|" + token + "|" + "8"+ "|" + percent)
            button9 = types.InlineKeyboardButton(text='9', callback_data="п" + "|" + token + "|" + "9"+ "|" + percent)
            button10 = types.InlineKeyboardButton(text='10', callback_data="п" + "|" + token + "|" + "10"+ "|" + percent)
            button11 = types.InlineKeyboardButton(text='11', callback_data="п" + "|" + token + "|" + "11"+ "|" + percent)
            button12 = types.InlineKeyboardButton(text='12', callback_data="п" + "|" + token + "|" + "12"+ "|" + percent)
            button13 = types.InlineKeyboardButton(text='13', callback_data="п" + "|" + token + "|" + "13"+ "|" + percent)
            button14 = types.InlineKeyboardButton(text='14', callback_data="п" + "|" + token + "|" + "14"+ "|" + percent)
            button15 = types.InlineKeyboardButton(text='15', callback_data="п" + "|" + token + "|" + "15"+ "|" + percent)
            button16 = types.InlineKeyboardButton(text='16', callback_data="п" + "|" + token + "|" + "16"+ "|" + percent)
            button17 = types.InlineKeyboardButton(text='17', callback_data="п" + "|" + token + "|" + "17"+ "|" + percent)
            button18 = types.InlineKeyboardButton(text='18', callback_data="п" + "|" + token + "|" + "18"+ "|" + percent)
            button19 = types.InlineKeyboardButton(text='19', callback_data="п" + "|" + token + "|" + "19"+ "|" + percent)
            button20 = types.InlineKeyboardButton(text='20', callback_data="п" + "|" + token + "|" + "20"+ "|" + percent)
            button21 = types.InlineKeyboardButton(text='21', callback_data="п" + "|" + token + "|" + "21"+ "|" + percent)
            button22 = types.InlineKeyboardButton(text='22', callback_data="п" + "|" + token + "|" + "22"+ "|" + percent)
            button23 = types.InlineKeyboardButton(text='23', callback_data="п" + "|" + token + "|" + "23"+ "|" + percent)
            button24 = types.InlineKeyboardButton(text='24', callback_data="п" + "|" + token + "|" + "24"+ "|" + percent)
            button25 = types.InlineKeyboardButton(text='25', callback_data="п" + "|" + token + "|" + "25"+ "|" + percent)
            button26 = types.InlineKeyboardButton(text='26', callback_data="п" + "|" + token + "|" + "26"+ "|" + percent)
            button27 = types.InlineKeyboardButton(text='27', callback_data="п" + "|" + token + "|" + "27"+ "|" + percent)
            button28 = types.InlineKeyboardButton(text='28', callback_data="п" + "|" + token + "|" + "28"+ "|" + percent)
            button29 = types.InlineKeyboardButton(text='29', callback_data="п" + "|" + token + "|" + "29"+ "|" + percent)
            button30 = types.InlineKeyboardButton(text='30', callback_data="п" + "|" + token + "|" + "30"+ "|" + percent)
            bet_markup = types.InlineKeyboardMarkup().add(button1, button2, button3, button4, button5, button6, button7, button8, button9,button10,button11,button12,button13,button14,button15,button16,button17,button18, button19,button20, button21, button22, button23, button24, button25, button26, button27, button28, button29, button30)
            await callback.message.answer("Через сколько дней сможете доставить ?", reply_markup=bet_markup)
        elif "п" in token:
            token = token.split("|")
            percent = token[3]
            data = token[2]
            token = token[1]
            order = self.db.get_order_by_token(token)
            if order[0]["status"] == 0:
                user_info = self.db.get_user_by_param("username", order[0]["username"])
                button1 = types.InlineKeyboardButton(text='Посмотреть предложение', callback_data="д"+"|" + token + "|" + str(callback.message.chat.id) + "|" + percent + "|" + data)
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                state = self.dp.current_state(chat=user_info["chat_id"])
                await state.reset_state()
                await callback.bot.send_message(user_info["chat_id"], "Ваш заказ заинтересовал продавца!", reply_markup=bet_markup)
                await callback.message.answer("Покупатель увидит, что вы заинтересованы в его заказе")
            else:
                button1 = types.InlineKeyboardButton(text='Выйти из просмотра заказов', callback_data="away")
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                await callback.message.answer("Извините, заказ уже нашел своего покупателя", reply_markup=bet_markup)
        elif "д" in token:
            token = token.split("|")
            chat_id = token[2]
            percent = token[3]
            data = token[4]
            token = token[1]
            now = datetime.now().date()
            delta = timedelta(days=int(data))
            date = now + delta
            user_info = self.db.get_user_by_param("chat_id", chat_id)
            order_info = self.db.get_order_by_token(token)
            percent_price = (int(percent) / 100) * order_info[0]["average_price"]
            print(str(date))
            button1 = types.InlineKeyboardButton(text='Согласен с продавцом!', callback_data="с" + "|" + token + "|" + chat_id + "|" + percent + "|" + str(date))
            bet_markup = types.InlineKeyboardMarkup().add(button1)
            if user_info["number_of_ratings"] == 0:
                a = 1
            else:
                a = user_info["number_of_ratings"]
            await callback.message.answer(
                                 "*Продавец* \n"
                                 "Имя: " + str( user_info["full_name"]) + "\n"
                                 "Рейтинг: " + str(round(user_info["sum_of_ratings"]/a,2)) + "\n"
                                 "Успешных сделок, как продавец: " + str( user_info["orders_as_seller"]) + "\n"
                                 "-------------------------------------------\n"
                                 "*Предлагает* \n"
                                 "Наценка: " + percent + "% ( "+ str(percent_price) + "€ )\n"
                                 "Когда продавец сможет отдать товар: " + str(date) + "\n"
                                 "-------------------------------------------\n"
                                 "*Товар* \n"                                                      
                                 "Ссылка на заказ: " + order_info[0]["item_link"] + "\n", parse_mode="Markdown", reply_markup=bet_markup)
        elif "с" in token:
            token = token.split("|")
            chat_id = token[2]
            percent = token[3]
            data = token[4]
            token = token[1]
            order_info = self.db.get_order_by_token(token)
            percent_price = (int(percent) / 100) * order_info[0]["average_price"]
            self.db.update_status_in_order(1, token)
            self.db.update_percent_and_date_in_order(percent_price, data, token)
            user_info = self.db.get_user_by_param("chat_id", chat_id)
            print(user_info["username"])
            self.db.update_salesman_username_in_order(user_info["username"], token)
            button1 = types.InlineKeyboardButton(text='Выйти из просмотра заказов', callback_data="away" + "|" + "salesman")
            bet_markup = types.InlineKeyboardMarkup().add(button1)
            await callback.message.answer("Ваш заказ нашел своего продавца", reply_markup=bet_markup)
            await callback.bot.send_message(user_info["chat_id"], f"Покупатель @{callback.message.chat.username} согласен с вашим предложением, а этот заказ появился в списке заказов, над которыми в работаете")

        elif "delete" in token:
            token = token.split("|")
            type = token[2]
            token = token[1]
            order = self.db.get_order_by_token(token)
            if order[0]["status"] == 0:
                self.db.delete_order(token)
                await callback.message.delete()
                button1 = types.InlineKeyboardButton(text='Выйти из просмотра заказов', callback_data="away"+ "|" + type)
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                await callback.message.answer("Заказ удален", reply_markup=bet_markup)
            else:
                button1 = types.InlineKeyboardButton(text='Выйти из просмотра заказов', callback_data="away" + "|" + type)
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                await callback.message.answer("Вы не можете удалить этот заказ, так как он уже взят продавцом", reply_markup=bet_markup)

        elif "change_status" in token:
            token = token.split("|")
            token = token[1]
            order_info = self.db.get_order_by_token(token)
            self.db.update_status_in_order(2,token)
            user_info = self.db.get_user_by_param("chat_id", order_info[0]["chat_id"])
            button1 = types.InlineKeyboardButton(text='Выйти из просмотра своих заказов', callback_data="away" + "|" + "salesman")
            bet_markup = types.InlineKeyboardMarkup().add(button1)
            await callback.message.answer("Заказ изменил свой статус !")
            await callback.bot.send_message(user_info["chat_id"], "Ваш заказ изменил свой статус !")

        elif "refusal" in token:
            token = token.split("|")
            token = token[1]
            order_info = self.db.get_order_by_token(token)
            if order_info[0]["status"] == 1:
                self.db.update_status_in_order(0, token)
                user_info = self.db.get_user_by_param("chat_id", order_info[0]["chat_id"])
                button1 = types.InlineKeyboardButton(text='Выйти из просмотра своих заказов',callback_data="away" + "|" + "salesman")
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                await callback.message.answer("Вы отказались работать над проектом, ваш рейтинг снизиться", reply_markup=bet_markup)
                await callback.bot.send_message(user_info["chat_id"], "Продавец отказался работать над вашим проектом, просим прощения(")
            else:
                button1 = types.InlineKeyboardButton(text='Выйти из просмотра своих заказов', callback_data="away" + "|" + "salesman")
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                await callback.message.reply("Вы не можете от него отказаться",reply_markup=bet_markup)

        elif "кон" in token:
            token = token.split("|")
            token = token[1]
            button1 = types.InlineKeyboardButton(text='Да', callback_data="Да" + "|" + token)
            button2 = types.InlineKeyboardButton(text='Нет', callback_data="away" + "|" + "salesman")
            button3 = types.InlineKeyboardButton(text='Выйти из просмотра своих заказов',callback_data="away" + "|" + "salesman")
            bet_markup_away = types.InlineKeyboardMarkup().add(button3)
            bet_markup = types.InlineKeyboardMarkup().add(button1, button2)
            await callback.message.answer("Мы спросим у покупателя, получил ли он товар")
            order_info = self.db.get_order_by_token(token)
            await callback.bot.send_message(order_info[0]["chat_id"],f"Пришел этот заказ: {order_info[0]['item_link']} ?", reply_markup=bet_markup)

        elif "Да" in token:
            token = token.split("|")
            token = token[1]
            order_info = self.db.get_order_by_token(token)
            user_info = self.db.get_user_by_param("username", order_info[0]["salesman_username"])
            self.db.update_number_oreders_in_param("orders_as_buyer", callback.message.chat.id)
            self.db.update_number_oreders_in_param("orders_as_seller", user_info["chat_id"])
            button1 = types.InlineKeyboardButton(text='1', callback_data="о" + "|" + str(user_info["chat_id"]) + "|" + "1")
            button2 = types.InlineKeyboardButton(text='2', callback_data="о" + "|" + str(user_info["chat_id"]) + "|" + "2")
            button3 = types.InlineKeyboardButton(text='3', callback_data="о" + "|" + str(user_info["chat_id"]) + "|" + "3")
            button4 = types.InlineKeyboardButton(text='4', callback_data="о" + "|" + str(user_info["chat_id"]) + "|" + "4")
            button5 = types.InlineKeyboardButton(text='5', callback_data="о" + "|" + str(user_info["chat_id"]) + "|" + "5")
            bet_markup = types.InlineKeyboardMarkup().add(button1, button2, button3, button4, button5)
            button6 = types.InlineKeyboardButton(text='Выйти из просмотра своих заказов', callback_data="away" + "|" + "salesman")
            bet_markup_away = types.InlineKeyboardMarkup().add(button6)
            await callback.message.answer("Ура! Заказ передан !\nКак вы оценили бы работу продавца ?", reply_markup=bet_markup)
            self.db.delete_order(token)
            user_info = self.db.get_user_by_param("username", order_info[0]["salesman_username"])
            print(str(callback.message.chat.id))
            button1 = types.InlineKeyboardButton(text='1', callback_data="о" + "|" + str(callback.message.chat.id) + "|" + "1")
            button2 = types.InlineKeyboardButton(text='2',
                                                 callback_data="о" + "|" + str(callback.message.chat.id) + "|" + "2")
            button3 = types.InlineKeyboardButton(text='3',
                                                 callback_data="о" + "|" + str(callback.message.chat.id) + "|" + "3")
            button4 = types.InlineKeyboardButton(text='4',
                                                 callback_data="о" + "|" + str(callback.message.chat.id) + "|" + "4")
            button5 = types.InlineKeyboardButton(text='5',
                                                 callback_data="о" + "|" + str(callback.message.chat.id) + "|" + "5")
            bet_markup_s = types.InlineKeyboardMarkup().add(button1, button2, button3, button4, button5)
            await callback.bot.send_message(user_info["chat_id"],"Заказчик все подтвердил, доставка заказа окончена !\nКак вы оценили бы покупателя ?", reply_markup=bet_markup_s)

        elif "о" in token:
            token = token.split("|")
            chat_id = int(token[1])
            rating = int(token[2])
            button6 = types.InlineKeyboardButton(text='Выйти из просмотра своих заказов',  callback_data="away" + "|" + "salesman")
            bet_markup_away = types.InlineKeyboardMarkup().add(button6)
            self.db.update_rating_in_user(chat_id, rating)
            await callback.message.answer("Спасибо", reply_markup=bet_markup_away)
        elif "away" in token:
            token = token.split("|")
            type = token[1]
            await callback.message.answer("Вы вышли из просмотра заказов", reply_markup=self.menu_markups[type])
            if type == "buyer":
                await ST.Buyer.set()
            else:
                await ST.Salesman.set()
        elif "token" in token:
            token = token.split("|")
            token = token[1]
            order = self.db.get_order_by_token(token)
            user_info = self.db.get_user_by_param("username", order[0]["username"])
            button1 = types.InlineKeyboardButton(text='Выйти из просмотра заказов', callback_data="away" + "|"+"salesman")
            button2 = types.InlineKeyboardButton(text='Беру заказ !', callback_data="take" + "|" + token)
            if order[0]["status"] == 0:
                bet_markup = types.InlineKeyboardMarkup().add(button1, button2)
                if user_info["number_of_ratings"] == 0:
                    a = 1
                else:
                    a = user_info["number_of_ratings"]
                await callback.message.answer("*Покупатель* \n"
                                              "Имя заказчика: "  + str(user_info["full_name"]) + "\n"
                                              "Рейтинг заказчика: " + str(round(user_info["sum_of_ratings"]/a,2)) + "\n"
                                              "Успешных сделок, как покупатель: *" + str(user_info["orders_as_buyer"]) + "*\n"
                                              "-------------------------------------------\n"
                                              "*Товар* \n"
                                              "Цена товара: " + str(int(order[0]["average_price"])) + " €\n"
                                              "Дата оформления: " + str(order[0]["add_date"]) + "\n"
                                              "Ссылка: " + order[0]["item_link"] + "\n", parse_mode="Markdown", reply_markup=bet_markup)
            else:
                button1 = types.InlineKeyboardButton(text='Выйти из просмотра заказов', callback_data="away")
                bet_markup = types.InlineKeyboardMarkup().add(button1)
                await callback.message.answer("Извините, заказ уже нашел своего покупателя", reply_markup=bet_markup)

    def run(self):
        from aiogram import executor
        executor.start_polling(self.dp, skip_updates=True)
