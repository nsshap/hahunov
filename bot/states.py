from aiogram.fsm.state import State, StatesGroup


class CongratsFlow(StatesGroup):
    name   = State()
    city   = State()
    video  = State()
    message = State()
    advice = State()
