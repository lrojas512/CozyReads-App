from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search_books, name="search"),
    path("add/", views.add_book, name="add_book"),
    path("mybooks/", views.my_books, name="my_books"),
    path("update/<int:pk>/", views.update_book, name="update_book"),
    path("delete/<int:pk>/", views.delete_book, name="delete_book"),
]