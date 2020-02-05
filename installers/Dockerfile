# Dockerfile used to test the installer in a clean environment.
# TODO: Write actual tests to run inside the container.

FROM mcr.microsoft.com/windows/servercore:ltsc2019

ARG SETUP_EXE

COPY $SETUP_EXE pythonup-setup.exe
RUN pythonup-setup.exe /S

RUN pythonup install 3.6
RUN python3.6 --version

RUN pip3.6 install python-dotenv
RUN where dotenv

RUN pythonup list
RUN pythonup list --all

RUN python3 --version

RUN pip3 install pytest
RUN where pytest

RUN pythonup use 3.6
RUN pythonup use --reset
RUN pythonup list --all

RUN pythonup uninstall 3.6
