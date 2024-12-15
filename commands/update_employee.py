from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from models.employee import Employee

CONTACT, FIELD, NEW_VALUE = range(3)

async def start_update_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please provide the contact number of the employee you want to update:")
    return CONTACT

async def ask_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.text.strip()
    context.user_data['contact'] = contact
    
    employees = Employee.get_employees_by_contact(contact)
    
    if not employees:
        await update.message.reply_text("No employee found with that contact number.")
        return ConversationHandler.END
    
    context.user_data['employees'] = employees
    await update.message.reply_text(
        "Which field would you like to update?\n"
        "Options: name, position, salary, department\n"
        "Please choose one of the following:"
    )
    return FIELD

async def ask_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    field = update.message.text.lower()

    if field not in ["name", "position", "salary", "department"]:
        await update.message.reply_text("Invalid field. Please choose from: name, position, salary, department.")
        return FIELD
    
    context.user_data['field'] = field
    await update.message.reply_text(f"Please provide the new value for {field}:")
    return NEW_VALUE

async def update_employee_in_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_value = update.message.text.strip()
    field = context.user_data['field']
    contact = context.user_data['contact']

    update_data = {field: new_value}
    result = Employee.update_employee(contact, update_data)

    if result:
        await update.message.reply_text(f"Employee's {field} updated successfully.")
    else:
        await update.message.reply_text("Failed to update employee. Please try again.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Employee update cancelled.")
    return ConversationHandler.END

update_employee_conversation = ConversationHandler(
    entry_points=[CommandHandler('update_employee', start_update_employee)],
    states={
        CONTACT: [MessageHandler(filters.Text() & ~filters.Command(), ask_field)],
        FIELD: [MessageHandler(filters.Text() & ~filters.Command(), ask_new_value)],
        NEW_VALUE: [MessageHandler(filters.Text() & ~filters.Command(), update_employee_in_db)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
