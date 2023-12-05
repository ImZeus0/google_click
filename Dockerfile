FROM --platform=linux/amd64 python:3.10
LABEL service=proxy_service
RUN apt-get update -y
RUN apt-get upgrade -y
WORKDIR /app
COPY ./ /app
RUN pip3 install -r req.txt
CMD ["python3","main.py"]