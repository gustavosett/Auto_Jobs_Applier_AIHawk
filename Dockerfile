FROM python:3.11-bullseye

# install dependencies
RUN apt-get update -y && apt-get install -y wget xvfb unzip jq

# install Google Chrome dependencies
RUN apt-get install -y libxss1 libappindicator1 libgconf-2-4 \
    fonts-liberation libasound2 libnspr4 libnss3 libx11-xcb1 libxtst6 lsb-release xdg-utils \
    libgbm1 libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcb-dri3-0

# define the version and URL for the specific version of Chrome
ARG CHROME_VERSION=115.0.5790.170
ARG CHROME_URL=https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip
ARG CHROMEDRIVER_URL=https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip

# easy check if the url exists:
RUN wget --spider $CHROME_URL
RUN wget --spider $CHROMEDRIVER_URL

# download and install chrome
RUN wget -q --continue -O /tmp/chrome-linux64.zip $CHROME_URL && \
    unzip /tmp/chrome-linux64.zip -d /opt/chrome && \
    chmod +x /opt/chrome/chrome-linux64/chrome


# download and install chromedriver
RUN wget -q --continue -O /tmp/chromedriver-linux64.zip $CHROMEDRIVER_URL && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/chromedriver && \
    chmod +x /opt/chromedriver/chromedriver-linux64/chromedriver

# set up chromedriver environment variables
ENV CHROMEDRIVER_DIR /opt/chromedriver
ENV PATH $CHROMEDRIVER_DIR:$PATH
ENV CHROME_PATH /opt/chrome/chrome-linux64/chrome

# clean upa
RUN rm /tmp/chrome-linux64.zip /tmp/chromedriver-linux64.zip

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DISPLAY=:99
ENV LINKEDIN_EMAIL=${LINKEDIN_EMAIL}
ENV LINKEDIN_PASSWORD=${LINKEDIN_PASSWORD}
ENV STYLE_CHOICE=${STYLE_CHOICE}
ENV SEC_CH_UA=${SEC_CH_UA}
ENV SEC_CH_UA_PLATFORM=${SEC_CH_UA_PLATFORM}
ENV USER_AGENT=${USER_AGENT}
ENV WEBHOOK_URI=${WEBHOOK_URI}
ENV WEBHOOK_TOKEN=${WEBHOOK_TOKEN}
ENV BOT_ID=${BOT_ID}
ENV API_PORT=${API_PORT}
ENV GOTENBERG_URL=${GOTENBERG_URL}

EXPOSE ${API_PORT}

# create a directory for the app
WORKDIR /app

# copy the requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy the application files
COPY app_config.py /app/
COPY main.py /app/
COPY src/ /app/src/
COPY assets/ /app/assets/
COPY data_folder/ /app/data_folder/

# ensure permissions are correct
RUN chmod +x /app/main.py

# define the command to run your application
CMD ["python", "./main.py"]