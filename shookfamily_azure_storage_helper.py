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

        if force is not True:
            sys.stdout.write("Download all images from azure storage?  Default n: [y|n] ")
            line_read = sys.stdin.readline()

            # Remove os.linesep
            line_read = line_read.strip()
            if line_read == "" or line_read is None:
                return

            if line_read.lower() != "y":
                return

        items_in_azure_storage = defaultdict(lambda: [])
        items_on_disk = defaultdict(lambda: [])

        async for blob in self.web_container.list_blobs():
            extension = os.path.splitext(blob.name)[1]
            items_in_azure_storage[extension].append(blob)
        
        tracked_extensions = set([".html", ".txt", ".csv", ".css", ".js"])
        # We will quickly verify that all tracked files in azure storage
        # also exist in the enlistment.

        files_on_disk = glob.glob(self.enlistment_path + "/**", recursive=True)

        for item in files_on_disk:
            extension = os.path.splitext(item)[1]
            items_on_disk[extension].append(item)

        def compare_blob_list(blob_list, paths):
            """ Compare a list of azure storage blobs to paths

            """
            azure_storage_file_set = set()
            on_disk_file_set = set()

            for item in blob_list:
                azure_storage_file_set.add(item.name)

            for item in paths:
                on_disk_file_set.add(item.split(self.enlistment_path + os.path.sep)[1])

            # Check that on disk has all files in azure storage
            has_same_contents = True
            differences = [[], []]
            for path in on_disk_file_set:
                if path not in azure_storage_file_set:
                    has_same_contents = False
                    differences[0].append(path)
            
            # Check that azure storage has all on disk changes
            for path in azure_storage_file_set:
                if path not in on_disk_file_set:
                    has_same_contents = False
                    differences[1].append(path)

            return differences

        for extension in items_on_disk:
            if extension in tracked_extensions:
                differences = compare_blob_list(items_in_azure_storage[extension], items_on_disk[extension])
                has_differences = not (len(differences[0]) == 0 and len(differences[1]) == 0)
                has_files_in_azure_storage_not_on_disk = not (len(differences[0]) == 0)

                # The enlistment should always be in sync with azure storage
                # for tracked files.
                assert not has_files_in_azure_storage_not_on_disk

        untracked_files = []
        for extension in items_in_azure_storage:
            if extension not in tracked_extensions:
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

    def divide_into_chunks(self, container, size):
        for index in range(0, len(container), size):
            yield container[index: index + size]