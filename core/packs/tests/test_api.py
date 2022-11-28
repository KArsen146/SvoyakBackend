from collections import OrderedDict
import json
from django.urls import reverse
from rest_framework.test import APITestCase
from core.packs.models import Pack, Round, Theme, Question
from core.players.tests.test_api import create_player, get_authorized_client
from core.rooms.models import Room


def create_question(theme, text, price, answer="Ura"):
    q = Question.objects.create(theme=theme, text=text, answer=answer, price=price)
    return q


def create_theme(round, title):
    theme = Theme.objects.create(title=title, round=round)
    for i in range(3):
        create_question(theme, "New Question" + str(i), (1 + i) * 100)
    return round


def create_round(pack, title="New round"):
    round = Round.objects.create(title=title, pack=pack)
    for i in range(3):
        create_theme(round, "New Theme" + str(i))
    return round


def create_pack(author, title="New pack"):
    pack = Pack.objects.create(title=title, author=author)
    for i in range(3):
        create_round(pack, title + " New round" + str(i))
    return pack


class PackApiTestCase(APITestCase):

    def setUp(self):
        self.p = create_player()
        self.c = get_authorized_client()

    def test_create(self):
        val = json.load(open("core/packs/tests/test_data/pack1.json"))
        response = self.c.post('/api/packs/', data=val, format='json')
        assert response.status_code == 201
        assert response.json() == json.load(open("core/packs/tests/test_data/pack1_response.json"))

    def test_create_with_not_unique_title(self):
        val = json.load(open("core/packs/tests/test_data/pack1.json"))
        response = self.c.post('/api/packs/', data=val, format='json')
        assert response.status_code == 201

        val = json.load(open("core/packs/tests/test_data/pack1.json"))
        response = self.c.post('/api/packs/', data=val, format='json')
        assert response.status_code == 403
        assert response.data == {'detail': 'Pack with this title already exists'}

    def test_get(self):
        pack = create_pack(self.p)
        response = self.c.get('/api/packs/' + str(pack.id) + '/')
        assert response.status_code == 200
        assert response.json() == json.load(open("core/packs/tests/test_data/pack_response.json"))

    def test_update(self):
        pack = create_pack(self.p)
        val = json.load(open("core/packs/tests/test_data/pack1.json"))
        response = self.c.put('/api/packs/' + str(pack.id) + '/', data=val, format='json')
        assert response.status_code == 200
        assert response.json() == json.load(open("core/packs/tests/test_data/pack1_put.json"))

    def test_update_with_existing_room(self):
        pack = create_pack(self.p)
        room = Room.objects.create(name="ar", password="1234", pack=pack)
        val = json.load(open("core/packs/tests/test_data/pack1.json"))
        response = self.c.put('/api/packs/' + str(pack.id) + '/', data=val, format='json')
        assert response.status_code == 200
        assert Pack.objects.count() == 2

        pack = Pack.objects.get(pk=1)
        assert pack.is_deprecated is True

        room.delete()
        assert Pack.objects.count() == 1

    def test_delete(self):
        pack = create_pack(self.p)
        response = self.c.delete('/api/packs/' + str(pack.id) + '/')
        assert response.status_code == 204
        assert Pack.objects.count() == 0

    def test_delete_with_existing_room(self):
        pack = create_pack(self.p)
        room = Room.objects.create(name="ar", password="1234", pack=pack)
        response = self.c.delete('/api/packs/' + str(pack.id) + '/')
        assert response.status_code == 204
        assert Pack.objects.count() == 1

        pack = Pack.objects.get(pk=1)
        assert pack.is_deprecated is True

        room.delete()
        assert Pack.objects.count() == 0

    def test_list(self):
        create_pack(self.p)
        response = self.c.get(path=reverse('packs-list'))
        assert response.status_code == 200
        assert response.data == OrderedDict([('count', 1), ('next', None), ('previous', None), (
            'results',
            [OrderedDict([('id', 1), ('title', 'New pack'), ('author', 'karsen146'), ('rounds_count', 3)])])])

        for i in range(10):
            create_pack(self.p, "Pack " + str(i))
        response = self.c.get(path=reverse('packs-list'))
        assert response.status_code == 200
        assert response.data.get('count') == 11

    def test_filter_pack(self):
        create_pack(self.p)
        create_pack(self.p, "New pack2")
        create_pack(self.p, "Old pack3")

        response = self.c.get('/api/packs/?title=New')
        assert response.status_code == 200
        assert response.data.get('count') == 2

        p2 = create_player(first=False)
        create_pack(p2, "Old pack4")
        response = self.c.get('/api/packs/?author=' + self.p.username)
        assert response.status_code == 200
        assert response.data.get('count') == 3
