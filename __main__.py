
"""
Entry point for the browsers command line interface.
"""
from .browsers import cmdline

if __name__ == "__main__":
    import sys
    sys.exit(cmdline(sys.argv[1:]))
