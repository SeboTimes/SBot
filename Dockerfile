FROM python:3.12.7

WORKDIR /src

RUN apt install -y ffmpeg

RUN git clone https://github.com/SeboTimes/SBot.git .

RUN echo "#!/bin/sh" > start
RUN echo "git pull https://github.com/SeboTimes/SBot.git" >> start
RUN echo "pip install -r requirements.txt" >> start
RUN echo "python3 src/Main.py" >> start

RUN chmod +x start

CMD [ "./start" ]

