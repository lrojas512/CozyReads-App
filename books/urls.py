from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search_books, name="search"),
    path('books/<path:olid>/', views.book_detail, name='book_detail'),    path("add/", views.add_book, name="add_book"),
    path("mybooks/", views.my_books, name="my_books"),
    path("update/<int:pk>/", views.update_book, name="update_book"),
    path("delete/<int:pk>/", views.delete_book, name="delete_book"),

    #User
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="books/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name= "logout"),
]