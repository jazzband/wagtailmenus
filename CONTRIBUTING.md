# Contributing to wagtailmenus

Hey! First of all, thanks for considering to help out!

We welcome all support, whether on bug reports, code, reviews, tests, 
documentation, translations or just feature requests.

## Using the issue tracker

The [issue tracker](https://github.com/rkhleics/wagtailmenus/issues) is
the preferred channel for bug reports, features requests and 
submitting pull requests. Please don't use the issue tracker
for support requests. If you need help with something that isn't a bug, you can
join our [Wagtailmenus support group](https://groups.google.com/forum/#!forum/wagtailmenus-support-requests) and ask your question there.

## Contributing code via pull requests

If there are any open issues you think you can help with, please comment
on the issue and state your intent to help. Or, if you have an idea for a
feature you'd like to work on, raise it as an issue. Once a core contributor 
has responded and is happy for you to proceed with a solution, you should 
[create your own fork](https://help.github.com/articles/fork-a-repo/) of 
`wagtailmenus`, make the changes there (before committing any changes, we
highly recommend that you create a new branch, and keep all related changes
within that same branch). When you've finished making your changes, you can
then submit a pull request for review.

### What your pull request should include

In order to be accepted/merged, your pull request will need to meet the
following criteria:

1. Any new features must be documented in `README.md`

2. If you're not in the list already, add a new line to `CONTRIBUTORS.md`
   (under the 'Contributors' heading) with your name, company name, and
   an optional twitter handle / email address.

3. Add a concise description of what you have changed to `CHANGELOG.md`.

4. For all new features, please add additional unit tests to
   `wagtailmenus.tests`, to test what you've written. Although the quality
   of unit tests is the most important thing (they should be readable, and 
   test the correct thing / combination of things), code coverage is
   important too, so please ensure as many lines of your code as possible
   are accessed when the unit tests are run.


### Developing locally

If you'd like a runnable Django project to help with development of
wagtailmenus, follow these steps to get started (Mac only). The development
environment has django-debug-toolbar and some other helpful packages installed
to help you debug with your code as you develop:

1. In a Terminal window, cd to the `wagtailmenus` root directory, and run:  
   `pip install -r requirements/development.txt`
2. Now create a copy of the development settings:  
   `cp wagtailmenus/settings/development.py.example wagtailmenus/settings/development.py`
3. Now create a copy of the development urls:  
   `cp wagtailmenus/development/urls.py.example wagtailmenus/development/urls.py`
4. Now create `manage.py` by copying the example provided:  
   `cp manage.py.example manage.py`
5. To load some test data into the database, run the following:  
   `python manage.py loaddata wagtailmenus/tests/fixtures/test.json`
6. Now run the following and follow the prompts to set up a new superuser:  
   `python manage.py createsuperuser`
7. Now run the project using the standard Django command:  
   `python manage.py runserver`

Your local copies of `settings/development.py` and `manage.py` should be
ignored by git when you push any changes, as will anything you add to the
`wagtailmenus/development/` directory.

## Testing locally

It's important that any new code is tested before submitting. To quickly
test code in your active development environment, you should first install all 
of the requirements by running:

`pip install -r requirements/testing.txt`

Then, run the following command to execute tests:

`python runtests.py`

Or if you want to measure test coverage, you can run:

`coverage --source=wagtailmenus runtests.py`

followed by `coverage report` or `coverage html` (depending on what you find
more useful).

Testing in a single environment is a quick and easy way to identify obvious
issues with your code. However, it's important to test changes in other
environments too, before they are submitted. In order to help with this,
wagtailmenus is configured to use `tox` for multi-environment tests. They
take longer to complete, but running them is as simple as entering the
following command:

`tox`

## Translations

Please submit any new or improved translations through [Transifex](https://www.transifex.com/rkhleics/wagtailmenus/).
