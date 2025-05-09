def string_input(prompt_text, lower=False, upper=False, correct_values=None, default_value=None):
    while True:
        try:
            user_input = str(input(prompt_text))
            user_input = user_input.lower() if lower else user_input.upper() if upper else user_input
            if correct_values is None: return user_input
            if user_input in correct_values: return user_input
            if default_value is not None: return default_value
            print("Invalid Input!")
        except ValueError:
            if default_value is not None: return default_value
            print("Invalid number!")


def int_input(prompt_text, correct_values=None, default_value=None):
    while True:
        try:
            user_input = int(input(prompt_text))
            if correct_values is None: return user_input
            if user_input in correct_values: return user_input
            if default_value is not None: return default_value
            print("Invalid Input!")
        except ValueError:
            if default_value is not None: return default_value
            print("Invalid number!")


def float_input(prompt_text, correct_values=None, default_value=None):
    while True:
        try:
            user_input = float(input(prompt_text))
            if correct_values is None: return user_input
            if user_input in correct_values: return user_input
            if default_value is not None: return default_value
            print("Invalid Input!")
        except ValueError:
            if default_value is not None: return default_value
            print("Invalid number!")


def bool_input(prompt_text):
    while True:
        if len(prompt_text) == 0: return False

        try:
            user_input = str(input(prompt_text))
            if user_input.lower() in ["y", "yes"]: return True
            return False
        except ValueError:
            pass

        try:
            user_input = int(input(prompt_text))
            if user_input == 1: return True
            if user_input == 0: return False
        except ValueError:
            print("Invalid input!")
