from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('<int:page_no>', views.user_detail, name='user'),
    path('logout', views.logout, name='logout'),
    path('delete/<int:slug>', views.delete_user, name='delete'),
    path('update/<int:slug>', views.update_user, name='update')
]