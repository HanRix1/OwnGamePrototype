from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField


class Theme(models.Model):
    theme_name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.theme_name


class Question(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200, blank=False)
    answer_text = models.CharField(max_length=200, blank=False)
    pub_date = models.DateTimeField(auto_now_add=True)
    pub_update = models.DateTimeField(auto_now=True)
    question_value = models.IntegerField(default=0)
    is_answered = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text



def default_settings():
    return [0 for _ in range(9)]


class Lobby(models.Model):
    player_id = models.IntegerField(default=1, blank=False)
    score = models.IntegerField(default=0)
    theme_num = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(9)])
    question_num = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(9)])
    pos = ArrayField(models.IntegerField(), default=default_settings)
    rand_value = ArrayField(models.IntegerField(), default=default_settings)
    is_ended = models.BooleanField(default=False)

    def __str__(self):
        return self.player_id
