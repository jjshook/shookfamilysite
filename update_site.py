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
# Dependencies:
#
# pip3 install azure-storage-blob
# pip3 install azure-storage-file
# pip3 install azure-storage-queue
#
################################################################################
################################################################################

import argparse
import asyncio
import sys

from shookfamily_azure_storage_helper import *

################################################################################
# Argparse
################################################################################

description = """
Small python script to update the azure storage website containing the
shookfamily site. This is expected to be run on the master branch of github
website and will require an azure cli key to run correctly.

Dependencies:

pip3 install azure-storage-blob
pip3 install azure-storage-file
pip3 install azure-storage-queue
"""
parser = argparse.ArgumentParser(description=description)

parser.add_argument("--download_images", default=False, action="store_true")
parser.add_argument("--force", "-f", default=False, action="store_true")

################################################################################
# Main
################################################################################

def main(args):
    """ Main method

    Return:
        return_code (int)
    """
    storage_helper = ShookFamilyAzureStorageHelper()

    if args.download_images:
        task = storage_helper.download_non_tracked_files(args.force)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)

    return 0

################################################################################
# __main__
################################################################################

if __name__ == "__main__":
    args = parser.parse_args()
    sys.exit(main(args))