FROM python

RUN apt-get update && apt-get install -y \
    net-tools \
    iproute \
    inetutils-ping \
    curl

ADD app.py app.py
RUN chmod +x app.py

ENV SON_EMU_CMD ./app.py

CMD /bin/bash

