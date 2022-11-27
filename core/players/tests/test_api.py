from collections import OrderedDict
from django.db.models import signals

from django.core.mail.backends.smtp import EmailBackend
from django.urls import reverse
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase, APIClient
from django.test.utils import override_settings

from core.players.models import Player

TEST_EMAIL = 'root@mail.ru'
TEST_EMAIL2 = 'no-reply.svoyak@yandex.com'
TEST_USERNAME = 'karsen146'
TEST_USERNAME2 = 'kartem146'
TEST_PASSWORD = 'password'
TEST_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MX0.1Db5Qu62JNDde1SHmJwajkoWQfMMNr4NjwnvTQBHW1g'
TEST_TOKEN2 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6Mn0.TeE1_zItAJjk0Y2CuuvdDJc9WdETBT7zDZl0FWqYH00'
TEST_INCORRECT_EMAIL = 'karsen146@gmail.ru'
TEST_NEW_PASSWORD = 'rootroot'


def create_player(email=TEST_EMAIL, username=TEST_USERNAME, password=TEST_PASSWORD, is_verified=True, first=True):
    if first:
        p = Player.objects.create(email=email, username=username, password=password, is_verified=is_verified)
    else:
        p = Player.objects.create(email=TEST_EMAIL2, username=TEST_USERNAME2, password=password,
                                  is_verified=is_verified)
    p.set_password(password)
    p.save()
    return p


def get_authorized_client(first=True):
    c = APIClient()
    if first:
        c.credentials(HTTP_AUTHORIZATION=TEST_TOKEN)
    else:
        c.credentials(HTTP_AUTHORIZATION=TEST_TOKEN2)
    return c


class MyTestCase(APITestCase):

    def setUp(self):
        self.c = APIClient()
        signals.post_save.disconnect(sender=Player, dispatch_uid="my_id")


