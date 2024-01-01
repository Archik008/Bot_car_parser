from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import *
from auto_browser import *
from change_filename import return_formatted_file_name

import time
import pickle

class TestStates(Helper):
    mode = HelperMode.snake_case

    TEST_STATE_0 = ListItem()
    TEST_STATE_1 = ListItem()#Ввод минимального года
    TEST_STATE_2 = ListItem()#Ввод максимального года
    TEST_STATE_3 = ListItem()#Ввод телефона


class GetLang(StatesGroup):
    lang = State()


bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
users_languages = {}


@dp.message_handler(state='*',commands = ["start"])     
async def choose_lang_message(message):
    await message.answer(hello_msg)
    time.sleep(2)
    lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for lang in languages:
        lang_kb.add(types.KeyboardButton(lang))
    await message.answer(choose_lang, reply_markup=lang_kb)
    await GetLang.lang.set()

@dp.message_handler(state='*', commands=['check_errors'])
async def checking_selenium_errors(msg):
    if msg.chat.id != 'My_developer_id':
       return
    with open('nohup.out', 'r', encoding='utf-8') as file:
       errors = file.read()
    if 'selenium' in errors:
       await msg.answer('Selenium error is here')
    else:
       await msg.answer('No selenium  errors:)')

@dp.message_handler(state=GetLang.lang)
async def get_lang(msg: types.Message):
    global users_languages
    if msg.text not in languages:
        await msg.answer(incorrect_lang_choice)
        return
    users_languages[msg.from_id] = msg.text
    eng_rus_menu = {languages[0]: ['Car search', 'How to buy', 'FAQ', 'Change language', 'Choose the action'], languages[1]: ['Подбор авто', 'Как купить', 'Частые вопросы', 'Сменить язык', 'Выберите действие']}
    state = dp.current_state(user=msg.from_user.id)

    await state.set_state(TestStates.all()[0])
    kb_return=ReplyKeyboardMarkup(resize_keyboard=True)
    btn_labels = eng_rus_menu.get(users_languages.get(msg.from_id))
    for btn_label in btn_labels:
        if btn_label != btn_labels[-1]:
            btn = KeyboardButton(btn_label)
            kb_return.add(btn)
    await msg.answer(btn_labels[-1],reply_markup=kb_return)
    await state.finish()

   
@dp.message_handler(state='*', commands=['start_choosing'])
async def start_changing(msg: types.Message):
    global users_languages

    user_lang = users_languages.get(msg.from_id)
    if not user_lang:
        lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for lang in languages:
            lang_kb.add(types.KeyboardButton(lang))
        await msg.answer(choose_lang_repeat, reply_markup=lang_kb)
        await GetLang.lang.set()
        return
    
    state = dp.current_state(user=msg.from_user.id)
    await state.set_state(TestStates.all()[0])
    kb_return = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_labels = eng_rus_menu.get(user_lang)
    for btn_label in btn_labels:
        if btn_label != btn_labels[-1]:
            btn = KeyboardButton(btn_label)
            kb_return.add(btn)
    await msg.answer(btn_labels[-1],reply_markup=kb_return)
    await state.finish()

def if_updated():
    list_auction=["Lawton Auto Auction","Mainheim Halifax"]
    for auction in list_auction:
        formatted_auction = return_formatted_file_name(auction)
        with open(f'data/{formatted_auction}_state.txt', 'r', encoding='utf-8') as file:
            state = file.read()
            file.close()
            if state == 'updating...':
                return False
    return True

def get_cars_by_model(auction, model):
    file_auction_name = return_formatted_file_name(auction)
    with open(f'data/{file_auction_name}.txt','rb+') as f:
         all_cars = pickle.loads(f.read())
    car_list = []
    for car in all_cars:
        if car['model'] == model:
            car_list.append(car)
    return car_list
 
