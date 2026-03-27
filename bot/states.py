from aiogram.fsm.state import State, StatesGroup


class CongratsFlow(StatesGroup):
    name    = State()
    city    = State()
    videos  = State()
    message = State()
    advice  = State()
