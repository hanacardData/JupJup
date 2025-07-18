# test_cafeteria.py

from bot.services.cafeteria.menu import get_weekly_menu_message

if __name__ == "__main__":
    msg = get_weekly_menu_message()
    print(msg)
