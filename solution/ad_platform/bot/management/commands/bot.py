from django.core.management.base import BaseCommand
from django.core.cache import cache
from telebot import TeleBot
from io import BytesIO
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from bot.models import TgUser, Advertiser
from ._keyboards import get_campaigns_keyboard, get_main_keyboard

from campaigns.serializers import CampaignSerializer


class Command(BaseCommand):
    help = "Tg bot"

    def handle(self, *args, **options):
        start_bot()


users_and_campaigns = dict()

def start_bot():
    bot = TeleBot('REDACTED')
    logging.debug("STARTED")


    @bot.message_handler(commands=['start'])
    def start(message):
        tg_user, created = TgUser.objects.get_or_create(tg_id=message.chat.id)
        if created or tg_user.adververtiser is None:
            bot.send_message(message.chat.id, 'Укажите ID рекламодателя!')
            bot.register_next_step_handler(message, get_advertiser)
            return
        keyboard = get_main_keyboard()
        bot.send_message(message.chat.id, 'Здравствуйте!', reply_markup=keyboard)

    def get_advertiser(message):
        try:
            advertiser = Advertiser.objects.get(advertiser_id=message.text)
        except:
            bot.send_message(message.chat.id, 'Такого рекламодателя не существует!')
            bot.register_next_step_handler(message, get_advertiser)
            return
        if TgUser.objects.filter(adververtiser=advertiser).exists():
            bot.send_message(message.chat.id, 'Рекламодатель уже зарегистрирован! Проерьте данные!')
            bot.register_next_step_handler(message, get_advertiser)
            return
        tg_user = TgUser.objects.get(tg_id=message.chat.id)
        tg_user.adververtiser = advertiser
        tg_user.save()
        keyboard = get_main_keyboard()
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data.startswith('campaigns_'))
    def get_campaigns(message):
        page = int(message.data.split("_")[1])
        keyboard = get_campaigns_keyboard(TgUser.objects.get(tg_id=message.message.chat.id), page)
        bot.edit_message_text(text='Кампании', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data == "how_create_campaign")
    def create_campaign(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'campaigns_1'))
        keyboard.add(InlineKeyboardButton(text='Загрузить в .json формате', callback_data=f'upload_json'))
        keyboard.add(InlineKeyboardButton(text='Создать с нуля', callback_data=f'create_campaign'))
        bot.edit_message_text(text='Выберите способ создания', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data == "upload_json")
    def upload_json(message):
        example = '''
{
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
  "targeting": {
    "gender": "MALE",
    "age_from": 0,
    "age_to": 0,
    "location": "string"
  }
}
'''
        bot.edit_message_text(text='Отправьте .json файл. Вот пример его содержимого:\n' + example, chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, upload_json_file)

    def upload_json_file(message):
        try:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file = BytesIO()
            file.write(downloaded_file)
            # file.close()
        except:
            bot.send_message(message.chat.id, 'Ошибка при загрузке файла!')
            bot.register_next_step_handler(message, upload_json_file)
            return
        file.seek(0)
        try:
            json_data = json.load(file)
        except:
            bot.send_message(message.chat.id, 'Ошибка при загрузке файла!')
            bot.register_next_step_handler(message, upload_json_file)
            return
        json_data["advertiser_id"] = TgUser.objects.get(tg_id=message.chat.id).adververtiser.advertiser_id
        serilizer = CampaignSerializer(data=json_data)
        if serilizer.is_valid():
            serilizer.save()
        else:
            bot.send_message(message.chat.id, 'Ошибка при обработке файла!')
            bot.register_next_step_handler(message, upload_json_file)
            return
        bot.send_message(message.chat.id, 'Кампания успешно загружена!')
        
    @bot.callback_query_handler(func=lambda m: m.data == "create_campaign")
    def create_campaign(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'how_create_campaign'))
        bot.edit_message_text(text='Введите название кампании', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)
        bot.register_next_step_handler(message.message, create_campaign_name)

    @bot.callback_query_handler(func=lambda m: m.data == "cancel_create_campaign")
    def cancel_create_campaign(message):
        global users_and_campaigns
        users_and_campaigns.pop(message.message.chat.id)
        keyboard = get_main_keyboard()
        bot.edit_message_text(text='Создание кампании отменено!', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    def create_campaign_name(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        users_and_campaigns[message.chat.id] = {"ad_title": message.text}
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите описание кампании', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_description)

    def create_campaign_description(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        users_and_campaigns[message.chat.id]["ad_text"] = message.text
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите цену за клик', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_cost_per_click)

    def create_campaign_cost_per_click(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            cost_per_click = float(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_cost_per_click)
            return
        if cost_per_click < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message, create_campaign_cost_per_click)
            return
        users_and_campaigns[message.chat.id]["cost_per_click"] = int(message.text)
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите цену за просмотр', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_cost_per_impression)

    def create_campaign_cost_per_impression(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            cost_per_impression = float(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_cost_per_impression)
            return
        if cost_per_impression < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message, create_campaign_cost_per_impression)
            return
        users_and_campaigns[message.chat.id]["cost_per_impression"] = int(message.text)
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите желаемое количество показов', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_desired_impressions)

    def create_campaign_desired_impressions(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            desired_impressions = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_desired_impressions)
            return
        if desired_impressions < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message, create_campaign_desired_impressions)
            return
        users_and_campaigns[message.chat.id]["impressions_limit"] = int(message.text)
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите желаемое количество кликов', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_desired_clicks)

    def create_campaign_desired_clicks(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            desired_clicks = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_desired_clicks)
            return
        if desired_clicks < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message, create_campaign_desired_clicks)
            return
        users_and_campaigns[message.chat.id]["clicks_limit"] = int(message.text)
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите дату начала кампании', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_start_date)

    def create_campaign_start_date(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            start_date = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_start_date)
            return
        if start_date < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message, create_campaign_start_date)
            return
        if start_date < cache.get('time', 0):
            bot.send_message(message.chat.id, 'Введите дату в будущем!')
            bot.register_next_step_handler(message, create_campaign_start_date)
            return
        users_and_campaigns[message.chat.id]["start_date"] = int(message.text)
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите дату окончания кампании', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_end_date)
    
    def create_campaign_end_date(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            end_date = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_end_date)
            return
        if end_date < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message, create_campaign_end_date)
            return
        if end_date < cache.get('time', 0):
            bot.send_message(message.chat.id, 'Введите дату в будущем!')
            bot.register_next_step_handler(message, create_campaign_end_date)
            return
        if end_date < users_and_campaigns[message.chat.id]["start_date"]:
            bot.send_message(message.chat.id, 'Введите дату в будущем!')
            bot.register_next_step_handler(message, create_campaign_end_date)
            return
        users_and_campaigns[message.chat.id]["end_date"] = int(message.text)
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите гендер пользователя в формате (1 - мужской, 2 - женский, 0 - любой)', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_gender)

    def create_campaign_gender(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            gender = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_gender)
            return
        if gender < 0 or gender > 2:
            bot.send_message(message.chat.id, 'Введите число в диапазоне от 1 до 2!')
            bot.register_next_step_handler(message, create_campaign_gender)
            return
        genders = {
            1: 'MALE',
            2: 'FEMALE',
            0: 'ALL'
        }
        users_and_campaigns[message.chat.id]["targeting"] = {}
        users_and_campaigns[message.chat.id]["targeting"]["gender"] = genders[gender]
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите нижний порог пользователя возраста пользователя в формате (от 0 до 100). Если не хотите указывать нижний порог, введите -1', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_age_from)

    def create_campaign_age_from(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            age_from = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_age_from)
            return
        if age_from < -1 or age_from > 100:
            bot.send_message(message.chat.id, 'Введите число в диапазоне от -1 до 100!')
            bot.register_next_step_handler(message, create_campaign_age_from)
            return
        if age_from == -1:
            users_and_campaigns[message.chat.id]["targeting"]["age_from"] = None
        else:
            users_and_campaigns[message.chat.id]["targeting"]["age_from"] = age_from
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, "Введите верхний порог пользователя в формате (от 0 до 100). Если не хотите указывать верхний порог, введите -1", reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_age_to)

    def create_campaign_age_to(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        try:
            age_to = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите целое число!')
            bot.register_next_step_handler(message, create_campaign_age_to)
            return
        if age_to < -1 or age_to > 100:
            bot.send_message(message.chat.id, 'Введите число в диапазоне от -1 до 100!')
            bot.register_next_step_handler(message, create_campaign_age_to)
            return
        if users_and_campaigns[message.chat.id]["targeting"]["age_from"] is not None and age_to < users_and_campaigns[message.chat.id]["targeting"]["age_from"]:
            bot.send_message(message.chat.id, 'Введите верхний порог больше нижнего!')
            bot.register_next_step_handler(message, create_campaign_age_to)
            return
        if age_to == -1:
            users_and_campaigns[message.chat.id]["targeting"]["age_to"] = None
        else:
            users_and_campaigns[message.chat.id]["targeting"]["age_to"] = age_to
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        bot.send_message(message.chat.id, 'Введите локацию пользователя. Если не хотите указывать локацию, введите -1', reply_markup=keyboard)
        bot.register_next_step_handler(message, create_campaign_location)

    def create_campaign_location(message):
        global users_and_campaigns
        keyboard = InlineKeyboardMarkup()
        if message.text == '-1':
            users_and_campaigns[message.chat.id]["targeting"]["location"] = None
        else:
            users_and_campaigns[message.chat.id]["targeting"]["location"] = message.text
        text = ""
        text += f"Название: {users_and_campaigns[message.chat.id]['ad_title']}\n"
        text += f"Описание: {users_and_campaigns[message.chat.id]['ad_text']}\n"
        text += f"Цена за клик: {users_and_campaigns[message.chat.id]['cost_per_click']}\n"
        text += f"Цена за показ: {users_and_campaigns[message.chat.id]['cost_per_impression']}\n"
        text += f"Дата начала: {users_and_campaigns[message.chat.id]['start_date']}\n"
        text += f"Дата окончания: {users_and_campaigns[message.chat.id]['end_date']}\n"
        text += f"Желаемое количество показов: {users_and_campaigns[message.chat.id]['impressions_limit']}\n"
        text += f"Желаемое количество кликов: {users_and_campaigns[message.chat.id]['clicks_limit']}\n"
        text += "\nТаргетинг:\n" if users_and_campaigns[message.chat.id]["targeting"]["location"] or users_and_campaigns[message.chat.id]["targeting"]["gender"] or users_and_campaigns[message.chat.id]["targeting"]["age_from"] is not None or users_and_campaigns[message.chat.id]["targeting"]["age_to"] is not None else ""
        text += f"  Местоположение: {users_and_campaigns[message.chat.id]['targeting']['location']}\n" if users_and_campaigns[message.chat.id]["targeting"]["location"] else ""
        text += f"  Пол: {users_and_campaigns[message.chat.id]['targeting']['gender']}\n" if users_and_campaigns[message.chat.id]["targeting"]["gender"] else ""
        text += f"  Возраст:\n" if users_and_campaigns[message.chat.id]["targeting"]["age_from"] is not None or users_and_campaigns[message.chat.id]["targeting"]["age_to"] is not None else ""
        text += f"      От: {users_and_campaigns[message.chat.id]['targeting']['age_from']}\n" if users_and_campaigns[message.chat.id]["targeting"]["age_from"] is not None else ""
        text += f"      До: {users_and_campaigns[message.chat.id]['targeting']['age_to']}\n" if users_and_campaigns[message.chat.id]["targeting"]["age_to"] is not None else ""

        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_create_campaign'))
        keyboard.add(InlineKeyboardButton(text='Записать', callback_data=f'create_campaign_save'))
        bot.send_message(message.chat.id, 'Проверьте введенные данные и нажмите "Записать"\n' + text, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data == "create_campaign_save")
    def create_campaign_save(message):
        global users_and_campaigns
        tg_user = TgUser.objects.get(tg_id=message.message.chat.id)
        users_and_campaigns[message.message.chat.id]["advertiser_id"] = tg_user.adververtiser.advertiser_id
        serializer = CampaignSerializer(data=users_and_campaigns[message.message.chat.id])
        if serializer.is_valid():
            campaign = serializer.save()
        else:
            bot.send_message(message.message.chat.id, 'Произошла ошибка при сохранении кампании!')
            return
        users_and_campaigns.pop(message.message.chat.id)
        keyboard = get_main_keyboard()
        bot.send_message(message.message.chat.id, 'Записано!', reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda m: m.data.startswith('view_campaign_'))
    def view_campaign(message):
        campaign_id = message.data.split("_")[2]
        campaign = TgUser.objects.get(tg_id=message.message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Редактировать', callback_data=f'what_edit_campaign_{campaign.campaign_id}'), InlineKeyboardButton(text='Удалить', callback_data=f'check_delete_campaign_{campaign.campaign_id}'))
        keyboard.add(InlineKeyboardButton(text='Cтатистика', callback_data=f'stat_campaign_{campaign.campaign_id}'))
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'campaigns_1'))

        # Основная информация о кампании
        text = ""
        text += f"Название: {campaign.ad_title}\n"
        text += f"Описание: {campaign.ad_text}\n"
        text += f"Цена за клик: {campaign.cost_per_click}\n"
        text += f"Цена за показ: {campaign.cost_per_impression}\n"
        text += f"Дата начала: {campaign.start_date}\n"
        text += f"Дата окончания: {campaign.end_date}\n"
        text += f"Желаемое количество показов: {campaign.impressions_limit}\n"
        text += f"Желаемое количество кликов: {campaign.clicks_limit}\n"
        text += "\nТаргетинг:\n" if campaign.location or campaign.gender or campaign.age_from is not None or campaign.age_to is not None else ""
        text += f"  Местоположение: {campaign.location}\n" if campaign.location else ""
        text += f"  Пол: {campaign.gender}\n" if campaign.gender else ""
        text += f"  Возраст:\n" if campaign.age_from is not None or campaign.age_to is not None else ""
        text += f"      От: {campaign.age_from}\n" if campaign.age_from is not None else ""
        text += f"      До: {campaign.age_to}\n" if campaign.age_to is not None else ""
        bot.edit_message_text(text=text, chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data.startswith('check_delete_campaign_'))
    def check_delete_campaign(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Да', callback_data=f'delete_campaign_{message.data.split("_")[3]}_yes'), InlineKeyboardButton(text='Нет', callback_data=f'view_campaign_{message.data.split("_")[3]}'))

        bot.edit_message_text(text='Удалить кампанию?', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data.startswith('delete_campaign_'))
    def delete_campaign(message):
        campaign_id = message.data.split("_")[2]
        campaign = TgUser.objects.get(tg_id=message.message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.delete()
        keyboard = get_main_keyboard()
        bot.edit_message_text(text='Кампания удалена!', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)
    
    @bot.callback_query_handler(func=lambda m: m.data.startswith('what_edit_campaign_'))
    def edit_campaign(message):
        campaign_id = message.data.split("_")[3]
        campaign = TgUser.objects.get(tg_id=message.message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        text = ""
        text += f"Название: {campaign.ad_title}\n"
        text += f"Описание: {campaign.ad_text}\n"
        text += f"Цена за клик: {campaign.cost_per_click}\n"
        text += f"Цена за показ: {campaign.cost_per_impression}\n"
        text += f"Дата начала: {campaign.start_date}\n"
        text += f"Дата окончания: {campaign.end_date}\n"
        text += f"Желаемое количество показов: {campaign.impressions_limit}\n"
        text += f"Желаемое количество кликов: {campaign.clicks_limit}\n"
        text += "\nТаргетинг:\n" if campaign.location or campaign.gender or campaign.age_from is not None or campaign.age_to is not None else ""
        text += f"  Местоположение: {campaign.location}\n" if campaign.location else ""
        text += f"  Пол: {campaign.gender}\n" if campaign.gender else ""
        text += f"  Возраст:\n" if campaign.age_from is not None or campaign.age_to is not None else ""
        text += f"      От: {campaign.age_from}\n" if campaign.age_from is not None else ""
        text += f"      До: {campaign.age_to}\n" if campaign.age_to is not None else ""
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        keyboard.row(InlineKeyboardButton(text='Название', callback_data=f"name_{campaign.campaign_id}"), InlineKeyboardButton(text='Описание', callback_data=f"text_{campaign.campaign_id}"))
        keyboard.row(InlineKeyboardButton(text="Цена за клик", callback_data=f"cost_per_click_{campaign.campaign_id}"), InlineKeyboardButton(text="Цена за показ", callback_data=f"cost_per_impression_{campaign.campaign_id}"))
        keyboard.row(InlineKeyboardButton(text="Местоположение", callback_data=f"location_{campaign.campaign_id}"), InlineKeyboardButton(text="Пол", callback_data=f"gender_{campaign.campaign_id}"))
        keyboard.row(InlineKeyboardButton(text="Возраст с", callback_data=f"age_from_{campaign.campaign_id}"), InlineKeyboardButton(text="Возраст до", callback_data=f"age_to_{campaign.campaign_id}"))
        bot.edit_message_text(text="Выберите что хотите изменить:\n" + text, chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)
    @bot.callback_query_handler(func=lambda m: m.data.startswith('name_'))
    def edit_name(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text(text='Введите название кампании', chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_name_ok, message.data.split("_")[1])
    
    def edit_name_ok(message, campaign_id):
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.ad_title = message.text
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda m: m.data.startswith('text_'))
    def edit_text(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text(text='Введите описание кампании', chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_text_ok, message.data.split("_")[1])
    
    def edit_text_ok(message, campaign_id):
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.ad_text = message.text
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)

    
    @bot.callback_query_handler(func=lambda m: m.data.startswith("cost_per_click_"))
    def edit_cost_per_click(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text(text='Введите цену за клик', chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_cost_per_click_ok, message.data.split("_")[3])
    
    def edit_cost_per_click_ok(message, campaign_id):
        try:
            cost_per_click = float(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите число!')
            bot.register_next_step_handler(message.message, edit_cost_per_click_ok)
            return
        if cost_per_click < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message.message, edit_cost_per_click_ok)
            return
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.cost_per_click = cost_per_click
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)

    
    @bot.callback_query_handler(func=lambda m: m.data.startswith("cost_per_impression_"))
    def edit_cost_per_impression(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text(text='Введите цену за показ', chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_cost_per_impression_ok, message.data.split("_")[3])
    
    def edit_cost_per_impression_ok(message, campaign_id):
        try:
            cost_per_impression = float(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите число!')
            bot.register_next_step_handler(message.message, edit_cost_per_impression_ok)
            return
        if cost_per_impression < 0:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message.message, edit_cost_per_impression_ok)
            return
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.cost_per_impression = cost_per_impression
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda m: m.data.startswith("location_"))
    def edit_location(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text(text='Введите локацию, если не хотите убрать ограничение, введите -1', chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_location_ok, message.data.split("_")[1])

    def edit_location_ok(message, campaign_id):
        location = message.text
        if location == "-1":
            location = None
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.location = location
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)

    
    @bot.callback_query_handler(func=lambda m: m.data.startswith("gender_"))
    def edit_gender(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text('Введите гендер пользователя в формате (1 - мужской, 2 - женский, 0 - любой)', chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_gender_ok, message.data.split("_")[1])

    def edit_gender_ok(message, campaign_id):
        try:
            gender = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите число!')
            bot.register_next_step_handler(message.message, edit_gender_ok)
            return
        if gender < 0 or gender > 2:
            bot.send_message(message.chat.id, 'Введите число от 0 до 2!')
            bot.register_next_step_handler(message.message, edit_gender_ok)
            return
        genders = {
            0: 'ALL',
            1: 'MALE',
            2: 'FEMALE'
        }
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.gender = genders[gender]
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)

    
    @bot.callback_query_handler(func=lambda m: m.data.startswith("age_from_"))
    def edit_age_from(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text('Введите минимальный возраст, если не хотите убрать ограничение, введите -1', chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_age_from_ok, message.data.split("_")[2])

    
    def edit_age_from_ok(message, campaign_id):
        try:
            age_from = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите число!')
            bot.register_next_step_handler(message.message, edit_age_from_ok)
            return
        if age_from < -1:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message.message, edit_age_from_ok)
            return
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        campaign.age_from = age_from if age_from != -1 else None
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))
        bot.send_message(message.chat.id, 'Записано!', reply_markup=keyboard)

    
    @bot.callback_query_handler(func=lambda m: m.data.startswith("age_to_"))
    def edit_age_to(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'what_edit_campaign_{message.data.split("_")[1]}'))
        bot.edit_message_text("Введите максимальный возраст, если не хотите убрать ограничение, введите -1", chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.register_next_step_handler(message.message, edit_age_to_ok, message.data.split("_")[2])

    def edit_age_to_ok(message, campaign_id):
        try:
            age_to = int(message.text)
        except:
            bot.send_message(message.chat.id, 'Введите число!')
            bot.register_next_step_handler(message.message, edit_age_to_ok)
            return
        if age_to < -1:
            bot.send_message(message.chat.id, 'Введите положительное число!')
            bot.register_next_step_handler(message.message, edit_age_to_ok)
            return
        campaign = TgUser.objects.get(tg_id=message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        if age_to != -1 and campaign.age_from is not None and age_to < campaign.age_from:
            bot.send_message(message.chat.id, 'Максимальный возраст не может быть меньше минимального!')
            bot.register_next_step_handler(message.message, edit_age_to_ok)
            return
        campaign.age_to = age_to if age_to != -1 else None
        campaign.save()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign.campaign_id}'))

    @bot.callback_query_handler(func=lambda m: m.data.startswith("stat_campaign_"))
    def stat_campaign(message):
        campaign_id = message.data.split("_")[2]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'view_campaign_{campaign_id}'))
        keyboard.add(InlineKeyboardButton(text='Cтатистика за всё время', callback_data=f'all_stat_campaign_{campaign_id}'))
        keyboard.add(InlineKeyboardButton(text='Cтатистика по дням', callback_data=f'daily_stat_campaign_{campaign_id}'))
        bot.edit_message_text('Статистика кампании', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data.startswith("all_stat_campaign_"))
    def all_stat_campaign(message):
        campaign_id = message.data.split("_")[3]
        campaign = TgUser.objects.get(tg_id=message.message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'stat_campaign_{campaign_id}'))
        immersive_count = campaign.views.all().count()
        clicks_count = campaign.clicks.all().count()
        spent_impressions = sum([view.price for view in campaign.views.all()])
        spent_clicks = sum([click.price for click in campaign.clicks.all()])
        response = {
            "immersive_count": immersive_count,
            "clicks_count": clicks_count,
            "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
            "spent_impressions": spent_impressions,
            "spent_clicks": spent_clicks,
            "total": spent_impressions + spent_clicks
        }
        text = ""
        text += f"Количество показов: {immersive_count}\n"
        text += f"Количество кликов: {clicks_count}\n"
        text += f"Конверсия: {response['conversion']}%\n"
        text += f"Потрачено на показы: {spent_impressions}\n"
        text += f"Потрачено на клики: {spent_clicks}\n"
        text += f"Всего потрачено: {response['total']}"
        bot.edit_message_text(text=text, chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)
    
    @bot.callback_query_handler(func=lambda m: m.data.startswith("daily_stat_campaign_"))
    def daily_stat_campaign(message):
        campaign_id = message.data.split("_")[3]
        campaign = TgUser.objects.get(tg_id=message.message.chat.id).adververtiser.campaigns.get(campaign_id=campaign_id)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'stat_campaign_{campaign_id}'))
        response = []
        for time in range(0, cache.get('time', 0) + 1):
            immersive_count = campaign.views.filter(date=time).count()
            clicks_count = campaign.clicks.filter(date=time).count()
            spent_impressions = sum([view.price for view in campaign.views.filter(date=time)])
            spent_clicks = sum([click.price for click in campaign.clicks.filter(date=time)])
            response_for_date = {
                "immersive_count": immersive_count,
                "clicks_count": clicks_count,
                "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
                "spent_impressions": spent_impressions,
                "spent_clicks": spent_clicks,
                "total": spent_impressions + spent_clicks,
                "date": time
            }
            response.append(response_for_date)
        text = ""
        for date in response:
            text += f"Дата: {date['date']}\n"
            text += f"  Количество показов: {date['immersive_count']}\n"
            text += f"  Количество кликов: {date['clicks_count']}\n"
            text += f"  Конверсия: {date['conversion']}%\n"
            text += f"  Потрачено на показы: {date['spent_impressions']}\n"
            text += f"  Потрачено на клики: {date['spent_clicks']}\n"
            text += f"  Всего потрачено: {date['total']}\n"
            text += "\n"
        bot.edit_message_text(text=text, chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data == "advertiser_stat")
    def advertiser_stat(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Cтатистика за всё время', callback_data=f'all_stat_advertiser'))
        keyboard.add(InlineKeyboardButton(text='Cтатистика по дням', callback_data=f'daily_stat_advertiser'))
        bot.edit_message_text('Статистика рекламодателя', chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data == "all_stat_advertiser")
    def all_stat_advertiser(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'advertiser_stat'))
        advertiser = TgUser.objects.get(tg_id=message.message.chat.id).adververtiser
        campaigns = advertiser.campaigns.all()
        immersive_count = sum([campaign.views.all().count() for campaign in campaigns])
        clicks_count = sum([campaign.clicks.all().count() for campaign in campaigns])
        spent_impressions = sum([view.price for campaign in campaigns for view in campaign.views.all()])
        spent_clicks = sum([click.price for campaign in campaigns for click in campaign.clicks.all()])
        response = {
            "immersive_count": immersive_count,
            "clicks_count": clicks_count,
            "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
            "spent_impressions": spent_impressions,
            "spent_clicks": spent_clicks,
            "total": spent_impressions + spent_clicks
        }
        text = ""
        text += f"Количество показов: {immersive_count}\n"
        text += f"Количество кликов: {clicks_count}\n"
        text += f"Конверсия: {response['conversion']}%\n"
        text += f"Потрачено на показы: {spent_impressions}\n"
        text += f"Потрачено на клики: {spent_clicks}\n"
        text += f"Всего потрачено: {response['total']}"
        bot.edit_message_text(text=text, chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda m: m.data == "daily_stat_advertiser")
    def daily_stat_advertiser(message):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'advertiser_stat'))
        advertiser = TgUser.objects.get(tg_id=message.message.chat.id).adververtiser
        now = cache.get('time', 0)
        response = []
        for time in range(0, now + 1):
            immersive_count = sum([campaign.views.filter(date=time).count() for campaign in advertiser.campaigns.all()])
            clicks_count = sum([campaign.clicks.filter(date=time).count() for campaign in advertiser.campaigns.all()])
            spent_impressions = sum([view.price for campaign in advertiser.campaigns.all() for view in campaign.views.filter(date=time)])
            spent_clicks = sum([click.price for campaign in advertiser.campaigns.all() for click in campaign.clicks.filter(date=time)])
            response_for_date = {
                "immersive_count": immersive_count,
                "clicks_count": clicks_count,
                "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
                "spent_impressions": spent_impressions,
                "spent_clicks": spent_clicks,
                "total": spent_impressions + spent_clicks,
                "date": time
            }
            response.append(response_for_date)
        text = ""
        for date in response:
            text += f"Дата: {date['date']}\n"
            text += f"  Количество показов: {date['immersive_count']}\n"
            text += f"  Количество кликов: {date['clicks_count']}\n"
            text += f"  Конверсия: {date['conversion']}%\n"
            text += f"  Потрачено на показы: {date['spent_impressions']}\n"
            text += f"  Потрачено на клики: {date['spent_clicks']}\n"
            text += f"  Всего потрачено: {date['total']}\n"
            text += "\n"
        bot.edit_message_text(text=text, chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=keyboard)
    bot.polling()