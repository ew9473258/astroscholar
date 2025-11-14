FROM python:3.13
WORKDIR /AstroScholar
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
