FROM python:3-slim
WORKDIR /usr/src/app
COPY  requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./send_sms_forum.py ./
COPY ./amqp_setup.py ./
CMD [ "python", "./send_sms_forum.py" ]