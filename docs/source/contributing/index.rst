============================
Contributing to wagtailmenus
============================

Hey! First of all, thanks for considering to help out!

We welcome all support, whether on bug reports, code, reviews, tests, documentation, translations or just feature requests.

.. contents::
    :local:
    :depth: 2


Using the issue tracker
=======================

The `issue tracker <https://github.com/jazzband/wagtailmenus/issues>`_ is the preferred channel for bug reports, features requests and submitting pull requests. Please don't use the issue tracker for support requests. If you need help with something that isn't a bug, you can join our `Wagtailmenus support group <https://groups.google.com/forum/#!forum/wagtailmenus-support-requests>`_ and ask your question there.


Submitting translations
=======================

Please submit any new or improved translations (both `.po` and `.mo` files) as a new PR.


Contributing code changes via pull requests
===========================================

If there are any open issues you think you can help with, please comment on the issue and state your intent to help. Or, if you have an idea for a feature you'd like to work on, raise it as an issue. Once a core contributor has responded and is happy for you to proceed with a solution, you should `create your own fork <https://help.github.com/articles/fork-a-repo/>`_ of wagtailmenus, make the changes there. Before committing any changes, we highly recommend that you create a new branch, and keep all related changes within that same branch. When you've finished making your changes, and the tests are passing, you can then submit a pull request for review.


What your pull request should include
-------------------------------------

In order to be accepted/merged, your pull request will need to meet the
following criteria:

1.  Documentation updates to cover any new features or changes.

2.  If you're not in the list already, add a new line to ``CONTRIBUTORS.md``
    (under the 'Contributors' heading) with your name, company name, and an optional twitter handle / email address.

3.  For all new features, please add additional unit tests to
    ``wagtailmenus.tests``, to test what you've written. Although the quality
    of unit tests is the most important thing (they should be readable, and
    test the correct thing / combination of things), code coverage is important
    too, so please ensure as many lines of your code as possible are accessed
    when the unit tests are run.


Developing locally
==================

If you'd like a runnable Django project to help with development of wagtailmenus, follow these steps to get started. The development environment has ``django-debug-toolbar`` and some other helpful packages installed to help you debug with your code as you develop:

1.  In a Terminal window, ``cd`` to the project's root directory, and run:

    .. code-block:: console

        python3 -m venv .venv
        pip install -e '.[development]' -U
        source .venv/bin/activate

2.  Create a copy of the development settings:

    .. code-block:: console

        cp wagtailmenus/settings/development.py.example wagtailmenus/settings/development.py

3.  Create a copy of the development urls:

    .. code-block:: console

        cp wagtailmenus/development/urls.py.example wagtailmenus/development/urls.py

4.  Create ``manage.py`` by copying the example provided:

    .. code-block:: console

        cp manage.py.example manage.py

5.  Run the migrate command to set up the database tables:

    .. code-block:: console

        python manage.py migrate

6.  To load some test data into the database, run:

    .. code-block:: console

        python manage.py loaddata wagtailmenus/tests/fixtures/test.json

7.  Create a new superuser that you can use to access the CMS:

    .. code-block:: console

        python manage.py createsuperuser

8.  Run the project using the standard Django command:

    .. code-block:: console

        python manage.py runserver

Your local copies of ``settings/development.py`` and ``manage.py`` will be ignored by git when you push any changes, as will anything you add to the ``wagtailmenus/development/`` directory.


Running the test suite
======================

It's important that any new code is tested before submitting. To quickly test code in your active development environment, you should first install all of the requirements by running:

.. code-block:: console

    source .venv/bin/activate
    pip install -e '.[testing]' -U

Then, run the following command to execute tests:

.. code-block:: console

    python runtests.py

Or if you want to measure test coverage, run:

.. code-block:: console

    coverage run --source=wagtailmenus runtests.py
    coverage report

Testing in a single environment is a quick and easy way to identify obvious issues with your code. However, it's important to test changes in other environments too, before they are submitted. In order to help with this, wagtailmenus is configured to use ``tox`` for multi-environment tests. They take longer to complete, but running them is as simple as running:

.. code-block:: console

    tox

You might find it easier to set up a Travis CI service integration for your fork in GitHub (look under **Settings > Apps and integrations** in GitHub's web interface for your fork), and have Travis CI run tests whenever you commit changes. The test configuration files already present in the project should work for your fork too, making it a cinch to set up.


Building the documentation
==========================

1. First install the necessary requirements by running:

    .. code-block:: console

        source .venv/bin/activate
        pip install -e '.[docs]' -U

2. ``cd`` into the ``docs`` directory to do documentation-related stuff:

    .. code-block:: console

        cd docs

3. Check for and correct any spelling errors raised by sphinx. If you're on Windows, please see `how to run make commands on Windows <http://gnuwin32.sourceforge.net/packages/make.htm>`_:

    .. code-block:: console

        make spelling

4. Check that the docs build okay, and look out for errors or warnings:

    .. code-block:: console

        make html


Other topics
============

.. toctree::
    :maxdepth: 1

    packaging_releases
