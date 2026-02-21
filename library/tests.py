"""Unit tests for the ``library`` app.

This module verifies behavior for:

* Dashboard aggregates on the home page.
* Search, status, and empty-state behavior on the books page.
* Loan status rendering (active, returned, overdue) on the loans page.
* Core model convenience behavior such as string representations.

The tests use Django's ``TestCase`` to provide transactional isolation and
fast database setup/teardown for each test method.
"""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Book, Loan


class HomeViewTests(TestCase):
    """Tests for the dashboard home view."""

    @classmethod
    def setUpTestData(cls):
        """Create catalog and loan fixtures shared by all tests in this class."""
        cls.available_book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            isbn="9780441172719",
            published_year=1965,
            is_available=True,
        )
        cls.unavailable_book = Book.objects.create(
            title="The Hobbit",
            author="J. R. R. Tolkien",
            isbn="9780261103344",
            published_year=1937,
            is_available=False,
        )

        today = timezone.localdate()
        Loan.objects.create(
            book=cls.available_book,
            borrower_name="Alice",
            loan_date=today - timedelta(days=3),
            due_date=today + timedelta(days=10),
            returned_date=today - timedelta(days=1),
        )
        Loan.objects.create(
            book=cls.unavailable_book,
            borrower_name="Bob",
            loan_date=today - timedelta(days=2),
            due_date=today + timedelta(days=7),
            returned_date=None,
        )

    def test_home_view_renders_expected_template_and_context(self):
        """Home page should render counts for total, available, and active."""
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/home.html")
        self.assertEqual(response.context["total_books"], 2)
        self.assertEqual(response.context["available_books"], 1)
        self.assertEqual(response.context["active_loans"], 1)

    def test_home_view_contains_expected_dashboard_labels(self):
        """Home page should contain user-facing dashboard labels."""
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Library Dashboard")
        self.assertContains(response, "Total Books")
        self.assertContains(response, "Available Books")
        self.assertContains(response, "Active Loans")


