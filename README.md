# Dependencias
Estos scripts ha sido probados en una computadora usando Ubuntu 13.10 y
necesitan que las siguientes dependencias estén instaladas.

* Python
* pip: ``sudo apt-get install python-pip``
* bs4: ``sudo apt-get install python-bs4``
* requests: ``sudo apt-get install python-requests``
* dataset: ``sudo pip install dataset``
* short_url: ``sudo pip install short_url``
* PyRSS2Gen: ``sudo pip install pyrss2gen``

# Modo de ejecución

## script scrape.py

* El script ``scrape.py`` se encarga de cosechar la información del servidor del
congreso.
* Elabora un HTML con la lista de proyectos ``index.html``,
información básica (título, autores, código) y enlaces al expediente y PDF del
proyecto. 
* Toda la información cosechada se almancena en una base de datos SQLite3. El
  código en javascript se encarga de obtener los datos de esta base de datos
  usando JQuery y AJAX.

## script do_ocr.py
[We don't want OCR yet]

Esto se ha implentado al incio del proyecto pero es posible que no funcione
ya que no se ha actualizado recientemente.
* El script ``do_ocr.py`` se encarga de convertir los PDFs del folder ``pdf/``
  a HTML previo proceso OCR usando ``tesseract``.
* También crea un ATOM Feed ``feed.xml`` conteniendo los proyectos de ley que
  han sido convertidos de PDF a HTML.
* Si un PDF ya ha sido procesado por OCR y convertido a HTML, este script
  evitará volverlo a procesar en futuras corridas.
* Los archivos HTML y el ``feed.xml`` son creados con info contenida en la
  "base de datos" ``proyectos_data.json``.

## plantilla HTML

* El archivo ``base.html`` funciona como plantilla para crear las páginas HTML.
  Cualquier cambio al estilo se debe realizar en este archivo. Esta plantilla
  usa un estilo basado en Twitter Bootstrap con *responsive features* para que
  se vea bien en computadoras y dispositivos móbiles.
* También se puede usar un HTML radicalmente diferente como plantilla. Pero es
  necesario que este archivo se llame ``base.html`` y tenga los siguientes
  campos:

     * ``{% titulo %}``
     * ``{% content %}``

* Esos campos se usan para introducir en contenido en la plantilla y generar
  los archivos HTML.

## Configuración Apache
Hay que asegurarse que se ha copiado el archivo .htaccess y que Apache2 está
configurado con los modulos requeridos, especialmente rewrite.


