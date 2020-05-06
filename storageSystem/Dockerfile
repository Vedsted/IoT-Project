FROM python:3
ADD dataStoragesystem.py /main.py

RUN pip install mysql-connector-python
RUN pip install paho-mqtt

CMD [ "python", "/main.py" ]