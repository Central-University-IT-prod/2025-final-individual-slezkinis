from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.models import TgUser

def get_campaigns_keyboard(tg_user: TgUser, page=1):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Создать кампанию', callback_data=f'how_create_campaign'))
    row = []
    for i, campaign in enumerate(tg_user.adververtiser.campaigns.all()[10*(page-1):10*page], 1):
        row.append(InlineKeyboardButton(text=campaign.ad_title, callback_data=f'view_campaign_{campaign.campaign_id}'))
        if i % 2 == 0:
            keyboard.add(*row)
            row = []
    if row:
        keyboard.add(*row)
    if page > 1:
        keyboard.add(InlineKeyboardButton(text='<<', callback_data=f'campaigns_{page-1}'))
    if len(tg_user.adververtiser.campaigns.all()[10*(page-1):]) > 10:
        keyboard.add(InlineKeyboardButton(text='>>', callback_data=f'campaigns_{page+1}'))
    return keyboard


def get_main_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Кампании', callback_data=f'campaigns_1'))
    keyboard.add(InlineKeyboardButton(text='Cтатистика', callback_data=f'advertiser_stat'))
    return keyboard