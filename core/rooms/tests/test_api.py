from collections import OrderedDict
import json
from django.urls import reverse
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from core.packs.models import Pack, Round, Theme, Question
from core.packs.tests.test_api import create_pack
from core.players.models import PlayerInGame
from core.players.tests.test_api import create_player, get_authorized_client
from core.rooms.models import Room


class MyRoomApiTestCase(APITestCase):
    def setUp(self):
        self.p = create_player()
        self.p2 = create_player(first=False)
        self.c = get_authorized_client()
        self.c2 = get_authorized_client(False)
        self.pack = create_pack(self.p)
        self.response = self.c.post(path='/api/rooms/',
                                    data={"name": "Room1", "password": "1234", "pack": self.pack.id,
                                          'document_id': "1111"})


class RoomApiTestCase(APITestCase):
    def setUp(self):
        self.p = create_player()
        self.c = get_authorized_client()
        self.pack = create_pack(self.p)

    def test_create(self):
        response = self.c.post(path='/api/rooms/',
                               data={"name": "Room1", "password": "1234", "pack": self.pack.id, "document_id": "1111"})
        assert response.status_code == 201
        assert response.data == {'id': 1, 'name': 'Room1', 'pack': 1, 'players_in_room': [
            OrderedDict([('room', 1), ('is_room_admin', True), ('is_presenter', True), ('score', 0)])],
                                 'document_id': "1111"}
        assert self.p.player_in_room
        assert self.p.player_in_room.is_room_admin

    def test_create_with_existing_room(self):
        response = self.c.post(path='/api/rooms/',
                               data={"name": "Room1", "password": "1234", "pack": self.pack.id, "document_id": "1111"})
        assert response.status_code == 201

        response = self.c.post(path='/api/rooms/',
                               data={"name": "Room2", "password": "1234", "pack": self.pack.id, "document_id": "1111"})
        assert response.status_code == 403
        assert response.data == {'detail': 'Already in game'}

    def test_create_with_not_unique_name(self):
        response = self.c.post(path='/api/rooms/',
                               data={"name": "Room1", "password": "1234", "pack": self.pack.id, "document_id": "1111"})
        assert response.status_code == 201

        p2 = create_player(first=False)
        c2 = get_authorized_client(False)
        response = c2.post(path='/api/rooms/',
                           data={"name": "Room1", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})

        assert response.status_code == 400
        assert response.data == {'name': [ErrorDetail(string='room with this name already exists.', code='unique')]}

    def test_create_room_with_not_existing_pack(self):
        response = self.c.post(path='/api/rooms/',
                               data={"name": "Room1", "password": "1234", "pack": self.pack.id + 5,
                                     "document_id": "1111"})
        assert response.status_code == 400
        print(response.data)
        assert response.data == {
            'pack': [ErrorDetail(string='Invalid pk "6" - object does not exist.', code='does_not_exist')]}

    def test_get(self):
        room = Room.objects.create(name="Room1", password="1234", pack=self.pack, document_id="1111")
        p_in_r = PlayerInGame.objects.create(player=self.p, room=room, is_room_admin=True, is_presenter=True)
        response = self.c.get(path='/api/rooms/' + str(room.id) + '/')
        assert response.status_code == 200
        assert response.data == {'id': 1, 'name': 'Room1', 'pack': 1, 'players_in_room': [
            OrderedDict([('room', 1), ('is_room_admin', True), ('is_presenter', True), ('score', 0)])],
                                 'document_id': "1111"}

    def test_delete(self):
        response = self.c.post(path='/api/rooms/',
                               data={"name": "Room1", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})
        assert response.status_code == 201
        assert PlayerInGame.objects.count() == 1

        response = self.c.delete(path='/api/rooms/' + str(1) + '/')
        assert response.status_code == 204
        assert Room.objects.count() == 0

        assert PlayerInGame.objects.count() == 0

    def test_list(self):
        pl2 = create_player(first=False)
        c2 = get_authorized_client(False)
        response = self.c.post(path='/api/rooms/',
                               data={"name": "Room1", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})
        assert response.status_code == 201

        response = c2.post(path='/api/rooms/',
                           data={"name": "Room2", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})
        assert response.status_code == 201

        assert Room.objects.count() == 2

        response = self.c.get(path=reverse('rooms-list'))
        assert response.status_code == 200

        assert response.data == [OrderedDict([('id', 1), ('name', 'Room1')]),
                                 OrderedDict([('id', 2), ('name', 'Room2')])]


class LoginToRoomTestCase(MyRoomApiTestCase):

    def test_login(self):
        assert PlayerInGame.objects.count() == 1

        response = self.c2.post(path='/api/rooms/1/login/', data={"name": "Room1", "password": "1234"})
        assert response.status_code == 200
        assert response.data == {'status': 'ok'}
        assert PlayerInGame.objects.count() == 2

    def test_login_already_in_game(self):
        response = self.c2.post(path='/api/rooms/1/login/', data={"name": "Room1", "password": "1234"})
        assert response.status_code == 200

        response = self.c2.post(path='/api/rooms/1/login/', data={"name": "Room1", "password": "1234"})
        assert response.status_code == 403
        assert response.data == {'detail': 'Already in game'}

    def test_login_incorrect_password(self):
        response = self.c2.post(path='/api/rooms/1/login/', data={"name": "Room1", "password": "124"})
        assert response.status_code == 403
        assert response.data == {'detail': 'Incorrect password'}


class LogoutFromRoomTestCase(MyRoomApiTestCase):

    def test_logout_with_deleting_room(self):
        assert PlayerInGame.objects.count() == 1

        response = self.c.get(path='/api/rooms/1/logout/')
        assert response.status_code == 200

        assert PlayerInGame.objects.count() == 0
        assert Room.objects.count() == 0

    def test_logout_without_deleting_room(self):
        assert PlayerInGame.objects.count() == 1

        response = self.c2.post(path='/api/rooms/1/login/', data={"name": "Room1", "password": "1234"})
        assert response.status_code == 200
        assert PlayerInGame.objects.count() == 2

        response = self.c2.get(path='/api/rooms/1/logout/')
        assert response.status_code == 200

        assert PlayerInGame.objects.count() == 1
        assert Room.objects.count() == 1

    def test_logout_not_in_room(self):
        response = self.c2.get(path='/api/rooms/1/logout/')

        assert response.status_code == 403
        assert response.data == {'detail': 'Do not have any room'}

    def test_logout_not_in_this_room(self):
        response = self.c2.post(path='/api/rooms/',
                                data={"name": "Room2", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})
        assert response.status_code == 201

        response = self.c2.get(path='/api/rooms/1/logout/')
        assert response.status_code == 403
        assert response.data == {'detail': 'Not in this room'}
