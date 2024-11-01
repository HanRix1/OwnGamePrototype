from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from random import randint
from django.contrib.auth import logout, authenticate, login

from games.models import Question, Theme, Lobby
from .forms import GetAnswer, GameSize

data_db = [
    {'id': 1, 'initials': 'Околов Виталиий Александрович', 'total_points': 2000},
    {'id': 2, 'initials': 'Басистый Илья Владимирович', 'total_points': 1800},
    {'id': 3, 'initials': 'Щуров Дмитрий Витальевич', 'total_points': 1900},
    {'id': 4, 'initials': 'Матюхин Никита Евгеньевич', 'total_points': 2200},
]


def index(request):
    menu = {'title': "Начать игру", 'url_name': 'size_init'}
    return render(request, 'games/index.html', context=menu)


def info(request):
    data = {'title': 'Информация о сайте',
            'subtitle': 'Здесь будет размещена вся информация о сайте'}
    return render(request, 'games/info.html', data)


@login_required
def results(request):
    data = {'title': 'Резульаты',
            'subtitle': 'Результаты викторин',
            'players': data_db, }
    return render(request, 'games/players_results.html', context=data)


@login_required
def show(request, player_id):
    return HttpResponse(f'Результаты игры с номером:{player_id}')


@login_required
def gamestart(request):
    data = {}
    qs_db = {}
    session_info = get_object_or_404(Lobby.objects.filter(player_id=request.user.id, is_ended=False))
    data['score'] = session_info.score
    questions_list = get_list_or_404(
        Question.objects
        .order_by("theme_id", "question_value", "id")
    )
    rand_values = session_info.rand_value
    pos = session_info.pos
    themes = get_list_or_404(Theme)
    k = 0
    m = 0
    flag = False
    for i in range(session_info.theme_num):
        buf = []
        for j in range(session_info.question_num):
            question = questions_list[k + rand_values[m]]
            if question.is_answered:
                buf.append(Question())
            else:
                flag = True
                buf.append(question)
            k += pos[m]
            m += 1
        qs_db[themes[i].theme_name] = buf

    if not flag:
        question = get_list_or_404(Question, is_answered=True)
        for qs in question:
            qs.is_answered = False
            qs.save()
        session_info.is_ended = True
        session_info.save()
        return HttpResponse(session_info.score)

    data['qs'] = qs_db
    return render(request, 'games/game.html', context=data)


def contact(request):
    return HttpResponse("Обратная связь")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


@login_required
def raise_question(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    session_info = get_object_or_404(Lobby.objects.filter(player_id=request.user.id, is_ended=False))
    if request.method == 'POST':
        form = GetAnswer(request.POST)
        if form.is_valid():
            if form.clean_answer_text().lower() == question.answer_text.lower():
                session_info.score += question.question_value
            else:
                session_info.score -= question.question_value
            question.is_answered = True
            question.save()
            session_info.save()
            return redirect('start_game')
    else:
        form = GetAnswer()

    data = {'qs': question.question_text,
            'form': form,
            }
    return render(request, 'games/raise_question.html', context=data)


@login_required
def size_init(request):
    data = {}
    session_info = Lobby.objects.filter(player_id=request.user.id, is_ended=False)
    if session_info:
        return redirect('start_game')

    if request.method == 'POST':
        form = GameSize(request.POST)
        if form.is_valid():
            themes = get_list_or_404(Theme)
            data['form'] = form
            if form.get_themes_num() != form.get_questions_num():
                data['title'] = f'Количество тем и вопрсов должно быть одинаковым'
                return render(request, 'games/games_settings.html', context=data)
            else:
                if form.get_themes_num() > len(themes):
                    data['title'] = f'В базе данных недостаточно тем, доступных тем: {len(themes)}'
                    return render(request, 'games/games_settings.html', context=data)
                else:
                    for i in range(form.get_themes_num()):
                        query = get_list_or_404(
                            Question.objects.values('question_value').filter(theme_id=themes[i]).annotate(
                                total=Count('id')))
                        if len(query) < form.get_questions_num():
                            data['title'] = f'В базе данных недостаточн вопросов для темы {themes[i].theme_name}'
                            return render(request, 'games/games_settings.html', context=data)

            rand_values = []
            positions = []
            for i in range(form.get_themes_num()):
                buf = get_list_or_404(
                    Question.objects
                    .values('question_value')
                    .filter(theme_id=themes[i])
                    .annotate(total=Count('id'))
                )
                for j in range(form.get_questions_num()):
                    rand_values.append(randint(0, buf[j]['total'] - 1))
                    positions.append(buf[j]['total'])

            session_info = Lobby(
                player_id=request.user.id,
                theme_num=form.get_themes_num(),
                question_num=form.get_questions_num(),
                pos=positions,
                rand_value=rand_values
            )
            session_info.save()
            return redirect('start_game')
    else:
        form = GameSize()

    data['form'] = form

    return render(request, 'games/games_settings.html', context=data)


@login_required
def custom_logout(request):
    logout(request)
    session_info = Lobby.objects.filter(player_id=request.user.id, is_ended=False)
    if session_info:
        for el in session_info:
            el.is_ended = True
        session_info.save()
    return redirect('/')


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # получаем имя пользователя и пароль из формы
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # выполняем аутентификацию
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/new_user.html', context={'form': form})


def test(request):
    return render(request, 'games/test.html')


# UPDATE games_question
# SET is_answered = false
# WHERE is_answered = true


# SELECT *
# FROM games_question
# ORDER BY theme_id, question_value
