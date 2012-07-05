#!/usr/bin/env python3

import re
import argparse
import os

# TODO :
#   Fix the regular expression : it does not always work for some twisted
#           uses of the concatening or stringizing operators.

class Macroizer(object):
    def __init__(self):
        self.args = argparse.ArgumentParser(
            description = "Backslash continue long macros marked as specially."
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
            help="The preferred line width at which to put backslashes."
        )

        self.args.add_argument(
            '-u', '--undo',
            action='store_true',
            dest='undo',
            help="Strip backslashes instead of adding them."
        )

    def find_all_files(self, paths):
        found = list()
        for path in paths:
            if not os.path.exists(path):
                raise ValueError("inexistant file/directory: {}".format(path))
            if os.path.isdir(path):
                for root, dirnames, filenames in os.walk(path):
                    filenames = filter(lambda f: not f.startswith("."),
                                                                    filenames)
                    fullpath = lambda name: os.path.join(root, name)
                    found.extend(map(fullpath, filenames))
            else:
                found.append(path)
        return found

    def macroize(self, argv):
        self.argv = self.args.parse_args(argv)
        action = (self.strip_backslashes if self.argv.undo
                                        else self.add_backslashes)

        arg_filenames = self.argv.file[1:]
        for filename in self.find_all_files(arg_filenames):
            replacement = ""
            with open(filename, 'r') as file:
                replacement = self.replace("".join(file), action)
            with open(filename, 'w') as file:
                file.write(replacement)
        del self.argv

    def add_backslashes(self, line):
        if line.endswith("\\"):
            return line
        else:
            return line.ljust(self.argv.line_width-2) + " \\"

    def strip_backslashes(self, line):
        if not line.endswith("\\"):
            return line
        else:
            return line[:-1].rstrip()

    def replace(self, string, action):
        def replacer(match):
            *tosub, last = match.group().splitlines()
            return "\n".join(list(map(action, tosub)) + [last])

        ppdirective = r"define|undef|if|else|endif"
        pattern = re.compile(
            r"^#\s*define\s+(?:[^#]|##|#(?!" + ppdirective + r"))*?/\*\*/",
            re.MULTILINE
        )

        return pattern.sub(replacer, string)


if __name__ == "__main__":
    import sys
    Macroizer().macroize(sys.argv)
