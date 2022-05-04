from django.db import models


class Pack(models.Model):
    title = models.TextField(max_length=32, null=False, blank=False, unique=True, db_index=True)


class Round(models.Model):
    title = models.TextField(max_length=32, null=False, blank=False)
    pack = models.ForeignKey(Pack, related_name='rounds', on_delete=models.CASCADE, null=False)


class Theme(models.Model):
    title = models.TextField(max_length=32, null=False, blank=False)
    round = models.ForeignKey(Round, related_name='themes', on_delete=models.CASCADE, null=False)


class Question(models.Model):
    text = models.TextField(max_length=512, null=False, blank=False)
    answer = models.TextField(max_length=512, null=False, blank=False)
    price = models.IntegerField(null=False, default=100)
    theme = models.ForeignKey(Theme, related_name='questions', on_delete=models.CASCADE, null=False)
