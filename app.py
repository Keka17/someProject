import telebot
import asyncio
from telebot.async_telebot import AsyncTeleBot
from config import TOKEN
from questions import questions
import animals_info

animals = animals_info.animals
animal_info = animals_info.animal_info
animal_images = animals_info.animal_images

bot = AsyncTeleBot(TOKEN, parse_mode='HTML')


current_question_index = 0


@bot.message_handler(commands=['quiz'])
async def quiz(message: telebot.types.Message):
    global current_question_index
    global animals

    current_question_index = 0
    animals = {animal: 0 for animal in animals.keys()}
    await send_question(message.chat.id)


async def send_question(chat_id):
    global current_question_index

    if current_question_index < len(questions):
        question = questions[current_question_index]
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in question['options']:
            markup.add(telebot.types.KeyboardButton(option))
        await bot.send_message(chat_id, question['question'], reply_markup=markup)
    else:
        await show_result(chat_id)


@bot.message_handler(func=lambda message: message.text in questions[current_question_index]['options'])
async def handle_answer(message: telebot.types.Message):
    global current_question_index, animals

    selected_option = message.text
    question = questions[current_question_index]

    for animal in question['animal_mapping'][selected_option]:
        animals[animal] += 1

    current_question_index += 1
    await send_question(message.chat.id)


@bot.message_handler(func=lambda message: current_question_index >= len(questions))
async def show_result(chat_id):  #
    global current_question_index, animals

    result = max(animals, key=animals.get)
    await bot.send_message(chat_id, f"Твое тотемное животное - <b>{result}</b>! 🎉")
    animal_info(chat_id, result)

    text = ('Пройти викторину заново ➡️ /restart\n'
            'Узнать информацию о "Клубе друзей" ➡️ /info\n'
            'Поделиться результатом ➡️ /share\n'
            'Обратная связь ➡️ /feedback')
    await bot.send_message(chat_id, text)
    current_question_index = 0


@bot.message_handler(commands=['restart'])
async def restart_quiz(message: telebot.types.Message):
    global current_question_index, animals

    current_question_index = 0
    animals = {animal: 0 for animal in animals}  # Обнуляем счетчики
    await send_question(message.chat.id)


@bot.message_handler(commands=['start', 'help'])
async def help(message: telebot.types.Message):
    text = """ Тотемный компас: твой путь к <b>“Клубу друзей”</b>!
Как это работает?\n
<b>Отвечай на вопросы:</b>
1) Выбери ответ, который лучше всего тебе подходит.
2) Не бойся быть честным с собой, ведь твой внутренний зверь ждет, чтобы раскрыться!
<b>Узнай свое тотемное животное:</b>
По результатам викторины ты получишь животное, которое символизирует твои лучшие качества и таланты.
Узнай больше о программе <b>“Клуб друзей” Московского зоопарка</b>, которая позволит тебе:
1) Стать ближе к животным зоопарка.
2) Поддержать зоопарк в заботе о его обитателях.\n
Расскажи своим друзьям о своем тотемном животном и пригласи их пройти викторину!
Делись своими впечатлениями о “Клубе друзей” и зоопарке в социальных сетях!

Начать викторину ➡️ /quiz
    """
    await bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['info'])
async def info(message: telebot.types.Message):
    text = """
Основная задача Московского зоопарка с самого начала его существования — сохранение биоразнообразия планеты. 
Когда вы берете под опеку животное, вы помогаете нам в этом благородном деле. 
При нынешних темпах развития цивилизации к 2050 году с лица Земли могут исчезнуть около 10 000 биологических видов. 
Московский зоопарк вместе с другими зоопарками мира делает все возможное, чтобы сохранить их.
В настоящее время опекуны объединились в неформальное сообщество — Клуб друзей Московского зоопарка. 
Программа «Клуб друзей» дает возможность опекунам ощутить свою причастность к делу сохранения природы, 
участвовать в жизни Московского зоопарка и его обитателей, видеть конкретные результаты своей деятельности.\n
Для связи с зоопарком вы можете написать на [zoofriends@moscowzoo.ru](mailto:zoofriends@moscowzoo.ru) 
или позвонить по номеру [+7 (962) 971-38-75](tel:+79629713875)\n
Узнать больше: https://moscowzoo.ru/about/guardianship
    """
    await bot.reply_to(message, text, parse_mode='Markdown')


@bot.message_handler(commands=['share'])
async def share_result(message: telebot.types.Message):
    global animals
    result = max(animals, key=animals.get)
    image_url = animal_images.get(result)

    if image_url:
        await bot.send_photo(message.chat.id, image_url, caption='Поделись изображением в социальных сетях - '
                                                           'помоги большему количеству людей узнать о "Клубе друзей" 😉')


@bot.message_handler(commands=['feedback'])
async def get_feedback(message: telebot.types.Message):
    form_url = 'https://forms.gle/PWUfpSAYvnpTmPYYA'
    text = f'Чтобы оставить отзыв, перейдите по ссылке:\n{form_url}'
    await bot.reply_to(message, text)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(bot.polling())