class BookListViewTests(TestCase):
    """Tests for the books listing and search behavior."""

    @classmethod
    def setUpTestData(cls):
        """Create book fixtures with varying availability and metadata."""
        cls.dune = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            isbn="9780441172719",
            published_year=1965,
            is_available=True,
        )
        cls.hobbit = Book.objects.create(
            title="The Hobbit",
            author="J. R. R. Tolkien",
            isbn="9780261103344",
            published_year=1937,
            is_available=False,
        )
        cls.unknown_year = Book.objects.create(
            title="Mystery Book",
            author="Anon Writer",
            isbn="9780000000002",
            published_year=None,
            is_available=True,
        )

    def test_book_list_without_query_returns_all_books(self):
        """Books page without ``q`` should list all catalog entries."""
        response = self.client.get(reverse("book_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/book_list.html")
        self.assertQuerySetEqual(
            response.context["books"].order_by("id"),
            [self.dune, self.hobbit, self.unknown_year],
            transform=lambda item: item,
        )

    def test_book_search_matches_title(self):
        """Search should match books by case-insensitive title text."""
        response = self.client.get(reverse("book_list"), {"q": "dune"})

        self.assertEqual(list(response.context["books"]), [self.dune])
        self.assertContains(response, "Showing results for")
        self.assertContains(response, "Clear")

    def test_book_search_matches_author(self):
        """Search should match books by case-insensitive author text."""
        response = self.client.get(reverse("book_list"), {"q": "tolkien"})

        self.assertEqual(list(response.context["books"]), [self.hobbit])

    def test_book_search_strips_whitespace_in_query(self):
        """Search query should be stripped before filtering and rendered back."""
        response = self.client.get(reverse("book_list"), {"q": "  dune  "})

        self.assertEqual(response.context["q"], "dune")
        self.assertEqual(list(response.context["books"]), [self.dune])

    def test_book_search_empty_result_message_for_query(self):
        """Books page should show query-specific empty state when no match."""
        response = self.client.get(reverse("book_list"), {"q": "notfound"})

        self.assertContains(response, "No books match your search.")

    def test_book_list_empty_catalog_message_without_query(self):
        """Books page should show generic empty state when catalog is empty."""
        Book.objects.all().delete()

        response = self.client.get(reverse("book_list"))
        self.assertContains(response, "No books in catalog yet.")

    def test_book_list_renders_human_readable_status_badges(self):
        """Books page should render semantic availability badges."""
        response = self.client.get(reverse("book_list"))

        self.assertContains(response, "Available")
        self.assertContains(response, "Checked out")
        self.assertContains(response, "Unknown")


class LoanListViewTests(TestCase):
    """Tests for the loans listing and status rendering."""

    @classmethod
    def setUpTestData(cls):
        """Create loan fixtures covering active, overdue, and returned states."""
        cls.today = timezone.localdate()

        cls.active_book = Book.objects.create(
            title="Active Book",
            author="Author One",
            isbn="9780000000003",
            is_available=False,
        )
        cls.overdue_book = Book.objects.create(
            title="Overdue Book",
            author="Author Two",
            isbn="9780000000004",
            is_available=False,
        )
        cls.returned_book = Book.objects.create(
            title="Returned Book",
            author="Author Three",
            isbn="9780000000005",
            is_available=True,
        )

        cls.active_loan = Loan.objects.create(
            book=cls.active_book,
            borrower_name="Chris",
            loan_date=cls.today - timedelta(days=2),
            due_date=cls.today + timedelta(days=3),
            returned_date=None,
        )
        cls.overdue_loan = Loan.objects.create(
            book=cls.overdue_book,
            borrower_name="Dana",
            loan_date=cls.today - timedelta(days=7),
            due_date=cls.today - timedelta(days=1),
            returned_date=None,
        )
        cls.returned_loan = Loan.objects.create(
            book=cls.returned_book,
            borrower_name="Evan",
            loan_date=cls.today - timedelta(days=10),
            due_date=cls.today - timedelta(days=4),
            returned_date=cls.today - timedelta(days=2),
        )

    def test_loan_list_view_renders_template_and_context(self):
        """Loans page should render expected template and provide ``today``."""
        response = self.client.get(reverse("loan_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/loan_list.html")
        self.assertIn("today", response.context)
        self.assertEqual(response.context["today"], timezone.localdate())

    def test_loan_list_orders_rows_by_most_recent_loan_date(self):
        """Loans should be ordered by descending loan date via model meta."""
        response = self.client.get(reverse("loan_list"))

        ordered_ids = list(response.context["loans"].values_list("id", flat=True))
        expected = [
            self.active_loan.id,
            self.overdue_loan.id,
            self.returned_loan.id,
        ]
        self.assertEqual(ordered_ids, expected)

    def test_loan_list_renders_active_overdue_and_returned_badges(self):
        """Loans page should expose distinct statuses for each loan state."""
        response = self.client.get(reverse("loan_list"))

        self.assertContains(response, "Active")
        self.assertContains(response, "Overdue")
        self.assertContains(response, "Returned")

    def test_loan_list_empty_state(self):
        """Loans page should show empty-state text when no loans exist."""
        Loan.objects.all().delete()

        response = self.client.get(reverse("loan_list"))
        self.assertContains(response, "No loans found.")


class ModelBehaviorTests(TestCase):
    """Targeted tests for model helper behavior."""

    def test_book_string_representation_contains_title_and_author(self):
        """``Book.__str__`` should include both title and author values."""
        book = Book.objects.create(
            title="Neuromancer",
            author="William Gibson",
            isbn="9780441569595",
        )

        result = str(book)
        self.assertIn("Neuromancer", result)
        self.assertIn("William Gibson", result)

    def test_loan_is_returned_property(self):
        """``Loan.is_returned`` should reflect returned date presence."""
        book = Book.objects.create(
            title="Hyperion",
            author="Dan Simmons",
            isbn="9780553283686",
        )
        today = timezone.localdate()

        active_loan = Loan.objects.create(
            book=book,
            borrower_name="Taylor",
            due_date=today + timedelta(days=5),
        )
        returned_loan = Loan.objects.create(
            book=book,
            borrower_name="Jordan",
            due_date=today + timedelta(days=8),
            returned_date=today,
        )

        self.assertFalse(active_loan.is_returned)
        self.assertTrue(returned_loan.is_returned)
