FROM python:3.9-slim-buster
WORKDIR /cloudApp
ADD . /cloudApp
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "start.py" ]