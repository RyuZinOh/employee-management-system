from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from models.employee import Employee

NAME = 0

async def start_view_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please provide the employee's name:")
    return NAME

async def fetch_employee_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text
    employees = Employee.get_employees_by_name(name)

    if employees:
        employee_details = ""
        for emp in employees:
            employee_details += (
                f"<b>Employee Name:</b> {emp['name']}\n"
                f"<b>Position:</b> {emp['position']}\n"
                f"<b>Contact:</b> {emp['contact']}\n"
                f"<b>Department:</b> {emp.get('department', 'N/A')}\n"
                f"<b>Status:</b> {emp['status']}\n\n"
            )

        await update.message.reply_text(employee_details, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("No employees found with that name.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Employee search cancelled.")
    return ConversationHandler.END

view_employee_conversation = ConversationHandler(
    entry_points=[CommandHandler('view_employee', start_view_employee)],
    states={
        NAME: [MessageHandler(filters.Text() & ~filters.Command(), fetch_employee_by_name)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
