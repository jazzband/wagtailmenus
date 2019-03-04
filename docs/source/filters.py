import os
from enchant.tokenize import Filter


class ContributorNamesFilter(Filter):
    """If a word is in the project's CONTRIBUTORS.md file, ignore it."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contributor_name_words = []
        filename = os.path.join(os.path.dirname(__file__), '../../CONTRIBUTORS.md')
        with open(filename) as f:
            for line in f.readlines():
                if line[0] == '*':
                    self.contributor_name_words.extend(
                        word.strip('( )') for word
                        in line.strip('*').split()
                    )

    def _skip(self, word):
        return word in self.contributor_name_words


class MentionsFilter(Filter):
    """If a word looks like a mention (e.g. @username), ignore it."""

    def _skip(self, word):
        return word[0] == '@'
