import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
load_dotenv()
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# List of jokes categorized
jokes = {
    "programmers": [
        "Чому програмісти не люблять природу? У ній забагато багів.",
        "Як програміст розважається на вечірці? Залишає всі труби відкритими.",
        "Як визначити хороший код? Якщо він не потребує коментарів — це код на Python!"
    ],
    "animals": [
        "Я спитав свого собаку, скільки буде два мінус два. Він сказав 'нічого'.",
        "Чому скелети не б'ються між собою? У них немає кишок!",
        "Як краб поздоровляється з другом? 'Здорово, дружище!'"
    ],
    "mood": [
        "Я сказав дружині, що вона малює брови занадто високо. Вона виглядала здивованою.",
        "Чому опудало отримало нагороду? Тому що воно було видатним у своєму полі!",
        "Моя настрій – це як Wi-Fi: спочатку ідеально, а потім просто зависає."
    ]
}

# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Стартувати", callback_data='start_jokes')],
        [InlineKeyboardButton("Додати жарт", callback_data='add_joke')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт, друже! Я твій новий веселий помічник! Обери опцію, щоб почати розваги 🎉:", reply_markup=reply_markup)

# Handle button press to show jokes and give rating options
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category = query.data
    if category == 'add_joke':
        # Request user to enter a new joke
        await query.answer()
        await query.edit_message_text("Ти хочеш поділитись своїм жартом? Напиши його тут!")
        return
    elif category == 'start_jokes':
        # Send the joke categories for the user to choose from
        await show_joke_categories(update, context)
        return
    elif category in ['programmers', 'animals', 'mood']:
        # Send a random joke from the selected category
        await show_random_joke(update, context)
        return

# Function to show joke categories (programmers, animals, mood)
async def show_joke_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Програмісти 👨‍💻", callback_data='programmers')],
        [InlineKeyboardButton("Тварини 🐾", callback_data='animals')],
        [InlineKeyboardButton("Для настрою 😄", callback_data='mood')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Оберіть категорію, і я розкажу тобі цікавий жарт 😎:", reply_markup=reply_markup)

# Handle category selection for showing a random joke
async def show_random_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category = query.data
    selected_joke = random.choice(jokes[category])  # Choose a random joke from the selected category
    
    # Add thumbs up/down buttons for rating the joke
    rating_keyboard = [
        [InlineKeyboardButton("👍 Це смішно!", callback_data=f"rate_{category}_thumb_up")],
        [InlineKeyboardButton("👎 Можна краще...", callback_data=f"rate_{category}_thumb_down")]
    ]
    rating_markup = InlineKeyboardMarkup(rating_keyboard)
    
    # Send the joke along with rating options
    await query.answer()  # Acknowledge the button click
    await query.edit_message_text(text=selected_joke, reply_markup=rating_markup)  # Update the message with the joke

# Handle rating submission (thumbs up or thumbs down)
async def rate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    rating = query.data.split("_")[2]  # Extract rating (thumb_up or thumb_down)
    category = query.data.split("_")[1]  # Extract category (programmers, animals, mood)
    
    # Send acknowledgment of the rating
    if rating == "thumb_up":
        await query.edit_message_text(text="Дякую за твою оцінку! Раді, що сподобалось! 🥳")
    else:
        await query.edit_message_text(text="Дякую за твою оцінку! Не переживай, наступний жарт буде ще кращим! 😅")

# Handle user input for new jokes
async def handle_joke_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    # Ask the user to select the category
    keyboard = [
        [InlineKeyboardButton("Програмісти 👨‍💻", callback_data='programmers')],
        [InlineKeyboardButton("Тварини 🐾", callback_data='animals')],
        [InlineKeyboardButton("Для настрою 😄", callback_data='mood')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть категорію для свого жарту, щоб я міг його додати:", reply_markup=reply_markup)
    
    # Save the user's joke temporarily until category is selected
    context.user_data['new_joke'] = user_message

# Handle category selection for new jokes
async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.callback_query.data
    new_joke = context.user_data.get('new_joke', None)
    
    if new_joke:
        # Add the joke to the selected category
        jokes[category].append(new_joke)
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(f"Готово! Твій жарт успішно додано до категорії '{category}'! 👍")
        # Clear the stored new joke after adding it
        del context.user_data['new_joke']
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Щось пішло не так. Спробуй знову. 😔")

# Main function
def main():
    """Start the bot."""
    BOT_TOKEN = os.getenv('token')  # Замініть на ваш токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Add /start command handler
    application.add_handler(CommandHandler("start", start))
    
    # Add button handler for when a user clicks a category
    application.add_handler(CallbackQueryHandler(button, pattern="^(programmers|animals|mood|add_joke|start_jokes)$"))
    
    # Add handler for rating submissions
    application.add_handler(CallbackQueryHandler(rate_joke, pattern="^rate_"))
    
    # Add handler for joke submissions
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_joke_submission))

    # Add handler for category selection for new jokes
    application.add_handler(CallbackQueryHandler(handle_category_selection, pattern="^(programmers|animals|mood)$"))

    # Start polling for updates
    print("Бот запущено! Починаємо веселитися! 🎉")
    application.run_polling()

if __name__ == '__main__':
    main()
