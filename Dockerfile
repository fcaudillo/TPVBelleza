FROM sabbir1cse/ubuntu-python-pip-supervisor 
RUN apt-get -y update; \
    apt-get -y upgrade;
	
WORKDIR tlapape


COPY ./requirements.txt .

RUN pip install -r requirements.txt
COPY ./consultaprecio .

ARG BUILD_USU_MQ
ARG BUILD_PASS_MQ
ARG BUILD_CLIENTE_ID
ARG BUILD_USU_DB
ARG BUILD_PASS_DB

ENV USUARIO_MQ=$BUILD_USU_MQ
ENV PASSWORD_MQ=$BUILD_PASS_MQ
ENV CLIENTE_ID=$BUILD_CLIENTE_ID
ENV USUARIO_DB=$BUILD_USU_DB
ENV PASSWORD_DB=$BUILD_PASS_DB

RUN chmod +x ./manage.py
RUN rm -f /etc/localtime
RUN ln  -s  /usr/share/zoneinfo/America/Mexico_City /etc/localtime
EXPOSE 9000

#RUN ./manage.py migrate

CMD ["./manage.py", "runserver", "0.0.0.0:9000"]




