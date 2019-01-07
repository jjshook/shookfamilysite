#!/usr/bin/env python
################################################################################
################################################################################
#
# Module: update_site.py
#
# Notes:
#
# Small python script to update the azure storage website containing the
# shookfamily site. This is expected to be run on the master branch of github
# website and will require an azure cli key to run correctly.
#
################################################################################
################################################################################

import sys

################################################################################
################################################################################

def main():
    """ Main method

    Return:
        return_code (int)
    """

    print("Hello World.")
    print("Check ci.")

    return 0

################################################################################
# __main__
################################################################################

if __name__ == "__main__":
    sys.exit(main())