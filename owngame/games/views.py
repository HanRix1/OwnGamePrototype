from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.db.models.functions import Rank, RowNumber
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.db.models import Count, Max, Window
from games.models import Question, Theme, Lobby, GameSizes
from .forms import GetAnswer, GameSize
from random import randint


def index(request):
    menu = {'title': "Начать игру", 'url_name': 'start_game'}
    return render(request, 'games/index.html', context=menu)


def info(request):
    data = {'title': 'Информация о сайте',
            'subtitle': 'Здесь будет размещена вся информация о сайте'}
    return render(request, 'games/info.html', data)


@login_required
def results(request):
    data = {}
    players_list = []
    join = (Lobby.objects
            .values('player_id_id__username')
            .annotate(total=Max('score'))
            .annotate(rank=Window(
                expression=RowNumber(),
                order_by=('-total',)
            ))
            .order_by('-total'))

    data['players'] = join
    return render(request, 'games/players_results.html', context=data)


@login_required
def show(request, player_id):
    return HttpResponse(f'Результаты игры с номером:{player_id}')


@login_required
def gamestart(request):
    data = {}
    qs_db = {}

    session_info = Lobby.objects.filter(player_id_id=request.user.id, is_ended=False)
    if not session_info:
        rand_values = []
        positions = []
        sizes = get_object_or_404(GameSizes)
        themes = get_list_or_404(Theme)

        for i in range(sizes.theme_num):
            buf = get_list_or_404(
                Question.objects
                .values('question_value')
                .filter(theme_id=themes[i])
                .annotate(total=Count('id'))
            )
            for j in range(sizes.question_num):
                rand_values.append(randint(0, buf[j]['total'] - 1))
                positions.append(buf[j]['total'])

        new_session = Lobby(
            player_id_id=request.user.id,
            theme_num=sizes.theme_num,
            question_num=sizes.question_num,
            pos=positions,
            rand_value=rand_values,
            map=[0 for i in range(sizes.theme_num * sizes.question_num)]
        )
        new_session.save()

    session_info = get_object_or_404(Lobby.objects.filter(player_id_id=request.user.id, is_ended=False))
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
            if question.id in session_info.map:
                buf.append(Question())
            else:
                flag = True
                buf.append(question)
            k += pos[m]
            m += 1
        qs_db[themes[i].theme_name] = buf

    if not flag:
        #блок обратки сценария по завершению игры
        session_info.is_ended = True
        session_info.save()
        return redirect('result')

    data['qs'] = qs_db
    return render(request, 'games/game.html', context=data)


def contact(request):
    return HttpResponse("Обратная связь")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


@login_required
def raise_question(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    session_info = get_object_or_404(Lobby.objects.filter(player_id_id=request.user.id, is_ended=False))
    if request.method == 'POST':
        form = GetAnswer(request.POST)
        if form.is_valid():
            if form.clean_answer_text().lower() == question.answer_text.lower():
                session_info.score += question.question_value
            else:
                session_info.score -= question.question_value
            session_info.map.append(question.id)
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
    sizes = get_object_or_404(GameSizes)
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
            size = get_object_or_404(GameSizes)
            size.theme_num = form.get_themes_num()
            size.question_num = form.get_questions_num()
            size.save()
            return redirect('/admin')
    else:
        form = GameSize()

    data['form'] = form

    return render(request, 'games/games_settings.html', context=data)


@login_required
def custom_logout(request):
    session_info = Lobby.objects.filter(player_id_id=request.user.id, is_ended=False)
    session_info.delete()
    logout(request)
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
