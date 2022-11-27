from collections import OrderedDict
import json
from django.urls import reverse
from rest_framework.test import APITestCase
from core.packs.models import Pack, Round, Theme, Question
from core.packs.tests.test_api import create_pack
from core.players.models import PlayerInGame
from core.players.tests.test_api import create_player, get_authorized_client
from core.rooms.models import Room


class RoomApiTestCase(APITestCase):
    def setUp(self):
        self.p = create_player()
        self.c = get_authorized_client()
        self.pack = create_pack(self.p)

    def test_create(self):
        response = self.c.post(path='/api/rooms/', data={"name": "Room1", "password": "1234", "pack": self.pack.id, "document_id": "1111"})
        assert response.status_code == 201
        assert response.data == {'id': 1, 'name': 'Room1', 'pack': 1, 'players_in_room': [
            OrderedDict([('room', 1), ('is_room_admin', True), ('is_presenter', True), ('score', 0)])], 'document_id': "1111"}
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

    def test_get(self):
        room = Room.objects.create(name="Room1", password="1234", pack=self.pack, document_id="1111")
        p_in_r = PlayerInGame.objects.create(player=self.p, room=room, is_room_admin=True, is_presenter=True)
        response = self.c.get(path='/api/rooms/' + str(room.id) + '/')
        assert response.status_code == 200
        assert response.data == {'id': 1, 'name': 'Room1', 'pack': 1, 'players_in_room': [
            OrderedDict([('room', 1), ('is_room_admin', True), ('is_presenter', True), ('score', 0)])], 'document_id': "1111"}

    def test_delete(self):
        response = self.c.post(path='/api/rooms/', data={"name": "Room1", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})
        assert response.status_code == 201
        assert PlayerInGame.objects.count() == 1

        response = self.c.delete(path='/api/rooms/' + str(1) + '/')
        assert response.status_code == 204
        assert Room.objects.count() == 0

        assert PlayerInGame.objects.count() == 0

    def test_list(self):
        pl2 = create_player(first=False)
        c2 = get_authorized_client(False)
        response = self.c.post(path='/api/rooms/', data={"name": "Room1", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})
        assert response.status_code == 201

        response = c2.post(path='/api/rooms/', data={"name": "Room2", "password": "1234", "pack": self.pack.id, 'document_id': "1111"})
        assert response.status_code == 201

        assert Room.objects.count() == 2

        response = self.c.get(path=reverse('rooms-list'))
        assert response.status_code == 200

        assert response.data == [OrderedDict([('id', 1), ('name', 'Room1')]),
                                 OrderedDict([('id', 2), ('name', 'Room2')])]
