from exceptions import BadIdentifier
import itertools


class IdentifierMatcher(object):
    """
       iOS apps use different kinds of identifiers (bundle ids, application ids, etc) usually in the form
       of TEAMID.tld.domain.myapp.myotherthing and sometimes with wildcards at the end like TEAMID.* .

       It is sometimes important to know if one id encompasses another. For instance, if you have a provisioning
       profile whose "application-identifier" covers TEAMID.foo.bar.*, and you have a bundle whose CFBundleIdentifier
       is TEAMID.foo.bar.baz. Is that provisioning profile good? In this case yes.

       This class also helps us decide which of many options is the most specific fit

       Because id is so overloaded here, the id we are trying to "fit" into is called the pattern, even if it's just
       another id.
    """
    @classmethod
    def get_best_pattern(cls, identifier, patterns):
        """ Return the best pattern that matched this identifier. May return None """
        best_pattern = None
        patterns_scored = [(pattern, cls.get_score(identifier, pattern)) for pattern in patterns]
        patterns_matching = filter(lambda tup: tup[1] > 0, patterns_scored)
        if len(patterns_matching) > 0:
            (best_pattern, _) = sorted(patterns_matching, key=lambda tup: tup[1])[-1]
        return best_pattern

    @classmethod
    def get_score(cls, identifier, pattern):
        """ Given an identifier like
                TEAMID.tld.domain.myapp

            and a pattern which is either a wildcard or fully-qualified, like:
                TEAMID.*
                TEAMID.tld.domain.myapp
                TEAMID.tld.domain.myapp.*
                TEAMID.tld.domain.myapp.mywatchkitapp

            return an natural number score of how well the pattern matches the id.
            0 means no match at all
        """
        if identifier is None or identifier is '':
            raise BadIdentifier("id doesn't look right: {}".format(identifier))
        if pattern is None or pattern is '':
            raise BadIdentifier("pattern doesn't look right: {}".format(pattern))

        identifier_parts = identifier.split('.')
        pattern_parts = pattern.split('.')
        try:
            star_index = pattern_parts.index('*')
            if star_index != -1 and star_index != len(pattern_parts) - 1:
                raise BadIdentifier("pattern has a non-terminal asterisk: {}".format(pattern))
        except ValueError:
            pass

        # to be a match, there must be equal or fewer pattern parts. Neither 'foo.bar' nor 'foo.*' can match 'foo'
        score = 0
        for identifier_part, pattern_part in itertools.izip_longest(identifier_parts, pattern_parts):
            if identifier_part is None or pattern_part is None:
                score = 0
                break

            if pattern_part == '*':
                break

            if identifier_part != pattern_part:
                score = 0
                break

            score = score + 1

        return score