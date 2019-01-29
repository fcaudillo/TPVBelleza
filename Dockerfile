FROM sabbir1cse/ubuntu-python-pip-supervisor 
#RUN apt-get -y update; \
#    apt-get -y upgrade;
	
WORKDIR tlapape

COPY ./consultaprecio .
COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN chmod +x ./manage.py

EXPOSE 9000

CMD ["./manage.py", "runserver", "0.0.0.0:9000"]




