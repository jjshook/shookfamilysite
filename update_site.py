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
pip3 install aiohttp
"""
parser = argparse.ArgumentParser(description=description)

parser.add_argument("--download_images", default=False, action="store_true")
parser.add_argument("--upload_images", default=False, action="store_true")
parser.add_argument("--upload", default=False, action="store_true")
parser.add_argument("--reset-content-type", default=False, action="store_true")
parser.add_argument("--force", "-f", default=False, action="store_true")

################################################################################
# Main
################################################################################

async def main(args):
    """ Main method

    Return:
        return_code (int)
    """
    storage_helper = ShookFamilyAzureStorageHelper()

    if args.download_images:
        await storage_helper.download_non_tracked_files(args.force)

    elif args.upload_images:
        await storage_helper.upload_non_tracked_files(args.force)
    
    elif args.upload:
        await storage_helper.upload_non_tracked_files(force=args.force)
        await storage_helper.upload_tracked_files(force=args.force)
    
    elif args.reset_content_type:
        await storage_helper.reset_content_type(force=args.force)

################################################################################
# __main__
################################################################################

if __name__ == "__main__":
    args = parser.parse_args()

    task = main(args)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)