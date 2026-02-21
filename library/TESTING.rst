Library App Testing Guide
=========================

Overview
--------

This document describes the unit test coverage for the ``library`` app.
The suite is implemented in ``library/tests.py`` using Django's
``django.test.TestCase`` and follows:

* PEP 8 style conventions for Python code formatting.
* PEP 287-compatible docstring conventions (reStructuredText).

Coverage
--------

The current suite covers these areas:

1. Home page aggregates and rendering

   * Route availability and template selection.
   * Correct dashboard counts:
     ``total_books``, ``available_books``, and ``active_loans``.
   * Presence of key dashboard labels.

2. Books page behavior

   * Full list rendering without a search query.
   * Search matching by title and author.
   * Query normalization (whitespace stripping).
   * Query-specific and generic empty states.
   * Semantic status badge rendering (available vs checked out).

3. Loans page behavior

   * Route availability, template selection, and ``today`` context value.
   * Ordering based on ``Loan.Meta.ordering``.
   * Status rendering for active, overdue, and returned loans.
   * Empty-state behavior when no loans exist.

4. Model helper behavior

   * ``Book.__str__`` includes title and author.
   * ``Loan.is_returned`` reflects ``returned_date`` state.


Running Tests
-------------

From the project root (directory containing ``manage.py``), run:

.. code-block:: bash

   python manage.py test library

Optional (verbose output):

.. code-block:: bash

   python manage.py test library -v 2


Maintenance Notes
-----------------

* Keep tests deterministic by using explicit fixture dates.
* Prefer testing user-observable behavior (rendered output and context).
* Add or update tests whenever templates, view logic, or model helpers change.
