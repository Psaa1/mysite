from django.contrib import admin

# Register your models here.

from .models import Book, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "published_year", "is_available")
    search_fields = ("title", "author", "isbn")
    list_filter = ("is_available", "published_year")
    ordering = ("title",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "borrower_name", "loan_date", "due_date", "returned_date", "is_returned")
    search_fields = ("borrower_name", "book__title", "book__author", "book__isbn")
    list_filter = ("loan_date", "due_date", "returned_date")
    autocomplete_fields = ("book",)

    @admin.display(boolean=True, description="Returned?")
    def is_returned(self, obj: Loan) -> bool:
        return obj.returned_date is not None

