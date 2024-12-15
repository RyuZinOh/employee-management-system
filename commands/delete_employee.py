from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from models.employee import Employee

NAME, CONTACT, CONFIRMATION = range(3)

async def start_delete_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please provide the name of the employee you want to delete:")
    return NAME

async def ask_contact_for_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text
    context.user_data['name'] = name
    employees = Employee.get_employees_by_name(name=name)
    
    if not employees:
        await update.message.reply_text("No employee found with that name.")
        return ConversationHandler.END
    
    if len(employees) == 1:
        contact = employees[0]['contact']
        context.user_data['contact'] = contact
        confirmation_message = f"Are you sure you want to delete the employee with the name {name} and contact {contact}? Reply with 'yes' to confirm or 'no' to cancel."
        await update.message.reply_text(confirmation_message)
        return CONFIRMATION
    else:
        await update.message.reply_text("Multiple employees found with that name. Please provide the contact number to narrow it down:")
        return CONTACT

async def ask_contact_and_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.text
    context.user_data['contact'] = contact
    employees = Employee.get_employees_by_name(contact=contact)

    if not employees:
        await update.message.reply_text("No employee found with that contact number.")
        return ConversationHandler.END
    
    context.user_data['employees'] = employees
    await update.message.reply_text(
        f"Found the following employee(s) with the contact {contact}:\n"
        f"{', '.join([f'{emp['name']} ({emp['department']})' for emp in employees])}\n"
        "Reply 'yes' to confirm deletion or 'no' to cancel."
    )
    return CONFIRMATION

async def confirm_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirmation = update.message.text.lower()

    if confirmation == 'yes':
        contact = context.user_data['contact']
        employees = context.user_data['employees']
        
        for employee in employees:
            result = Employee.delete_employee(employee['contact'])
            if result:
                await update.message.reply_text(f"Employee {employee['name']} deleted successfully.")
            else:
                await update.message.reply_text(f"Failed to delete employee {employee['name']}.")
                
        return ConversationHandler.END
    else:
        await update.message.reply_text("Employee deletion cancelled.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Employee deletion cancelled.")
    return ConversationHandler.END

delete_employee_conversation = ConversationHandler(
    entry_points=[CommandHandler('delete_employee', start_delete_employee)],
    states={
        NAME: [MessageHandler(filters.Text() & ~filters.Command(), ask_contact_for_delete)],
        CONTACT: [MessageHandler(filters.Text() & ~filters.Command(), ask_contact_and_confirm)],
        CONFIRMATION: [MessageHandler(filters.Text() & ~filters.Command(), confirm_deletion)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
