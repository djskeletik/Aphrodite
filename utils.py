from aiogram.dispatcher.filters.state import State, StatesGroup

class ST(StatesGroup):
    Menu = State("Menu")
    Salesman = State("Salesman")
    Buyer = State("Buyer")
    Application_viewer = State("Application_viewer")
    Application_register = State("Application_register")
    Applications_Buyer = State("Applications_Buyer")
    Applications_Salesman = State("Applications_Salesman")