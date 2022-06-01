from django.urls import path

from . import views

urlpatterns = [
    path('all', views.get_all_messages,
         name='get_all_messages'),
    path('unread', views.get_all_unread_messages,
         name='get_all_unread_messages'),
    path('new_message', views.write_a_message,
         name='write_a_message'),
    path('read', views.read_a_message,
         name='read_a_message'),
    path('delete', views.delete_a_message,
         name='delete_a_message'),
]
