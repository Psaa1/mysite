
# Create your views here.
from django.shortcuts import render
from django.utils import timezone
from .models import Book, Loan


def home(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(is_available=True).count()
    active_loans = Loan.objects.filter(returned_date__isnull=True).count()

    return render(
        request,
        "library/home.html",
        {
            "total_books": total_books,
            "available_books": available_books,
            "active_loans": active_loans,
        },
    )


def book_list(request):
    q = request.GET.get("q", "").strip()
    books = Book.objects.all()
    if q:
        books = books.filter(title__icontains=q) | books.filter(author__icontains=q)

    return render(request, "library/book_list.html", {"books": books, "q": q})


def loan_list(request):
    loans = Loan.objects.select_related("book").all()
    return render(
        request,
        "library/loan_list.html",
        {"loans": loans, "today": timezone.localdate()},
    )
