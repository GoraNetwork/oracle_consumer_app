from pyteal import *

def clear_state_program():
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)