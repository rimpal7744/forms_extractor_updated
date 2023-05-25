FROM python:3.8
WORKDIR /app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && apt-get install -y default-jre
RUN apt-get install poppler-utils -y

COPY requirement.txt requirement.txt
RUN pip install -r requirement.txt

COPY . .
CMD [ "python", "main.py"]
