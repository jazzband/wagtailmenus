============================
Release packaging guidelines
============================

Preparing for a new release
===========================

Follow the steps outlined below to prep changes in your fork:

1.  Merge any changes from ``upstream/master`` into your fork's ``master``
    branch.

    .. code-block:: console

        git fetch upstream
        git checkout master
        git merge upstream/master

2.  From your fork's ``master`` branch, create a new branch for preparing the
    release, e.g.:

    .. code-block:: console

        git checkout -b release-prep/2.X.X

3.  Update ``__version__`` in ``wagtailmenus/__init__.py`` to reflect the new
    release version.

4.  Make sure ``CHANGELOG.md`` is updated with details of any changes since
    the last release.

5.  Make sure the release notes for the new version have been created /
    updated in ``docs/source/releases/`` and are referenced in 
    ``docs/source/releases/index.rst``. Be sure to remove the '(alpha)' or 
    '(beta)' from the heading in the latest release notes, as well as the
    'Wagtailmenus X.X is in the alpha stage of development' just below.

6.  If releasing a 'final' version, following an 'alpha' or 'beta' release, 
    ensure the ``a`` or ``b`` is removed from the file name for the release, 
    and the reference to it in ``docs/source/releases/index.rst``.

7.  ``cd`` into the ``docs`` directory to check documentation-related stuff:

    .. code-block:: console

        cd docs


8.  Check for and correct any spelling errors raised by sphinx:

    .. code-block:: console

        make spelling

9.  Check that the docs build okay, and fix any errors raised by sphinx:

    .. code-block:: console

        make html

10. Commit changes so far:

    .. code-block:: console
    
        git commit -am 'Bumped version and updated release notes'
       
11. Update the source translation files by running the following from the
    project's root directory:

    .. code-block:: console

        # Update source files
        django-admin.py makemessages -l en

        # Commit the changes
        git commit -am 'Update source translation files'

12. Push all outstanding changes to GitHub:

    .. code-block:: console
    
        git push

13. Submit your changes as a PR to the main repository via
    https://github.com/jazzband/wagtailmenus/compare


Packaging and pushing to PyPi
=============================

When satisfied with the PR for preparing the files:

1.  From https://github.com/jazzband/wagtailmenus/pulls, merge the PR into the
    ``master`` branch using the "merge commit" option.

2.  Locally, ``cd`` to the project's root directory, checkout the ``master``
    branch, and ensure the local copy is up-to-date: 

    .. code-block:: console
        
        source .venv/bin/activate
        cd ../path-to-original-repo
        git checkout master
        git pull

3.  Ensure dependencies are up-to-date by running:

    .. code-block:: console

        pip install -e '.[deployment]' -U

4.  Create a new tag for the new version and push that too. Github Actions should deploy the new version directly to PyPI once it's finished building:

    .. code-block:: console
        
        git tag -a v2.X
        git push --tags

5. Edit the release notes for the release from
    https://github.com/jazzband/wagtailmenus/releases, by copying and pasting
    the content from ``docs/releases/x.x.x.rst``

6. Crack open a beer - you earned it!
