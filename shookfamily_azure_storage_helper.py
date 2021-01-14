#!/usr/bin/env python
################################################################################
################################################################################
#
# Module:  shookfamily_azure_storage_helper.py
#
################################################################################
################################################################################

import asyncio
import glob
import os
import sys

from collections import defaultdict

import tqdm

from azure.storage.blob.aio import BlobServiceClient

################################################################################
# Helper classes
################################################################################

class Diff:
    """ Abstract a set of differences
    """
    def __init__(self, extra_validation_first=None, extra_validation_second=None):
        self.first_lookup_list = defaultdict(lambda: None)
        self.second_lookup_list = defaultdict(lambda: None)

        self.first = set()
        self.second = set()

        # List of items that exist in self.first and not in self.second
        self.first_differences = []

        # List of items that exist in self.second and not in self.first
        self.second_differences = []

        # Overlapping items
        self.overlap = []
        self.extra_validation_first = extra_validation_first
        self.extra_validation_second = extra_validation_second

        self.has_differences = False

    ############################################################################
    # Member Methods
    ############################################################################

    def add_to_first(self, item_name, item):
        self.add(self.first, self.first_lookup_list, item_name, item)

    def add_to_second(self, item_name, item):
        self.add(self.second, self.second_lookup_list, item_name, item)

    def check(self):
        self.check_differences(self.first, self.second, self.first_lookup_list, self.first_differences, self.extra_validation_first)
        self.check_differences(self.second, self.first, self.second_lookup_list, self.second_differences, self.extra_validation_second)

    ############################################################################
    # Helper Methods
    ############################################################################

    def add(self, set_to_add, lookup_list, item_name, item):
        set_to_add.add(item_name)

        lookup_list[item_name] = item

    def check_differences(self, set_to_check, set_to_diff, lookup_list, differences, extra_validation):
        for item in set_to_check:
            has_difference = False

            if item not in set_to_diff:
                self.has_differences = True
                has_difference = True
            elif extra_validation is not None:
                if not extra_validation(lookup_list[item]):
                    has_difference = True

            if has_difference:
                differences.append(item)
            else:
                self.overlap.append(item)

################################################################################
################################################################################

