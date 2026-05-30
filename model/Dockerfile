#Cada uno de los from genera diferentes bloques para "la ejecucion", se puede controlar hasta que bloque correr
FROM python:3.8.13 as base


# Append /home/app/.local/bin/ to PATH variable because
# gunicorn is installed there.
ENV PYTHONPATH=$PYTHONPATH:/src/

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/src/

COPY ./ /src/

WORKDIR /src

FROM base as test
RUN ["pytest", "-v", "/src/tests"]

FROM base as build
ENTRYPOINT ["python3", "/src/ml_service.py"]

#Cuando se corre el comando docker build -t model_test --progress=plain --target test . se esta evaluando todo el codigo, pero por capas (entiendase una capa como un contenedor temporal interno), lo que nos permite evaluar el codigo. Si usamos docker build -t model_test --progress=plain . en este caso no se crea la imagen porque la ejecucion se esta deteniendo en el target.
#Estamos diciendo que no se haga visual la ejecucion del test, sin embargo si se la esta realizando por que está antes del build final, por lo que si falla el test, falla la creacion de la imagen.