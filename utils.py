from aiogram.dispatcher.filters.state import State, StatesGroup

# class ST (StatesGroup):
#     Menu = State()
#     Buyer = State()
#     Salesman = State()
#     Applications = State()

class ST(StatesGroup):
    Menu = State("Menu")
    Salesman = State("Salesman")
    Buyer = State("Buyer")
    Applications = State("Applications")
