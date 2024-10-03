FROM python

WORKDIR /app/free_games_email

COPY . .

RUN apt-get update\
    && apt-get install -y cron\
    && pip install -r requirements.txt\
    && chmod +x setup.sh\
    && sed -i 's/\r$//' /app/free_games_email/setup.sh

COPY crontab /etc/cron.d/crontab

RUN chmod 777 /etc/cron.d/crontab
RUN echo "" >> /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab
RUN service cron start

CMD ["sh", "-c", "service cron start && sh /app/free_games_email/setup.sh"]

ENV PYTHONPATH=/app
ENV DATABASE_URL="postgresql://user:qwe123@db:5432/free_games"
ENV ZLABS_TOKEN=
ENV YOUR_EMAIL=
ENV APP_PASSWORD=

