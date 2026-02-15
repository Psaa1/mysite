from django.db import models

# Create your models here.

from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    published_year = models.PositiveIntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"


class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="loans")
    borrower_name = models.CharField(max_length=200)
    loan_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-loan_date"]

    @property
    def is_returned(self) -> bool:
        return self.returned_date is not None

    def __str__(self) -> str:
        return f"{self.book.title} -> {self.borrower_name} (due {self.due_date})"
