FROM python:3-alpine

# musl-dev provides libc, alpine-sdk provides make
RUN apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev alpine-sdk
RUN pip install -r requirements.txt
RUN apk del .build-deps

COPY . /app
WORKDIR /app

#EXPOSE 8006
#CMD ["python", "json_head.py"]