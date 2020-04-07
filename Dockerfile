# Build stage:
FROM python:3.7-alpine as build
COPY . /app
WORKDIR /app

RUN apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add postgresql-dev 

RUN pip install -r requirements.txt



# "Default" stage:
FROM python:3.7-alpine
LABEL maintainer="WiNe" \
      description="Flask app linking grafana to user devices"

# Copy generated site-packages from former stage:
COPY --from=build /usr/local/lib/python3.7/site-packages/ /usr/local/lib/python3.7/site-packages/
COPY . /app

RUN apk add libpq

WORKDIR /app

ENTRYPOINT ["python"]
CMD ["app.py"]
