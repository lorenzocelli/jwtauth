from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logged/', views.logged_view, name='logged1'),
    path('logged_/', views.LoggedView.as_view(), name='logged2'),
    path('username/', views.username_view, name='username'),
    path('logout', views.logout_view, name='logout'),
]