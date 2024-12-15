from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from models.employee import Employee

NAME, POSITION, CONTACT, SALARY, DEPARTMENT = range(5)

async def start_add_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please provide the employee's name:")
    return NAME

async def ask_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Please provide the employee's position:")
    return POSITION

async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['position'] = update.message.text
    await update.message.reply_text("Please provide the employee's contact:")
    return CONTACT

async def ask_salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['contact'] = update.message.text
    await update.message.reply_text("Please provide the employee's salary (optional):")
    return SALARY

async def ask_department(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['salary'] = update.message.text if update.message.text else None
    await update.message.reply_text("Please provide the employee's department (optional):")
    return DEPARTMENT

async def add_employee_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['department'] = update.message.text if update.message.text else None

    employee = Employee(
        context.user_data['name'],
        context.user_data['position'],
        context.user_data['contact'],
        context.user_data['salary'],
        context.user_data['department']
    )

    result = employee.save_to_db()

    if result:
        await update.message.reply_text(f"Employee {context.user_data['name']} added successfully.")
    else:
        await update.message.reply_text("Failed to add employee. Please try again.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Employee addition cancelled.")
    return ConversationHandler.END

add_employee_conversation = ConversationHandler(
    entry_points=[CommandHandler('add_employee', start_add_employee)],
    states={
        NAME: [MessageHandler(filters.Text() & ~filters.Command(), ask_position)],
        POSITION: [MessageHandler(filters.Text() & ~filters.Command(), ask_contact)],
        CONTACT: [MessageHandler(filters.Text() & ~filters.Command(), ask_salary)],
        SALARY: [MessageHandler(filters.Text() & ~filters.Command(), ask_department)],
        DEPARTMENT: [MessageHandler(filters.Text() & ~filters.Command(), add_employee_to_db)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
