# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def send_email_task(subject, plain_message, from_email, to_email, html_message=None):
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
