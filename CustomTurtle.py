from turtle import Turtle, Screen
import time


def move_single_turtles_forward(turtle, amount, penup_on_start=False, pendown_on_finish=False, sleep=0):
    if penup_on_start: turtle.penup()
    turtle.forward(amount)
    if pendown_on_finish: turtle.pendown()
    time.sleep(sleep)


def goto_single_turtle(turtle, x, y, penup_on_start=False, pendown_on_finish=False, sleep=0):
    if penup_on_start: turtle.penup()
    turtle.goto(x, y)
    if pendown_on_finish: turtle.pendown()
    time.sleep(sleep)


class CustomTurtle:
    def __init__(self):
        self.c_screen = Screen()
        self.stored_turtles = []

    def add_onkeypress(self, func, key):
        self.c_screen.onkeypress(key=key, fun=func)

    def create_turtle(self, x=0, y=0, shape="square", color="#FFFFFF", penup=False):
        turtle = Turtle(shape=shape)
        turtle.color(color)
        if penup: turtle.penup()
        turtle.goto(x, y)
        self.add_turtle(turtle)
        return turtle

    def add_turtle(self, turtle):
        self.stored_turtles.append(turtle)
        return turtle

    def return_turtle_from_index(self, index):
        index = max(0, min(index, len(self.stored_turtles) - 1))
        return self.stored_turtles[index]

    def move_all_turtles_forward(self, amount, penup_on_start=False, pendown_on_finish=False, sleep=0):
        for turtle in self.stored_turtles:
            move_single_turtles_forward(turtle, amount, penup_on_start, pendown_on_finish, sleep=0)
        time.sleep(sleep)

    def goto_all_turtles_forward(self, x, y, penup_on_start=False, pendown_on_finish=False, sleep=0):
        for turtle in self.stored_turtles:
            goto_single_turtle(turtle, x, y, penup_on_start, pendown_on_finish, sleep=0)
        time.sleep(sleep)

    def start_screen(self, title="Title", width=600, height=600, bg="#000000", tracer=0):
        self.c_screen.title(title)
        self.c_screen.setup(width=width, height=height)
        self.c_screen.bgcolor(bg)
        self.c_screen.tracer(tracer)

    def return_colliding_turtles_with_distance(self, turtle, distance, include_self=False):
        colliding_turtles=[]
        for stored_turtle in self.stored_turtles:
            if stored_turtle is turtle and not include_self: continue
            if stored_turtle.distance(turtle) < distance: colliding_turtles.append(stored_turtle)
        return colliding_turtles

    def update_screen(self):
        self.c_screen.update()
