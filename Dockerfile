# Utilizar la imagen base oficial de Lambda con Python 3.13
FROM public.ecr.aws/lambda/python:3.13

# Establecer el directorio de trabajo
WORKDIR /var/task

# Copiar los requerimientos
COPY ./requirements.txt ./requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# Copiar el código de la aplicación
COPY ./app .

# Cambiar CMD a ENTRYPOINT para que admita comandos dinámicos
ENTRYPOINT ["python3", "-m", "awslambdaric"]
CMD ["main.handler"]
