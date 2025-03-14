import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import random
import threading

TOKEN = "7814136530:AAEtr2sP3S1PENRy_uw0PGr7vLltSgF62a8"
DATA_FILE = "homework.json"

bot = telebot.TeleBot(TOKEN)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_homework():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_homework(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Добавить задание", callback_data="add_homework"))
    markup.add(InlineKeyboardButton("Показать задания", callback_data="show_homework"))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add_homework":
        msg = bot.send_message(call.message.chat.id, "Введите название предмета, название задания и описание через запятую")
        bot.register_next_step_handler(msg, add_homework)
    elif call.data == "show_homework":
        show_homework(call.message)
    elif call.data.startswith("show_task_"):
        task_id = int(call.data[10:])
        show_task_details(call.message, task_id)
    elif call.data.startswith("done_"):
        task_id = int(call.data[5:])
        complete_homework(call.message, task_id)
    elif call.data.startswith("delete_"):
        task_id = int(call.data[7:])
        confirm_delete(call.message, task_id)

def add_homework(message):
    try:
        subject, title, description = message.text.split(',', 2)
        data = load_homework()
        user_id = str(message.chat.id)

        if user_id not in data:
            data[user_id] = []
        
        task_id = len(data[user_id]) + 1
        data[user_id].append({
            "id": task_id,
            "subject": subject.strip(),
            "title": title.strip(),
            "description": description.strip()
        })
        save_homework(data)
        bot.send_message(message.chat.id, "Задание добавлено!")
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Введите название предмета, название задания и описание через запятую.")

def show_homework(message):
    data = load_homework()
    user_id = str(message.chat.id)

    if user_id not in data or not data[user_id]:
        bot.send_message(message.chat.id, "Список заданий пуст.")
    else:
        task_list = "Список заданий:\n"
        for task in data[user_id]:
            task_list += f"{task['id']}. {task['subject']} - {task['title']}\n"
        bot.send_message(message.chat.id, task_list + "\nНапишите номер задания, чтобы посмотреть детали.")

@bot.message_handler(func=lambda message: message.text.isdigit())
def show_task_details(message):
    task_id = int(message.text)
    data = load_homework()
    user_id = str(message.chat.id)
    
    task = next((t for t in data.get(user_id, []) if t['id'] == task_id), None)
    
    if task:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Выполнено ✅", callback_data=f"done_{task_id}"))
        markup.add(InlineKeyboardButton("Удалить ❌", callback_data=f"delete_{task_id}"))
        bot.send_message(message.chat.id, f"{task['subject']} - {task['title']}\n{task['description']}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Задание не найдено.")

def complete_homework(message, task_id):
    data = load_homework()
    user_id = str(message.chat.id)

    data[user_id] = [t for t in data[user_id] if t['id'] != task_id]
    save_homework(data)
    bot.send_message(message.chat.id, "Задание выполнено!")
    show_homework(message)

def confirm_delete(message, task_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить", callback_data=f"delete_{task_id}"))
    markup.add(InlineKeyboardButton("❌ Отменить", callback_data="cancel_delete"))
    bot.send_message(message.chat.id, "Вы уверены, что хотите удалить задание?", reply_markup=markup)

def delete_homework(message, task_id):
    data = load_homework()
    user_id = str(message.chat.id)

    data[user_id] = [t for t in data[user_id] if t['id'] != task_id]
    save_homework(data)
    bot.send_message(message.chat.id, "Задание удалено!")
    show_homework(message)

bot.polling()
