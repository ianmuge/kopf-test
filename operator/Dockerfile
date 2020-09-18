FROM python:3.7
WORKDIR /src
ADD . /src
RUN pip install --no-cache-dir -r requirements.txt
CMD kopf run /src/main.py --verbose