@dp.message_handler(state=TestStates.TEST_STATE_1)
async def get_min_year(message: types.Message,state: FSMContext): #самый ранний год выпуска
    global users_languages

    user_lang = users_languages.get(message.from_id)
    if not user_lang:
        lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for lang in languages:
            lang_kb.add(types.KeyboardButton(lang))
        await message.answer(choose_lang_repeat, reply_markup=lang_kb)
        await GetLang.lang.set()
        return
    
    earliest_year_text = {languages[0]: ["Enter the earliest release year (as number)", 
                                         "Enter the latest release year"], 
                          languages[1]: ["Введите самый ранний год выпуска (числом)", 
                                         "Введите самый поздний год выпуска"]}
    texts = earliest_year_text.get(user_lang)
    try:
        year_min=int(message.text)
    except Exception as e:
        print(e)
        await bot.send_message(message.from_user.id, texts[0])
        return
    async with state.proxy() as data:
        data[message.from_user.id]["year_min"]=year_min
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(TestStates.all()[2])
    await bot.send_message(message.from_user.id, texts[1])
    
    


@dp.message_handler(state=TestStates.TEST_STATE_2)
async def get_max_year(message: types.Message,state: FSMContext): #самый поздний год выпуска
    global users_languages

    user_lang = users_languages.get(message.from_id)
    if not user_lang:
        lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for lang in languages:
            lang_kb.add(types.KeyboardButton(lang))
        await message.answer(choose_lang_repeat, reply_markup=lang_kb)
        await GetLang.lang.set()

    latest_year_text = {languages[0]: ["Enter the latest release year (as number)", 
                                       "The latest year cannot be less than the earliest, re-enter data",
                                       "Searching cars in database⏳", 
                                       "There is no cars, type other time interval or choose other car brand",
                                       "Choose a car:"],
                        languages[1]: ["Введите самый поздний год выпуска (числом)",
                                       "Самый поздний год не может быть меньше самого раннего, повторите ввод",
                                       "Ищем в базе подходящие авто⏳",
                                       "Результатов нет, выберите другую марку или измените интервал времени",
                                       "Выберите автомобиль:"]}
    texts = latest_year_text.get(user_lang)
    try:
        year_max=int(message.text)
    except Exception as e:
        print(e)
        await bot.send_message(message.from_user.id, texts[0])
        return
    async with state.proxy() as data:
        year_min= data[message.from_user.id]["year_min"]
        if year_min>year_max:
            await bot.send_message(message.from_user.id, texts[1])
            return
        else:
            data[message.from_user.id]["year_max"]=year_max
            auction=data[message.from_user.id]["auction"]
            brand=data[message.from_user.id]["brand"]
            model=data[message.from_user.id]["model"]
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(TestStates.all()[0])
    await bot.send_message(message.from_user.id, texts[2])
    car_list = get_cars_by_model(auction, model) 
    car_list_result=[]
    for i in car_list:
        if i["model"]==model:
            if int(i["year"])>=int(year_min):
                if int(i["year"])<=int(year_max):
                        car_list_result.append(i)
    if car_list_result==[]:
        await bot.send_message(message.from_user.id, texts[3])
        return
    car_list=car_list_result
    async with state.proxy() as data:
        data[message.from_user.id]["car_list"]=car_list

    inline_kb2 = InlineKeyboardMarkup()
    for car in car_list:
        text=car["info"]
        car_id=car["id_car"]
        inline_btn_1 = InlineKeyboardButton(text, callback_data='car-'+str(car_id))
        inline_kb2.add(inline_btn_1)
    await message.answer(texts[-1], reply_markup=inline_kb2)



