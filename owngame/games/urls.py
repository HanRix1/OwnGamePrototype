from django.urls import path, register_converter, include
from . import views
from . import convertors

register_converter(convertors.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.index, name='home'),  # http://127.0.0.1:8000/,
    path('info', views.info, name='info'),
    path('res/', views.results, name='result'),  # http://127.0.0.1:8000/res/
    path('res/<int:player_id>/', views.show, name='result_for_person'),
    path('size_init/', views.size_init, name='size_init'),
    path('gamestart/', views.gamestart, name='start_game'),
    path('contact/', views.contact, name='contact'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('registration/', views.registration, name='registration'),
    path('test/', views.test, name='test'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('gamestart/<int:question_pk>/', views.raise_question, name='open_question'),
]
