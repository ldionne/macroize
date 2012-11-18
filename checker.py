#/usr/bin/env python

import re
import string


def check(lines):
    """Scans a sequence of lines of the form
       `arbitrary_content==arbitrary_content`
       to detect lines where the left side does not match the right side.

       Only the lines enclosed within "[[[" and "]]]" tags are checked. Each
       tag needs to be on its own line. Leading and trailing whitespace is
       removed before trying to match the begin and end tags.

       For lines inside the begin and end tags, leading and trailing
       whitespaces are stripped. If the line is empty after that, checking
       goes on to the next line.

       The following transformations are applied to the lines before checking
       for equality of both sides:
         - All whitespaces are collapsed to only one whitespace.
         - Whitespace around these characters is removed: ",()-+%/=*".

       Returns a list of (line number, line) tuples representing the lines
       where the left side of the `==` did not match the right side.
    """

    failures = [ ]
    enabled = False
    for lineno, line in enumerate(map(string.strip, lines.splitlines()), 1):
        if not line:
            continue
        elif line == "[[[":
            enabled = True
        elif line == "]]]":
            enabled = False
        elif enabled:
            # 1st transformation
            line = re.sub(r"(.)\s+", r"\1 ", line)
            # 2nd transformation
            line = re.sub(r"\s*([,()\-+%/=*])\s*", r"\1", line)
            # try to match both sides of the equality
            match = re.match(r"^(?P<lhs>.*?)==(?P=lhs)$", line)
            if match is None:
                failures.append((lineno, line))
        else:
            pass # We are outside the blocks, just skip the lines.

    return failures


if __name__ == "__main__":
    pass
