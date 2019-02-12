FROM vim-emu-test

RUN apt-get update && apt-get install -y git python-pip
RUN pip install flake8

COPY . /tng-sdk-test
WORKDIR /tng-sdk-test
#RUN python setup.py develop
RUN pip install --upgrade .

CMD /bin/bash
