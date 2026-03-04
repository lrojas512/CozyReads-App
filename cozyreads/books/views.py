from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import Book
from django.urls import reverse

# Create your views here.
def home (request):
    return render(request, "books/home.html")

def search_books(request):
    query = request.GET.get("q")
    results = []

    if query:
        url = f"https://openlibrary.org/search.json?q={query}"
        response = requests.get(url)
        data = response.json()
        results = data["docs"][:10]
    
    return render(request, "books/search.html", {
        "results": results
    })

def add_book(request):
    if request.method == "POST":
        Book.objects.create(
            open_library_id = request.POST.get("olid"),
            title = request.POST.get('title'),
            authors = request.POST.get("authors"),
            cover_id = request.POST.get("cover_id"),
            status = "want"
        )
        return redirect ("my_books")

def my_books(request):
    want = Book.objects.filter(status="want")
    completed = Book.objects.filter(status="completed")

    return render(request, "books/my_books.html", {
        "want": want,
        "completed": completed
    })


def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        book.status = request.POST.get("status")
        book.notes = request.POST.get("notes")
        book.rating = request.POST.get("rating")
        book.save()
        return redirect("my_books")

    return render(request, "books/update_book.html", {"book": book})


def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect("my_books")