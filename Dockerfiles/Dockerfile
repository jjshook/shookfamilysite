from ubuntu:20.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3 python3-pip -y

RUN pip3 install azure-storage-blob
RUN pip3 install azure-storage-file
RUN pip3 install azure-storage-queue
RUN pip3 install aiohttp

RUN apt-get clean