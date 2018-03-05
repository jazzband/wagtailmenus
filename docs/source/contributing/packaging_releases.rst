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

2.  From your fork's ``master`` branch, create a new branch for prepping the
    release, e.g.:

    .. code-block:: console

        git checkout -b release-prep/2.X.X

3.  Update ``__version__`` in ``wagtailmenus/__init__.py`` to reflect the new
    release version.

4.  Make sure ``CHANGELOG.md`` is updated with details of any changes since
    the last release.

5.  Make sure the release notes for the new version have been created /
    updated in ``docs/source/releases/`` and are referenced in 
    ``docs/source/releases/index.rst``.

6.  If releasing a 'final' version, following an 'alpha' or 'beta' release, 
    ensure the ``a`` or ``b`` is removed from the file name for the release, 
    and the reference to it in ``docs/source/releases/index.rst``.

7.  Check that the docs build okay, and fix any errors raised by sphinx:

    .. code-block:: console

        make html

8.  Commit changes so far:

    .. code-block:: console
    
        git commit -am 'Bumped version and updated release notes'
       
8.  Update the source translation files by running the following from the
    project's root directory:

    .. code-block:: console

        # Update source files
        django-admin.py makemessages -l en

        # Commit the changes
        git commit -am 'Update source translation files'

9.  Push all oustanding changes to github:

    .. code-block:: console
    
        git push

10. Submit your changes as a PR to the main repo via
    https://github.com/rkhleics/wagtailmenus/compare


Packaging and pushing to PyPi
=============================

When satisfied with the PR for prepping the files:

1.  From https://github.com/rkhleics/wagtailmenus/pulls, merge the PR into the
    ``master`` branch using the "merge commit" option.

2.  Locally, cd to the project's root directory, checkout the ``master``
    branch, and ensure the local copy is up-to-date: 

    .. code-block:: console
        
        workon wagtailmenus
        cd ../path-to-original-repo
        git checkout master
        git pull

3.  Ensure dependencies are up-to-date by running:

    .. code-block:: console

        pip install -e '.[testing,docs]' -U

4.  Push any updated translation source files to Transifex:

    .. code-block:: console

        tx push -s -l en

5.  Pull down updated translations from Transifex:

    .. code-block:: console

        tx pull --a
        rm -r wagtailmenus/locale/en_GB/
        git add *.po

6.  Convert the .po files to .mo for each language by running:
    
    .. code-block:: console

         find . -name *.po -execdir msgfmt django.po -o django.mo \;

7.  Commit and push all changes so far:
    
    .. code-block:: console

        git commit -am 'Pulled updated translations from Transifex and converted to .mo'
        git push

8.  Create a new tag for the new version and push that too:

    .. code-block:: console
        
        git tag -a v2.X.X
        git push --tags

9.  Create a new source distribution and universal wheel for the new version

    .. code-block:: console

        python setup.py sdist
        python setup.py bdist_wheel --universal

10. Install twine (if not already installed) and upload to the new distribution
    files to the PyPi test environment.
    
    .. code-block:: console
        
        pip install twine
        twine upload dist/* -r pypitest

11. Test that the new test distribution installs okay:

    .. code-block:: console

        mktmpenv
        pip install -i https://testpypi.python.org/pypi wagtailmenus
        deactivate

12. If all okay, push distribution files to the live PyPi:

    .. code-block:: console

        twine upload dist/* -r pypi

13. Edit the release notes for the release from
    https://github.com/rkhleics/wagtailmenus/releases, by copying and pasting
    the content from ``docs/releases/x.x.x.rst``

14. Crack open a beer - you earned it!
