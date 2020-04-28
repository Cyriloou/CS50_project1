FROM python:3

LABEL Author="Cyril Lacheretz"
LABEL E-mail="cyril.lacheretz@gmail.com"
LABEL version="0.0.1b"

ARG REBUILD_BDD

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP "application.py"
ENV FLASK_DEBUG 1
ENV DATABASE_URL "postgres://kipbzvhituzrbz:3761da06eeb48607c765c404f19c5b26461d7b3f4e2ee3284f9f1aa7a59fb3ba@ec2-54-228-251-117.eu-west-1.compute.amazonaws.com:5432/d7fecdf224srvm"
ENV GOODREADS_API_KEY="ZupLTENpaYDXX7Fz8dkCQ"

RUN pip install werkzeug==0.16.0
RUN pip install requests

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN if [ $REBUILD_BDD = "true" ] ; then python ./create.py && python ./import.py ; else echo "keep the bdd" ; fi
# if [ "$argname" = "false" ] ; then echo 'false'; else echo 'true'; fi

EXPOSE 5000

CMD flask run --host=0.0.0.0

# ENTRYPOINT ["python"]
# CMD ["application.py"]