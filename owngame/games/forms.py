from django import forms
from django.core.exceptions import ValidationError


class GetAnswer(forms.Form):
    answer_text = forms.CharField(max_length=200, help_text="Введите ответ на поставленный вопрос.", label='Ответ')

    def clean_answer_text(self):
        data = self.cleaned_data['answer_text']
        return data


class GameSize(forms.Form):
    themes_num = forms.IntegerField(max_value=9, min_value=1, label="Количество тем")
    questions_num = forms.IntegerField(max_value=9, min_value=1, label="Количество вопросов")

    def get_themes_num(self):
        return self.cleaned_data['themes_num']

    def get_questions_num(self):
        return self.cleaned_data['questions_num']
