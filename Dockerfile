FROM python:3.12
EXPOSE 80
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["/bin/bash","docker-entrypoint.sh"]