@dp.message_handler(state=TestStates.TEST_STATE_3)
async def number(message: types.Message,state: FSMContext): #телефон
    tel=message.text
    async with state.proxy() as data:
        link=data[message.from_user.id]["link"]
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(TestStates.all()[0])
    client_id=message.from_user.id
    text="Номер телефона клиента: "
    text+=str(tel)
    try:
        client_name=message.from_user.first_name
        text=text+"\nИмя клиента: "+str(client_name)+"\n"
    except:
        pass
    try:
        client_username=message["from"]["username"]
    except Exception as e:
        print(e)
        pass
    if client_username==None:
        pass
    else:
        text=text+"Имя пользователя: @"+str(client_username)+"\n"
    text=text+"ID клиента: "+str(client_id)+"\nСсылка на авто: "+link
    if users_languages[message.from_id] == 'Russian(Русский)':
        await bot.send_message(admin_id,text)
        await bot.send_message(message.from_user.id,"Заявка отправлена - мы свяжемся с вами в течении часа")
    else:
        await bot.send_message(admin_id,text)
        await bot.send_message(message.from_user.id,"The application has been sent - we will contact you within an hour")


    
 
@dp.message_handler(state='*')     
async def in_start(message,state: FSMContext):
    global users_languages
    if message.text=="Подбор авто":
        users_languages[message.from_id] = 'Russian(Русский)'
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(TestStates.all()[0])
        text="Выберите аукцион"
        inline_kb2 = InlineKeyboardMarkup()
        inline_btn_1 = InlineKeyboardButton("Lawton Auto Auction", callback_data='auction-Lawton Auto Auction')
        inline_btn_2 = InlineKeyboardButton("Mainheim Halifax", callback_data='auction-Mainheim Halifax')
        inline_kb2.add(inline_btn_1).add(inline_btn_2)
        await message.answer(text,reply_markup=inline_kb2)
    if message.text == "Car search":
        users_languages[message.from_id] = 'English(Английский)'
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(TestStates.all()[0])
        text="Choose auction"
        inline_kb2 = InlineKeyboardMarkup()
        inline_btn_1 = InlineKeyboardButton("Lawton Auto Auction", callback_data='auction-Lawton Auto Auction')
        inline_btn_2 = InlineKeyboardButton("Mainheim Halifax", callback_data='auction-Mainheim Halifax')
        inline_kb2.add(inline_btn_1).add(inline_btn_2)
        await message.answer(text,reply_markup=inline_kb2)
    if message.text =='Change language' or message.text == 'Сменить язык':
       lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
       for lang in languages:
           lang_kb.add(types.KeyboardButton(lang))
       await message.answer(choose_lang, reply_markup=lang_kb)
       await GetLang.lang.set()
    if message.text == "FAQ":
        users_languages[message.from_id] = 'English(Английский)'
        await bot.send_message(message.from_user.id, text_question_eng)
    if message.text == "How to buy":
        users_languages[message.from_id] = 'English(Английский)'
        await bot.send_message(message.from_user.id, text_buy_eng)
    if message.text=="Частые вопросы":
        users_languages[message.from_id] = 'Russian(Русский)'
        await bot.send_message(message.from_user.id,text_question_rus)
    if message.text=="Как купить":
        users_languages[message.from_id] = 'Russian(Русский)'
        await bot.send_message(message.from_user.id,text_buy_rus)
        
        

    


