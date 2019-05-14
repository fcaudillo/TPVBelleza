FROM sabbir1cse/ubuntu-python-pip-supervisor 
RUN apt-get -y update; \
    apt-get -y upgrade;
	
WORKDIR tlapape


COPY ./requirements.txt .

RUN pip install -r requirements.txt
COPY ./consultaprecio .

RUN chmod +x ./manage.py
RUN rm -f /etc/localtime
RUN ln  -s  /usr/share/zoneinfo/America/Mexico_City /etc/localtime
EXPOSE 9000

CMD ["./manage.py", "runserver", "0.0.0.0:9000"]




