from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, NotFound
from django.contrib.auth import authenticate
from django.db import transaction

from .models import *
from core.players.serializers import PlayerShortSerializer


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'answer', 'price']
        # read_only_fields = ['id']

    @classmethod
    def _create(cls, validated_data, theme):
        question = Question.objects.create(theme=theme, **validated_data)
        return question

    @classmethod
    def _update(cls, instance, question_data):
        for attr, value in question_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ThemeShortSerializer(ModelSerializer):
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        fields = ['id', 'title', 'questions_count']

    def get_questions_count(self, instance):
        return len(instance.questions.all())


class ThemeSerializer(ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Theme
        fields = ['id', 'title', 'questions']
        # read_only_fields = ['id']

    @classmethod
    def _create(cls, validated_data, round):
        questions = validated_data.pop('questions')
        theme = Theme.objects.create(round=round, **validated_data)
        for question_data in questions:
            QuestionSerializer._create(validated_data=question_data, theme=theme)
        return theme

    @classmethod
    def _update(cls, instance, theme_data):
        questions = theme_data.pop('questions')
        for attr, value in theme_data.items():
            setattr(instance, attr, value)
        instance.save()
        for question_data in questions:
            question = None if 'id' not in question_data else Question.objects.filter(id=question_data['id'])
            if question:
                question = question[0]
                QuestionSerializer._update(instance=question, question_data=question_data)
            else:
                QuestionSerializer._create(validated_data=theme_data, theme=instance)
        return instance


class RoundShortSerializer(ModelSerializer):
    themes = ThemeShortSerializer(many=True)

    class Meta:
        model = Round
        fields = ['id', 'title', 'themes']


class RoundSerializer(ModelSerializer):
    themes = ThemeSerializer(many=True)

    class Meta:
        model = Round
        fields = ['id', 'title', 'themes']

        # read_only_fields = ['id']

    @classmethod
    def _create(cls, validated_data, pack):
        themes = validated_data.pop('themes')
        round = Round.objects.create(pack=pack, **validated_data)
        for theme_data in themes:
            ThemeSerializer._create(validated_data=theme_data, round=round)
        return round

    # @classmethod
    # def _update(cls, instance, round_data):
    #     for round in instance.rounds.all():
    #         round.delete()
    #
    #     rounds = validated_data.pop('rounds')
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #
    #     for round_data in rounds:
    #         RoundSerializer._create(validated_data=round_data, pack=instance)
    #     return instance


class PackSuperShortSerializer(ModelSerializer):
    rounds_count = serializers.SerializerMethodField()

    class Meta:
        model = Pack
        fields = ['id', 'title', 'author', 'rounds_count']

    def get_rounds_count(self, instance):
        return len(instance.rounds.all())


class PackShortSerializer(ModelSerializer):
    rounds = RoundShortSerializer(many=True)

    # author = PlayerShortSerializer

    class Meta:
        model = Pack
        fields = ['id', 'title', 'author', 'rounds']


class PackSerializer(PackShortSerializer):
    rounds = RoundSerializer(many=True)
    # MODELCLASS_NESTEDFIELD_MAP = {
    #     Pack: {'field_name': 'rounds', 'field_class': Round},
    #     Round: {'field_name': 'themes', 'field_class': Theme},
    #     Theme: {'field_name': 'questions', 'field_class': Question},
    #     Question: {'field_name': None, 'field_class': None}
    # }

    @transaction.atomic
    def create(self, validated_data):
        # return self._create_model(validated_data=validated_data, ModelClass=Pack)
        rounds = validated_data.pop('rounds')
        pack = Pack.objects.create(**validated_data)
        for round_data in rounds:
            RoundSerializer._create(validated_data=round_data, pack=pack)
        return pack

    @transaction.atomic
    def update(self, instance, validated_data):
        for round in instance.rounds.all():
            round.delete()

        rounds = validated_data.pop('rounds')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for round_data in rounds:
            RoundSerializer._create(validated_data=round_data, pack=instance)  # TODO check and probably add _update
        return instance

    # @transaction.atomic
    # def update(self, instance, validated_data):
    #     rounds = validated_data.pop('rounds')
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     for round_data in rounds:
    #         print(round_data)
    #         round = None if 'id' not in round_data else Round.objects.filter(id=round_data['id'])
    #         print(round)
    #         if round:
    #             round = round[0]
    #             print(round.title)
    #             RoundSerializer._update(instance=round, round_data=round_data)
    #             print(round)
    #         else:
    #             RoundSerializer._create(validated_data=round_data, pack=instance)
    #     return instance

    # def _create_model(self, validated_data, ModelClass):
    #     nested_field_name = self.MODELCLASS_NESTEDFIELD_MAP[ModelClass]['field_name']
    #     if nested_field_name is None:
    #         instance = ModelClass.objects.create(**validated_data)
    #         return instance
    #
    #     nested_models = validated_data.pop(nested_field_name)
    #     instance = ModelClass.objects.create(**validated_data)
    #     for nested_model_data in nested_models:
    #         self._create_model(nested_model_data, self.MODELCLASS_NESTEDFIELD_MAP[ModelClass]['field_class'])
    #
    #     return instance

    def _create_round(self, pack, round_data):
        themes = round_data.pop('themes')
        round = Round.objects.create(pack=pack, **round_data)
        for theme_data in themes:
            self._create_theme(round=round, theme_data=theme_data)
        return round

    def _create_theme(self, round, theme_data):
        questions = theme_data.pop('questions')
        theme = Theme.objects.create(round=round, **theme_data)
        for question_data in questions:
            self._create_question(theme=theme, question_data=question_data)
        return theme

    def _create_question(self, theme, question_data):
        question = Question.objects.create(theme=theme, **question_data)
        return question

    def _update_round(self, instance, round_data):
        themes = round_data.pop('themes')
        for attr, value in round_data.items():
            setattr(instance, attr, value)
        instance.save()
        for theme_data in themes:
            theme = None if 'id' not in theme_data else Theme.objects.filter(id=theme_data['id'])
            if theme:
                theme = theme[0]
                self._update_theme(instance=theme, theme_data=theme_data)
            else:
                self._create_theme(round=instance, theme_data=theme_data)
        return instance

    def _update_model(self, instance, data, ModelClass):
        field_name = self.MODELCLASS_NESTEDFIELD_MAP[ModelClass]
        nested_models = data.pop(field_name)
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        for nested_model_data in nested_models:
            model_instance = None if 'id' not in data else ModelClass.objects.filter(id=data['id'])
            if model_instance:
                model_instance = model_instance[0]
                self._update_model(instance=model_instance, data=nested_model_data, ModelClass=type(model_instance))