@dp.callback_query_handler(state='*')
async def callback(callback_query: types.CallbackQuery,state: FSMContext):
    global users_languages
    code = callback_query.data
    code=code.split("-")
    user_lang = users_languages.get(callback_query.message.chat.id)

    if not user_lang:
       lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
       for lang in languages:
           lang_kb.add(types.KeyboardButton(lang))
       await callback_query.message.answer(choose_lang_repeat, reply_markup=lang_kb)
       await GetLang.lang.set()
       return
    
    if code[0]=="auction":
        choosing_brand_car = {languages[0]: ["There is no information about this auction. Choose other auction",
                                "Choose a brand of car:",
                                "Data is being updated at the moment, repeat the action later"],
                              languages[1]: ["Информации об этом аукционе не найдено. Повторите позже",
                                "Выберите марку",
                                "На данный момент идет обновление данных, повторите действие позже"]}
        choosing_brand_car_text = choosing_brand_car.get(user_lang)

        if not if_updated():
            await callback_query.message.answer(choosing_brand_car_text[-1])
            return
        auction=code[1]
        async with state.proxy() as data:
            data[callback_query.from_user.id]={"auction":auction,"brand":None,"year_min":None,"year_max":None}
        try:
            car_dict={}
            formatted_auction = return_formatted_file_name(auction) 
            with open(f'data/{formatted_auction}.txt','rb+') as f:
                text=f.read()
                car_dict[auction]=pickle.loads(text)
            brands=[]
            for i in car_dict[auction]:
                brands.append(i["brand"])
            brands=list(set(brands))
            brands.sort()
            #brands=brands_dict[auction]
        except Exception as e:
            print(e)
            await bot.send_message(callback_query.from_user.id, choosing_brand_car_text[0])
            return
        if (brands==None) or (brands==[]):
            await bot.send_message(callback_query.from_user.id, choosing_brand_car_text[0])
            return
        inline_kb2 = InlineKeyboardMarkup(row_width=3)
        for i in brands:
            inline_btn_1 = InlineKeyboardButton(i, callback_data='brand-'+str(i))
            inline_kb2.add(inline_btn_1)
        await callback_query.message.answer(choosing_brand_car_text[1],reply_markup=inline_kb2)

    if code[0]=="brand": #выбор марки
        choosing_model_car = {languages[0]: ["There is no information about this auction. Choose other auction",
                                "Select car model:",
                                "Data is being updated at the moment, repeat the action later"],
                              languages[1]: ["Информации об этом аукционе не найдено. Повторите позже",
                                "Выберите модель",
                                "На данный момент идет обновление данных, повторите действие позже"]}
        choosing_model_car_text = choosing_model_car.get(user_lang)
        if not if_updated():
            await callback_query.message.answer(choosing_model_car_text[-1])
            return
        brand=code[1]
        async with state.proxy() as data:
            data[callback_query.from_user.id]["brand"]=brand
            auction=data[callback_query.from_user.id]["auction"]
        car_dict={}
        file_auction_name = return_formatted_file_name(auction)
        with open(f'data/{file_auction_name}.txt','rb+') as f:
            text=f.read()
            car_dict[auction]=pickle.loads(text)
        car_list=[]
        models=[]
        inline_kb2 = InlineKeyboardMarkup()
        for i in car_dict[auction]:
            if i["brand"]==brand:
                car_list.append(i)
                model=i["model"]
                models.append(model)
        models=list(set(models))
        models.sort()
        for model in models:
            inline_btn_1 = InlineKeyboardButton(model, callback_data='model-'+str(model))
            inline_kb2.add(inline_btn_1)
        if car_list==[]:
            await callback_query.message.answer(choosing_model_car_text[0])
            return
        await callback_query.message.answer(choosing_model_car_text[1],reply_markup=inline_kb2)

    if 'car'==code[0]: #вывод информации об авто
        getting_info_car = {languages[0]: ["Getting information about the car⏳",
                                            "An unknown error has appeared during getting information. Please select other car or brand, we will fix it soon",
                                            "Order an inspection",
                                            "How to buy",
                                            'To start choosing cars type or click /start_choosing',
                                            "Data is being updated at the moment, repeat the action later"],
                            languages[1]: ["Получаем информацию об автомобиле⏳",
                                            "Произошла ошибка при получении информации об авто. Выберите другую марку, мы скоро исправим эту ошибку",
                                            "Заказать осмотр",
                                            "Как купить",
                                            "Для повторного поиска машин введите или нажмите /start_choosing",
                                            "На данный момент идет обновление данных, повторите действие позже"],
                            }
        getting_info_car_text = getting_info_car.get(user_lang)

        if not if_updated():
            await callback_query.message.answer(getting_info_car_text[-1])
            return
        
        await bot.send_message(callback_query.from_user.id, getting_info_car_text[0])
        driver=add_driver()
        id_car=code[1]
        url="https://cubedcommunity.xcira.com/inventory/"+str(id_car)
        driver.get(url)
        driver.set_window_size(1920, 1080)
        try:
            info=get_info_car(driver)
        except:
            await bot.send_message(callback_query.from_user.id, getting_info_car_text[1])
            return
        finally:
            driver.close()
            driver.quit()
        name_auto = info['CAR NAME']
        text=str(name_auto)+"\n"
        async with state.proxy() as data:
            car_list=data[callback_query.from_user.id]["car_list"]
        for car_1 in car_list:
            if id_car==car_1["id_car"]:
                break
        lot=str(car_1["lot"])
        lot=f"RUN NUMBER: {lot}\n"
        text+=lot
        for key in info:
            if key=="IMAGE":
                try:
                    media = types.MediaGroup()
                    count_photo=0
                    for url in info[key]:
                        media.attach_photo(url)
                        count_photo+=1
                        if count_photo==10 or count_photo != 0:
                            await callback_query.message.answer_media_group(media)
                            media = types.MediaGroup()
                            count_photo=0
                except Exception as e:
                    print(e)
                    pass
                #отправка фото
            elif key=="LIGHTS":
                if info[key]==[]:
                    continue
                if key != 'CAR NAME':
                    text+=key
                    text+=': '
                    for l in info[key]:
                        l+=" "
                        text+=l
                    text=text+"\n"
            else:
                if key != 'CAR NAME':
                    text_1=key+":"+info[key]+"\n"
                    text+=text_1
        inline_kb2 = InlineKeyboardMarkup()
        inline_btn_1 = InlineKeyboardButton(getting_info_car_text[2], callback_data='get_car-'+str(id_car))
        inline_btn_2 = InlineKeyboardButton(getting_info_car_text[3], callback_data='get_info-')
        inline_kb2.add(inline_btn_1).add(inline_btn_2)
        await callback_query.message.answer(text,reply_markup=inline_kb2)
        await callback_query.message.answer(getting_info_car_text[4])

    elif code[0]=="get_car":
        if not if_updated():
            await callback_query.message.answer(send_number_text[-1])
            return
        
        send_number = {languages[0]: ["Введите номер для обратной связи",
                                        "На данный момент идет обновление данных, повторите действие позже"],
                        languages[1]: ["Enter your phone number",
                                        "Data is being updated at the moment, repeat the action later"]}
        send_number_text = send_number.get(user_lang)
        link="https://cubedcommunity.xcira.com/inventory/"+str(code[1])

        async with state.proxy() as data:
            data[callback_query.from_user.id]['link']=link
        state = dp.current_state(user=callback_query.from_user.id)
        await state.set_state(TestStates.all()[3])
        await callback_query.message.answer(send_number_text[0])

    elif code[0]=="get_info":
        text_buy = {languages[0]: text_buy_eng, languages[1]: text_buy_rus}
        await bot.send_message(callback_query.from_user.id, text_buy.get(user_lang))

    elif code[0]=="model":
        earliest_model = {languages[0]: ["Enter the earliest release year",
                                            "Data is being updated at the moment, repeat the action later"],
                          languages[1]: ["Введите самый ранний год выпуска",
                                            "На данный момент идет обновление данных, повторите действие позже"]
                        }
        earliest_model_text = earliest_model.get(user_lang)
        if not if_updated():
            await callback_query.message.answer(user_lang[-1])
            return
        model=code[1]
        async with state.proxy() as data:
            data[callback_query.from_user.id]["model"]=model
        await bot.send_message(callback_query.from_user.id, earliest_model_text[0])
        state = dp.current_state(user=callback_query.from_user.id)
        await state.set_state(TestStates.all()[1])


if 1==1:
    executor.start_polling(dp)
