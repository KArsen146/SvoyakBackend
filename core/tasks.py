from __future__ import absolute_import, unicode_literals

import time
from celery import shared_task

from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email_html_task(subject, html_content, from_email, email):
    msg = EmailMultiAlternatives(subject, html_content, from_email, [email])
    msg.content_subtype = "html"
    msg.send()
    return None
