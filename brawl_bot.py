#python brawl_bot.py       (to start)
#8071391254:AAEqBJ5q_KopysmQIOliFeY7JgL65Z4cxeU
import json
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

CHOOSE_RARITY, CHOOSE_CHARACTER = range(2)

def load_characters_data():
    with open("characters_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

characters_data = load_characters_data()

rarities = [
    ("Common", "common"),
    ("Rare", "rare"),
    ("Super Rare", "super_rare"),
    ("Epic", "epic"),
    ("Mythic", "mythic"),
    ("Legendary", "legendary"),
]

CHARACTERS_PER_PAGE = 5

async def show_characters_page(query, characters_list, page_number, context):
    context.user_data["page_number"] = page_number

    start = page_number * CHARACTERS_PER_PAGE
    end = start + CHARACTERS_PER_PAGE

    page_characters = characters_list[start:end]

    #veidojam pogas katram varonim lapā
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"character:{name}")]
        for name in page_characters
    ]

    pagination_buttons = []

    #pievienojam pogu "iepriekšējā lapa", ja nav pirmajā lapā
    if page_number > 0:
        pagination_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"previous:{page_number - 1}"))

    #pievienojam pogu "nākamā lapa", ja vēl ir varoņi
    if end < len(characters_list):
        pagination_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"next:{page_number + 1}"))

    #ja eksistē pārlapošanas pogas, pievienojam tās
    if pagination_buttons:
        keyboard.append(pagination_buttons)

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_rarity")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.message.delete()
    except:
        pass

    await query.message.chat.send_message(
        "Choose a character from rarity: " + context.user_data['rarity'].replace('_', ' ').title(),
        reply_markup=reply_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in rarities]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose character rarity:", reply_markup=reply_markup)
    return CHOOSE_RARITY

async def rarity_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    rarity = query.data
    context.user_data["rarity"] = rarity

    #atlasām varoņus pēc izvēlētā retuma
    characters_list = [name for name, data in characters_data.items() if data["rarity"] == rarity]

    #ja nav atrasts neviens varonis, izbeidzam sarunu
    if not characters_list:
        await query.edit_message_text("No characters found for this rarity.")
        return ConversationHandler.END

    await show_characters_page(query, characters_list, page_number=0, context=context)
    return CHOOSE_CHARACTER

async def build_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    #pārbaudām, vai lietotājs vēlas lapot uz priekšu vai atpakaļ
    if data.startswith("next:") or data.startswith("previous:"):
        page_number = int(data.split(":")[1])
        rarity = context.user_data.get("rarity")

        #filtrējam varoņus ar izvēlēto retumu
        characters_list = [name for name, char_data in characters_data.items() if char_data["rarity"] == rarity]

        await show_characters_page(query, characters_list, page_number, context)
        return CHOOSE_CHARACTER

    #lietotājs izvēlējās atgriezties pie retuma izvēles
    if data == "back_to_rarity":
        try:
            await query.message.delete()
        except:
            pass
        keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in rarities]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.chat.send_message("Choose character rarity:", reply_markup=reply_markup)
        return CHOOSE_RARITY

    #lietotājs atgriežas uz varoņu lapu
    elif data == "back_to_characters":
        rarity = context.user_data.get("rarity")
        page_number = context.user_data.get("page_number", 0)

        #atlasām visus varoņus ar šo retumu
        characters_list = [name for name, char_data in characters_data.items() if char_data["rarity"] == rarity]

        await show_characters_page(query, characters_list, page_number, context)
        return CHOOSE_CHARACTER

    #lietotājs izvēlējās konkrētu varoni
    elif data.startswith("character:"):
        character = data.split(":", 1)[1]
        build_info = characters_data.get(character)

        #ja nav build informācijas, izbeidzam sarunu
        if not build_info:
            await query.edit_message_text("Build not found.")
            return ConversationHandler.END

        build_text = "\n".join(build_info.get("builds", []))
        description = build_info.get("description", "")
        image_url = build_info.get("image", "")

        caption = f"Build for {character}:\n{build_text}\n\n{description}"

        #saīsina parāk garus ziņojumus
        if len(caption) > 1024:
            caption = caption[:1020] + "..."

        keyboard = [
            [InlineKeyboardButton("🔙 Back to characters", callback_data="back_to_characters")],
            [InlineKeyboardButton("🔄 Start over", callback_data="back_to_rarity")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await query.message.delete()
        except:
            pass

        await query.message.chat.send_photo(photo=image_url, caption=caption, reply_markup=reply_markup)
        return CHOOSE_CHARACTER

    await query.edit_message_text("Unknown action.")
    return ConversationHandler.END

def main():
    application = Application.builder().token("8071391254:AAEqBJ5q_KopysmQIOliFeY7JgL65Z4cxeU").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_RARITY: [CallbackQueryHandler(rarity_selected)],
            CHOOSE_CHARACTER: [CallbackQueryHandler(build_selected)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