class ShookFamilyAzureStorageHelper:
    
    ############################################################################
    # Ctor
    ############################################################################
    def __init__(self):
        secret_name = "connection_string"
        if secret_name not in os.environ:
            raise RuntimeError(f"Secret: {secret_name} required in environment.")

        self.connection_string = os.environ[secret_name]

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        self.web_container = self.blob_service_client.get_container_client("$web")
        assert self.web_container is not None

        self.tracked_extensions = set([".html", ".txt", ".csv", ".css", ".js", ".py", ".pyc", ".yml"])
        self.enlistment_path = os.path.realpath(os.path.dirname(__file__))

    ############################################################################
    # Member Methods
    ############################################################################
    
    async def download_non_tracked_files(self, force=False):
        """ Download all images from azure storage.

        Notes:
        
        This is a lossy operation. It will overwrite all of the images current in
        the enlistment. This method will prompt to make sure the user is ok with
        this.
        """

        self.prompt(force)
        items_in_azure_storage, items_on_disk, differences = await self.get_files()

        untracked_files = []
        for extension in items_in_azure_storage:
            if extension not in self.tracked_extensions:
                for blob in items_in_azure_storage[extension]:
                    untracked_files.append(blob)

        # Start the download of all these blobs
        tasks = []
        for blob in untracked_files:
            tasks.append(self.download_blob(blob, log=False))

        # Create the progress bar
        progress_bar = tqdm.tqdm(total=len(untracked_files))
        for task in asyncio.as_completed(tasks):
            await task
            progress_bar.update()

        # at this point we have downloaded all files
        pass

    async def upload_non_tracked_files(self, force=False):
        """ Upload all untracked files to azure storage in the enlistment

        Notes:
        
        This is a lossy operation. It will overwrite all of the images current in
        azure storage. This method will prompt to make sure the user is ok with
        this.
        """

        self.prompt(force)
        items_in_azure_storage, items_on_disk, differences = self.get_files()

        untracked_files = []
        for extension in items_in_azure_storage:
            if extension not in self.tracked_extensions:
                for blob in items_in_azure_storage[extension]:
                    untracked_files.append(blob)

        # Start the download of all these blobs
        tasks = []
        for blob in untracked_files:
            tasks.append(self.download_blob(blob, log=False))

        # Create the progress bar
        progress_bar = tqdm.tqdm(total=len(untracked_files))
        for task in asyncio.as_completed(tasks):
            await task
            progress_bar.update()

        # at this point we have downloaded all files
        pass


    ############################################################################
    # Helper Methods
    ############################################################################

    async def download_blob(self, blob, log=True):
        path_on_disk = os.path.join(self.enlistment_path, blob.name)

        with open(path_on_disk, 'wb') as file_handle:
            blob_client = self.web_container.get_blob_client(blob.name)

            retry_count = 5
            success = False

            while success is False and retry_count > 0:
                try:
                    stream = await blob_client.download_blob()
                    data = await stream.readall()
                    file_handle.write(data)
                    success = True
                except Exception as exception:
                    retry_count -= 1

            if not success:
                print(f"Failed to download {path_on_disk}")
            elif log:
                print(f"Downloaded: {path_on_disk}")

    async def get_files(self):
        items_in_azure_storage = defaultdict(lambda: [])
        items_on_disk = defaultdict(lambda: [])

        async for blob in self.web_container.list_blobs():
            extension = os.path.splitext(blob.name)[1]
            items_in_azure_storage[extension].append(blob)
        
        # We will quickly verify that all tracked files in azure storage
        # also exist in the enlistment.

        files_on_disk = glob.glob(self.enlistment_path + "/**", recursive=True)

        for item in files_on_disk:
            extension = os.path.splitext(item)[1]
            items_on_disk[extension].append(item)

        def compare_blob_list(differences, blob_list, paths):
            """ Compare a list of azure storage blobs to paths

            """
            for item in blob_list:
                differences.add_to_first(item.name, item)

            for item in paths:
                differences.add_to_second(item.split(self.enlistment_path + os.path.sep)[1], item)

            differences.check()
            return differences

        def check_item_size(item):
            assert not isinstance(item, type(str))
            size_on_disk = os.path.getsize(os.path.join(self.enlistment_path, item["name"]))
            azure_storage_size = item["size"]

            if size_on_disk != azure_storage_size:
                return False

            return True

        differences = Diff(extra_validation_first=check_item_size)

        for extension in items_on_disk:
            if extension not in self.tracked_extensions and extension != "":
                differences = compare_blob_list(differences, items_in_azure_storage[extension], items_on_disk[extension])
                has_differences = differences.has_differences
                has_files_in_azure_storage_not_on_disk = not (len(differences.first_differences) == 0)

                # The enlistment should always be in sync with azure storage
                # for tracked files.
                assert not has_files_in_azure_storage_not_on_disk

        return items_in_azure_storage, items_on_disk, differences

    def prompt(self, force):
        if force is not True:
            sys.stdout.write("Download all images from azure storage?  Default n: [y|n] ")
            line_read = sys.stdin.readline()

            # Remove os.linesep
            line_read = line_read.strip()
            if line_read == "" or line_read is None:
                return

            if line_read.lower() != "y":
                return

    async def upload_blob(self, blob, log=True):
        path_on_disk = os.path.join(self.enlistment_path, blob.name)

        with open(path_on_disk, 'rb') as file_handle:
            blob_client = self.web_container.get_blob_client(blob.name)

            retry_count = 5
            success = False

            while success is False and retry_count > 0:
                try:
                    await blob_client.upload_blob(file_handle, type="BlockBlob")
                except Exception as exception:
                    retry_count -= 1

            if not success:
                print(f"Failed to upload {path_on_disk}")
            elif log:
                print(f"Upload: {path_on_disk}")