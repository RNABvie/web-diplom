from __future__ import absolute_import, unicode_literals
from celery import shared_task
import telebot
import datetime
import schedule
import time
from django.conf import settings
from django.core.mail import EmailMessage
from fpdf import FPDF
from . import models


@shared_task
def tgbot_products():
    global message_ls
    token = settings.TELEGRAM_API_TOKEN
    bot = telebot.TeleBot(token)
    message_ls = 1

    @bot.message_handler(commands=['start'])
    def start_message(message):
        global message_ls, vacancies
        bot.send_message(message.chat.id, f"Товар{datetime.datetime.now().time()}")
        message_ls = ["Вот:\n"]
        vacancies = models.Products.objects.all()
        counter = 1
        for vacancy in vacancies:
            message_ls.append(f"{counter}. {vacancy.product} - {vacancy.amount}")
            counter += 1
        message_ls = "\n".join(message_ls)
        message_ls = f"{message_ls}\nЭто всё!"

        def send_message(chat_id, txt_message):
            global vacancies
            bot.send_message(chat_id, txt_message)
            counter = 1
            pdf = FPDF('P', 'mm', 'Letter')
            pdf.add_page()
            pdf.add_font('DejaVu', '', 'DejaVuSerifCondensed.ttf', uni=True)
            pdf.set_font('DejaVu', '', 14)
            pdf.cell(0, 10, "Товары:", ln=True, align="C")

            for vacancy in vacancies:
                pdf.cell(70, 10, f"{counter}. {vacancy.product}: {vacancy.amount}", new_x="LMARGIN", new_y="NEXT")
                counter += 1
            pdf.output('report.pdf')

            m_from = settings.EMAIL_HOST_USER
            m_to = ["rasnabi4@gmail.com"]
            m_subject = "Отчет О 'Товарах'"
            m_message = f"Просмотрите ниже прикрепленный PDF-файл:"
            email = EmailMessage(
                m_subject,
                m_message,
                m_from,
                m_to
            )

            m_file = "report.pdf"
            with open(m_file, 'rb') as file:

                email.attach('report.pdf', file.read(), 'application/pdf')

            email.send()

        schedule.every().day.at("18:48").do(send_message, chat_id=message.chat.id,
                                            txt_message=message_ls)

        while True:
            schedule.run_pending()
            time.sleep(1)

    bot.infinity_polling()

