import sys

def foo():
    caller = sys._getframe(1).f_code.co_name
    print(f"Called from function: {caller}")

def bar():
    foo()

bar()