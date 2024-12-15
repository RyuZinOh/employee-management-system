import os
from dotenv import load_dotenv
from telegram.ext import Application
from commands.add_employee import add_employee_conversation
from commands.view_employee import view_employee_conversation
from commands.update_employee import update_employee_conversation  # Import the update handler
from commands.delete_employee import delete_employee_conversation


load_dotenv()

def main():
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        print("Error: BOT_TOKEN is not set in the .env file.")
        return

    application = Application.builder().token(bot_token).build()

    application.add_handler(add_employee_conversation)
    application.add_handler(view_employee_conversation)
    application.add_handler(update_employee_conversation)
    application.add_handler(delete_employee_conversation)
    application.run_polling()

if __name__ == "__main__":
    main()