class TracingBackend(EmailBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_messages(self, messages):
        self.__class__.called = True


class SignUpApiTestCase(MyTestCase):

    def setUp(self):
        super().setUp()
        self.url = '/api/signup/'
        create_player(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, True)

    def test_signup_200(self):
        response = self.c.post(self.url,
                               {'email': TEST_EMAIL2, 'username': TEST_USERNAME2, 'password': TEST_PASSWORD},
                               format='json')
        assert response.status_code == 201
        assert response.data == {'status': 'created'}

    def test_singup_not_unique_username_400(self):
        response = self.c.post(self.url,
                               {'email': TEST_EMAIL2, 'username': TEST_USERNAME, 'password': TEST_PASSWORD},
                               format='json')
        assert response.status_code == 400
        assert response.data == {
            'username': [ErrorDetail(string='user with this username already exists.', code='unique')]}

    def test_singup_not_unique_email_400(self):
        response = self.c.post(self.url,
                               {'email': TEST_EMAIL, 'username': TEST_USERNAME2, 'password': TEST_PASSWORD},
                               format='json')
        assert response.status_code == 400
        assert response.data == {
            'email': [ErrorDetail(string='user with this email already exists.', code='unique')]}


class LoginApiTestCase(MyTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('login')
        create_player(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, True)
        create_player(TEST_EMAIL2, TEST_USERNAME2, TEST_PASSWORD, False)

    def test_login_200(self):
        response = self.c.post(path=self.url, data={'email': TEST_EMAIL, 'password': TEST_PASSWORD}, format='json')
        assert response.status_code == 200
        assert response.data == {'username': TEST_USERNAME, 'email': TEST_EMAIL, 'current_room_id': None,
                                 'access_token': TEST_TOKEN}

    def test_login_incorrect_password_401(self):
        response = self.c.post(path=self.url, data={'email': TEST_EMAIL, 'password': "1"}, format='json')
        assert response.status_code == 401
        assert response.data == {
            'detail': ErrorDetail(string='Unable to log in with provided credentials.', code='authorization')}

    def test_login_via_token_200(self):
        self.c.credentials(HTTP_AUTHORIZATION=TEST_TOKEN)
        response = self.c.post(path=self.url, format='json')
        assert response.status_code == 200
        assert response.data == {'email': TEST_EMAIL, 'username': TEST_USERNAME, 'current_room_id': None}

    def test_login_to_unverified_user_403(self):
        response = self.c.post(path=self.url, data={'email': TEST_EMAIL2, 'password': TEST_PASSWORD}, format='json')
        assert response.status_code == 403
        assert response.data == {'detail': ErrorDetail(string='User is not verified', code='permission_denied')}


class ResetPasswordApiTestCase(MyTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('reset_password')
        create_player(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, True)

    def test_reset_password_200(self):
        response = self.c.post(self.url, {'email': TEST_EMAIL})
        assert response.status_code == 200
        assert response.data == {'status': 'New password was sent in email'}

    def test_reset_password_incorrect_email_401(self):
        response = self.c.post(self.url, {'email': TEST_INCORRECT_EMAIL})
        assert response.status_code == 401
        assert response.data == {
            'detail': ErrorDetail(string='No user with this email address', code='not_authenticated')}


class ChangePasswordTestCase(MyTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('change_password')
        create_player(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, True)

    def test_change_password_200(self):
        self.c.credentials(HTTP_AUTHORIZATION=TEST_TOKEN)
        response = self.c.post(path=self.url, data={'old_password': TEST_PASSWORD, 'new_password': TEST_NEW_PASSWORD,
                                                    'repeat_password': TEST_NEW_PASSWORD}, format='json')
        assert response.status_code == 200
        assert response.data == {'status': 'Password successfully changed'}

        response = self.c.post(path=reverse('login'), data={'email': TEST_EMAIL, 'password': TEST_PASSWORD},
                               format='json')

        assert response.status_code == 401
        assert response.data == {
            'detail': ErrorDetail(string='Unable to log in with provided credentials.', code='authorization')}

    def test_change_password_400(self):
        self.c.credentials(HTTP_AUTHORIZATION=TEST_TOKEN)
        response = self.c.post(path=self.url, data={'old_password': TEST_PASSWORD, 'new_password': TEST_NEW_PASSWORD,
                                                    'repeat_password': TEST_NEW_PASSWORD + '1'}, format='json')
        assert response.status_code == 400
        assert response.data == {'detail': ErrorDetail(string='Passwords do not match', code='parse_error')}

    def test_change_password_403(self):
        self.c.credentials(HTTP_AUTHORIZATION=TEST_TOKEN)
        response = self.c.post(path=self.url,
                               data={'old_password': TEST_NEW_PASSWORD, 'new_password': TEST_NEW_PASSWORD,
                                     'repeat_password': TEST_NEW_PASSWORD}, format='json')
        assert response.status_code == 403
        assert response.data == {'detail': ErrorDetail(string='Old password is incorrect', code='permission_denied')}


class ResendVerificationLetterTestCase(MyTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('resend_verification')
        create_player(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, False)

    def test_send_verification_200(self):
        response = self.c.post(path=self.url, data={'email': TEST_EMAIL}, format='json')
        assert response.status_code == 200
        assert response.data == {'status': 'Verification message was sent to your email'}

    def test_send_verification_401(self):
        response = self.c.post(path=self.url, data={'email': TEST_EMAIL2}, format='json')
        assert response.status_code == 401
        assert response.data == {
            'detail': ErrorDetail(string='No user with this email address', code='not_authenticated')}

    def test_send_verification_403(self):
        p = Player.objects.create(email=TEST_EMAIL2, username=TEST_USERNAME2, password=TEST_PASSWORD, is_verified=True)
        p.set_password(TEST_PASSWORD)
        p.save()
        response = self.c.post(path=self.url, data={'email': TEST_EMAIL2}, format='json')
        assert response.status_code == 403
        assert response.data == {'detail': ErrorDetail(string='User is already verified', code='permission_denied')}


class VerifyTestCase(MyTestCase):
    def setUp(self):
        super().setUp()
        self.p = create_player(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, False)
        self.p2 = create_player(TEST_EMAIL2, TEST_USERNAME2, TEST_PASSWORD, True)

    def test_verify_200(self):
        self.url = reverse('verify', args=[str(self.p.verification_uuid)])
        response = self.c.get(path=self.url)
        assert response.status_code == 200
        assert response.data == {'status': 'verified'}

    def test_verify_not_exists_401(self):
        s = str("efd9ac08-cdd8-4894-913c-b8061966eb4d")
        self.url = reverse('verify', args=[s])
        response = self.c.get(path=self.url)
        assert response.status_code == 401
        assert response.data == {'status': 'User does not exist'}

    def test_already_verified_user_403(self):
        self.url = reverse('verify', args=[str(self.p2.verification_uuid)])
        response = self.c.get(path=self.url)
        assert response.status_code == 403
        assert response.data == {'status': 'User is already verified'}


class PlayerTestCase(MyTestCase):

    def setUp(self):
        self.c = APIClient()
        self.c.credentials(HTTP_AUTHORIZATION=TEST_TOKEN)
        self.p = create_player(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, True)
        self.p2 = create_player(TEST_EMAIL2, TEST_USERNAME2, TEST_PASSWORD, True)
        self.p3 = create_player(TEST_EMAIL2 + 'c', TEST_USERNAME + 'c', TEST_PASSWORD, True)

    def test_list(self):
        response = self.c.get(path=reverse('players-list'))
        assert response.status_code == 200
        assert response.data == [OrderedDict([('username', 'karsen146')]), OrderedDict([('username', 'kartem146')]),
                                 OrderedDict([('username', 'karsen146c')])]

    def test_get(self):
        response = self.c.get('/api/players/' + str(self.p.id) + '/')
        assert response.status_code == 200
        assert response.data == {'email': TEST_EMAIL, 'username': TEST_USERNAME, 'player_in_room': None}

    def test_get_player_403(self):
        self.c2 = APIClient()
        response = self.c2.get('/api/players/' + str(self.p2.id) + '/')
        assert response.status_code == 403
        assert response.data == {'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                       code='permission_denied')}
