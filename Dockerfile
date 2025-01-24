# Utilizar la imagen base oficial de Lambda con Python 3.9 (compatible con AWS Lambda)
FROM public.ecr.aws/lambda/python:3.13

# Establecer el directorio de trabajo
WORKDIR /var/task

# Copiar los requerimientos
COPY ./requirements.txt ./requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# Copiar el código de la aplicación
COPY ./app .

# Especificar el manejador para AWS Lambda
CMD ["main.handler"]
