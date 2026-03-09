from django.shortcuts import render, redirect, get_object_or_404
import requests
from datetime import datetime
from .models import Book
from django.urls import reverse
from .forms import SignUpForm
from django.core.cache import cache
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


# Create your views here.


def home(request):
    trending_books = []

    try:
        response = requests.get("https://openlibrary.org/subjects/popular.json?limit=5")
        data = response.json()

        for book in data.get("works", []):
           
            olid = book.get("key").lstrip("/")  
            
            trending_books.append({
                "title": book.get("title"),
                "author": ", ".join([author["name"] for author in book.get("authors", [])]) if book.get("authors") else "Unknown",
                "cover_url": f"http://covers.openlibrary.org/b/id/{book['cover_id']}-M.jpg" if book.get("cover_id") else "",
                "url": f"/books/{olid}/"  
            })
    except Exception as e:
        print("Error fetching trending books:", e)

    return render(request, "books/home.html", {"trending_books": trending_books})

def search_books(request):
    query = request.GET.get("q")
    next_page = request.GET.get("next", "/")  
    results = []

    if query:
        url = f"https://openlibrary.org/search.json?q={query}"
        response = requests.get(url)
        data = response.json()
        results = data.get("docs", [])

    context = {
        "results": results,
        "query": query,
        "next_page": next_page,
    }
    return render(request, "books/search.html", context)

def book_detail(request, olid):
    url = f"https://openlibrary.org/{olid}.json"
    response = requests.get(url)
    data = response.json()

    # Description
    description = ""
    if "description" in data:
        if isinstance(data["description"], dict):
            description = data["description"].get("value", "")
        else:
            description = data["description"]

    # Authors
    authors = []
    for author_ref in data.get("authors", []):
        author_key = author_ref.get("author", {}).get("key")
        if author_key:
            r = requests.get(f"https://openlibrary.org/{author_key.lstrip('/')}.json")
            if r.status_code == 200:
                author_data = r.json()
                name = author_data.get("name")
                if name:
                    authors.append(name)

    if not authors:
        authors = ["Unknown Author"]

    # Published date
    raw_date = data.get("first_publish_date") or data.get("created", {}).get("value", None)
    published_date = "Unknown"
    if raw_date:
        try:
            
            if len(raw_date) == 4:  
                published_date = f"01/01/{raw_date}"
            else:
                dt = datetime.fromisoformat(raw_date)
                published_date = dt.strftime("%m/%d/%Y")
        except Exception:
            published_date = raw_date 
# Global rating
    rating = None
    try:
        rating_url = f"https://openlibrary.org/{olid}/ratings.json"
        r = requests.get(rating_url)
        if r.status_code == 200:
            rating_data = r.json()
            
            summary = rating_data.get("summary", {})
            avg = summary.get("average")
            if avg is not None:
                rating = round(float(avg), 2)  
    except Exception as e:
        print("Error fetching rating:", e)
        rating = None
       # Genres / subjects
    genres = data.get("subjects", [])  

    previous_page = request.META.get('HTTP_REFERER', '/')

    context = {
        "book": data,
        "description": description,
        "published_date": published_date,
        "authors": authors,
        "rating": rating,
        "genres": genres,
        "previous_page": previous_page
    }

    return render(request, "books/book_detail.html", context)
@login_required
def add_book(request):
    if request.method == "POST":
        Book.objects.create(
            user=request.user,
            open_library_id = request.POST.get("olid"),
            title = request.POST.get('title'),
            authors = request.POST.get("authors"),
            cover_id = request.POST.get("cover_id"),
            status = "want"
        )
        return redirect ("my_books")
@login_required
def my_books(request):
    want = Book.objects.filter(user=request.user,status="want")
    reading = Book.objects.filter(user=request.user, status="reading")
    completed = Book.objects.filter(user=request.user,status="completed")

    return render(request, "books/my_books.html", {
        "want": want,
        "reading": reading,
        "completed": completed
    })

@login_required
def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        # Update status
        book.status = request.POST.get("status")
        # Update notes
        book.notes = request.POST.get("notes")
        # Update rating safely
        rating_value = request.POST.get("rating")
        if rating_value in [None, ""]:
            book.rating = None
        else:
            try:
                book.rating = float(rating_value)
            except ValueError:
                book.rating = None

        book.save()
        return redirect("my_books")

    # GET request
    return render(request, "books/update_book.html", {"book": book})

@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect("my_books")

def signup(request):
    error_message = ''

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid sign up - please try again'
    else:
        form = SignUpForm()

    context = {
        'form': form,
        'error_message': error_message
    }

    return render(request, 'books/signup.html', context)