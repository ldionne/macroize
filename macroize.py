#!/usr/bin/env python

import argparse
import os
import re
import string


class Driver(object):
    """Driver of the script. Dispatches the tasks according to the options it
       receives.
    """

    def __init__(self, argv):
        self.args = argparse.ArgumentParser(
            description =
            "Perform various tasks related to heavy preprocessor macro usage."
        )

        self.args.add_argument(
            'file',
            nargs='+',
            help="The input file(s) to process."
        )

        self.args.add_argument(
            '-w', '--width',
            default=80,
            dest='line_width',
            metavar='n',
            type=int,
            help="When backslash escaping macros, this is the preferred line "
                 + "width at which to put backslashes."
        )

        self.args.add_argument(
            '-u', '--unescape',
            action='store_true',
            dest='unescape',
            help="Strip backslashes instead of adding them."
        )

        self.args.add_argument(
            '-c', '--check',
            action='store_true',
            dest='check',
            help="Check specially formatted unit test files for failures."
        )

        self.argv = self.args.parse_args(argv)

    def run(self):
        filenames = self._find_all_files(self.argv.file[1:])
        if self.argv.check:
            if self.argv.unescape:
                raise ValueError("conflicting options --check and --unescape")
            action = Checker()
        else:
            action = Backslasher(self.argv.unescape, self.argv.line_width)

        action(filenames)

    def _find_all_files(self, paths):
        found = [ ]
        for path in paths:
            if not os.path.exists(path):
                raise ValueError("inexistant file/directory: {}".format(path))
            if os.path.isdir(path):
                for root, dirnames, filenames in os.walk(path):
                    fullpath = lambda filename: os.path.join(root, filename)
                    filenames =(f for f in filenames if not f.startswith("."))
                    found.extend((fullpath(fname) for fname in filenames))
            else:
                found.append(path)
        return found


class Backslasher(object):
    """Performs backslash escaping on a list of files."""

    # TODO :
    #   Fix the regular expression : it does not always work for some twisted
    #           uses of the concatening or stringizing operators.

    def __init__(self, unescape, line_width):
        self.action = (self._strip_backslashes if unescape
                                               else self._add_backslashes)
        self.line_width = line_width

    def __call__(self, filenames):
        for filename in filenames:
            replacement = ""
            with open(filename, 'r') as file:
                replacement = self._replace("".join(file), self.action)
            with open(filename, 'w') as file:
                file.write(replacement)

    def _add_backslashes(self, line):
        if line.endswith("\\"):
            return line
        else:
            return line.ljust(self.line_width-2) + " \\"

    def _strip_backslashes(self, line):
        if not line.endswith("\\"):
            return line
        else:
            return line[:-1].rstrip()

    def _replace(self, string, action):
        def replacer(match):
            lines = match.group().splitlines()
            tosub, last = lines[:-1], lines[-1]
            return "\n".join(list(map(action, tosub)) + [last])

        ppdirective = r"define|undef|if|else|endif"
        pattern = re.compile(
            r"^#\s*define\s+(?:[^#]|##|#(?!" + ppdirective + r"))*?/\*\*/",
            re.MULTILINE
        )

        return pattern.sub(replacer, string)


class Checker(object):
    """Performs unit test checking on a list of files."""

    def __call__(self, filenames):
        for filename in filenames:
            with open(filename, 'r') as file:
                failures = self._check(file.read())

            for lineno, line in failures:
                print("{}:{}:{}".format(filename, lineno, line))

    def _check(self, lines):
        """Scans a sequence of lines of the form
           `arbitrary_content==arbitrary_content`
           to detect lines where the left side does not match the right side.

           Only the lines enclosed within "[[[" and "]]]" tags are checked.
           Each tag needs to be on its own line. Leading and trailing
           whitespace is removed before trying to match the tags.

           For lines inside the begin and end tags, leading and trailing
           whitespaces are stripped. If the line is empty after that, checking
           goes on to the next line.

           The following transformations are applied to the lines before
           checking for equality of both sides:
             - All whitespaces are collapsed to only one whitespace.
             - Whitespace around these characters is removed: ",()-+%/=*".

           Returns a list of (line number, line) tuples representing the lines
           where the left side of the `==` did not match the right side.
        """
        failures = [ ]
        enabled = False
        for lineno, line in enumerate(map(string.strip,lines.splitlines()),1):
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
    import sys
    Driver(sys.argv).run()
