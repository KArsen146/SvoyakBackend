from core.tasks import send_email_html_task


def send_email(subject, email, html_content):
    from_email = 'no-reply.svoyak@yandex.ru'
    html_content = "Здравствуйте!<br><br><br>" \
                   + html_content \
                   + "<br><br><br> С уважением, команда Svoyak"
    send_email_html_task.delay(subject, html_content, from_email, email)


def send_verification_email(email, uuid):
    html_content = f"Спасибо за регистрацию в Svoyak!" \
                   f"<br>Перейдите по <a href=https://svoyak-frontend.herokuapp.com/registration_verify/?id=" \
                   f"{uuid}>ссылке</a>  для верификации Вашего аккаунта"
    subject = 'Svoyak: verify'
    send_email(subject, email, html_content)


def send_new_password_email(email, password):
    html_content = f"<br>С вашего аккаунта был произведен запрос на сброс пароля" \
                   f"<br>Вам был сгененрирован временный пароль:" \
                   f"<br><strong> {password} </strong>" \
                   f"<br>Мы рекомендуем Вам сменить его при ближайшем входе в Ваш аккаунт"
    subject = 'Svoyak: new password'
    send_email(subject, email, html_content)
