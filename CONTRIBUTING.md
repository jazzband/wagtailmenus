# Contributing to wagtailmenus

Hey! First of all, thanks for considering to help out!

We welcome all support, whether on bug reports, code, design, reviews, tests, 
documentation, translations or just feature requests.

## Using the issue tracker

The [issue tracker](https://github.com/rkhleics/wagtailmenus/issues) is
the preferred channel for [bug reports](#bugs), [features requests](#features)
and [submitting pull requests](#pull-requests). Please don't use the issue tracker
for support requests. If you need help with something that isn't a bug, you can
join our [Wagtailmenus support group](https://groups.google.com/forum/#!forum/wagtailmenus-support-requests) and ask your question there.

## Contributing new code

If there are any open issues you think you can help with, please comment
on the issue and state your intent to help. Or, if you have an idea for a
feature you'd like to work on, raise it as an issue. Once a core contributor 
has responded and is happy for you to proceed with a solution, you should 
[create your own fork](https://help.github.com/articles/fork-a-repo/) of 
`wagtailmenus`, make the changes there (Before committing any changes, we
highly recommend that you create a new branch, and keep all related changes
within that same branch). When you've finished making your changes, you can
then submit a pull request for review.

## Code quality

Each pull request will need the following before it can be accepted/merged:

1. Any new features documented in `README.md`

2. A new line adding to `CONTRIBUTORS.md` (under the 'Contributors' heading)
   with your name, company name, and option twitter handle / email address.

3. A note adding to `CHANGELOG.md`, explaining the feature or fix you made.

4. New unit tests adding to `wagtailmenus.tests`, to test the code you've
   written. Although the quality of unit tests is the most important thing 
   (they must be readable, and test the correct thing / combination of things), 
   code coverage is important too (making each line of code runs during unit
   tests).

## Running tests locally

It's important that any new code is tested before submitting. To quickly
test code in your active development environment, you should first install all 
of the requirements from `requirements.txt`, by doing something like:

`pip install -r requirements.txt`

Then, run the following command to execute tests:

`python runtests.py`

Or if you want to measure test coverage, you can run:

`coverage --source=wagtailmenus runtests.py`

followed by `coverage report` or `coverage html` (depending on what you find
more useful).

Testing in a single environment is a quick and easy way to identify obvious
issues with your code. However, it's important to test other environments too.
before submitting code. Wagtailmenus is configured to use `tox` for
multi-environment tests. They take longer to complete, but running them is as
simple as entering the following command:

`tox`
