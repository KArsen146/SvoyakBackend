from django.db import models
from django.utils.translation import gettext_lazy as _


class Pack(models.Model):
    title = models.TextField(max_length=32, null=False, blank=False, db_index=True)
    version = models.IntegerField(default=1)
    author = models.ForeignKey('players.Player', related_name='packs', on_delete=models.SET_NULL, null=True,
                               db_index=True)
    # TODO WTF?
    # Restrictions on PostgreSQL
    #
    # PostgreSQL requires functions and operators referenced in an index to be marked as IMMUTABLE.
    # Django doesn’t validate this but PostgreSQL will error.
    # This means that functions such as Concat() aren’t accepted.

    is_deprecated = models.BooleanField(default=False, null=False)

    class Meta:
        unique_together = ('title', 'version')

    @property
    def rounds_count(self):
        return self.rounds.count()


class Round(models.Model):
    title = models.TextField(max_length=32, null=False, blank=False)
    pack = models.ForeignKey(Pack, related_name='rounds', on_delete=models.CASCADE, null=False, db_index=True)

    @property
    def themes_count(self):
        return self.themes.count()


class Theme(models.Model):
    title = models.TextField(max_length=32, null=False, blank=False)
    round = models.ForeignKey(Round, related_name='themes', on_delete=models.CASCADE, null=False, db_index=True)

    @property
    def questions_count(self):
        return self.questions.count()


class Question(models.Model):
    text = models.TextField(max_length=512, null=False, blank=False)
    answer = models.TextField(max_length=512, null=False, blank=False)
    price = models.IntegerField(null=False, default=100)
    theme = models.ForeignKey(Theme, related_name='questions', on_delete=models.CASCADE, null=False, db_index=True)


class RoundInGame(models.Model):
    next_round_in_game = models.ForeignKey('self', default=None, on_delete=models.SET_NULL, null=True, db_index=True)
    round = models.ForeignKey(Round, related_name='rounds_in_game', on_delete=models.CASCADE, null=False, db_index=True)
    not_played_questions_count = models.IntegerField(default=0)


class QuestionInGame(models.Model):
    class QuestionStatus(models.TextChoices):
        NOT_PLAYED = 'NP', _('Not played')
        IS_PLAYING = 'IP', _('Is playing')
        WRONG_ANSWER = 'WA', _('Wrong answer')
        CORRECT_ANSWER = 'CA', _('Correct answer')

    round_in_game = models.ForeignKey(RoundInGame, related_name='questions_in_game', on_delete=models.CASCADE,
                                      null=False)
    question = models.ForeignKey(Question, related_name='questions_in_game', on_delete=models.CASCADE, null=False)
    status = models.CharField(max_length=2, choices=QuestionStatus.choices, default=QuestionStatus.NOT_PLAYED)
