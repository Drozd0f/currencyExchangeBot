FROM python
WORKDIR bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY Bot/ .
