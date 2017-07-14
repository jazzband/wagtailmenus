## Updating translations (via Transifex)


### Pushing updated source files to Transifex

This should really be done from the master branch whenever code changes are
made/merged, as we want the source files to pick up any new strings, and
ensure line references for existing strings are up-to-date. 

From the project's root directory, run the following:

```
django-admin.py makemessages -l en
tx push -s -l en
```


### Pulling translations from Transifex

1. If you haven't pushed the source files to Transifex since changes code changes
were last made, do the above first!

2. Ensure all outstanding changes are committed / pushed / stashed

3. From the project's root directory, run the following:

```
# Pull complete translations only
tx pull --minimum-perc=100

# Remove the en_GB locale ('en' is the source language now, and is exactly the same, so let's not confuse things)
rm -r wagtailmenus/locale/en_GB/

# Add any .po files for new locales provided by Transifex
git add *.po

# Commit changes
git commit -am 'Pulled complete translations from Transifex'
```


### Compile .po to .mo before submitting a new release

From the project's root directory, for each supported language, do the following:

```
msgfmt --check-format -o wagtailmenus/locale/{{ lang }}/LC_MESSAGES/django.mo wagtailmenus/locale/{{ lang }}/LC_MESSAGES/django.po
```

