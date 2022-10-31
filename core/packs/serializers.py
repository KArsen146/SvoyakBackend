from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.db import transaction

from .models import *
from ..rooms.models import Room


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
    questions_count = serializers.ReadOnlyField()

    class Meta:
        model = Theme
        fields = ['id', 'title', 'questions_count']


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
    rounds_count = serializers.ReadOnlyField()
    author = serializers.StringRelatedField(many=False)

    class Meta:
        model = Pack
        fields = ['id', 'title', 'author', 'rounds_count']


class PackShortSerializer(PackSuperShortSerializer):
    rounds = RoundShortSerializer(many=True)

    class Meta:
        model = Pack
        fields = ['id', 'title', 'author', 'rounds_count', 'rounds']


class PackSerializer(PackShortSerializer):
    rounds = RoundSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        # return self._create_model(validated_data=validated_data, ModelClass=Pack)
        rounds = validated_data.pop('rounds')
        pack = Pack.objects.create(**validated_data)
        for round_data in rounds:
            RoundSerializer._create(validated_data=round_data, pack=pack)
        return pack

    def update(self, instance, validated_data):
        room = list(Room.objects.filter(pack=instance))
        if len(room):
            return self.create_new_version(instance, validated_data)
        with transaction.atomic():
            for round in instance.rounds.all():
                round.delete()
            rounds = validated_data.pop('rounds')
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            for round_data in rounds:
                RoundSerializer._create(validated_data=round_data, pack=instance)  # TODO check and probably add _update
        return instance

    @transaction.atomic
    def create_new_version(self, instance, validated_data):
        instance.is_deprecated = True
        instance.save(update_fields=['is_deprecated'])
        validated_data['version'] = instance.version + 1
        print(validated_data)
        pack = self.create(validated_data)
        return pack

    #TODO delete
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


class QuestionInGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionInGame
        fields = ['id', 'round_in_game', 'question', 'status']

    @classmethod
    def _create(self, round_in_game, question):
        question_in_game = QuestionInGame.objects.create(round_in_game=round_in_game, question=question)
        return question_in_game


class RoundInGameSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = QuestionInGame
        fields = ['id', 'next_round_in_game', 'round', 'not_played_questions_count', 'questions']

    @classmethod
    def _create(self, round: Round, next_round):
        round_in_game = RoundInGame.objects.create(next_round_in_game=next_round, round=round)
        not_played_questions_count = 0
        for theme in list(round.themes.all()):
            not_played_questions_count += theme.questions_count
            for question in list(theme.questions.all()):
                QuestionInGameSerializer._create(round_in_game=round_in_game, question=question)
        round_in_game.not_played_questions_count = not_played_questions_count
        round_in_game.save(update_fields=["not_played_questions_count"])
        return round_in_game
