import pandas as pd
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Leer el archivo CSV
df = pd.read_csv('formu.csv')
fila = df.iloc[-1]

for i in fila:
    print(i)

# Plantilla PDF
template_pdf = 'plantilla.pdf'
output_pdf = 'resultado.pdf'

# Crear un archivo PDF temporal con el texto usando reportlab
temp_pdf = 'temp_text.pdf'

# Crear un canvas para generar el texto
c = canvas.Canvas(temp_pdf, pagesize=A4)
nombre_y_apellido = fila.iloc[1]
tipo_y_dni = fila.iloc[2]
fecha_nac = fila.iloc[3]
direccion = fila.iloc[4]
localidad = fila.iloc[5]
tel_particular = '4444444'
celular = '1555555555'
email = fila.iloc[8]
obra_social = fila.iloc[9]


c.setFont("Helvetica", 10)

# Definir las posiciones donde agregar el texto
c.drawString(120, 702, nombre_y_apellido)
c.drawString(120, 688, tipo_y_dni)
c.drawString(340, 688, fecha_nac)
c.drawString(120, 676, direccion)
c.drawString(120, 664, localidad)
c.drawString(150, 650, tel_particular)
c.drawString(340, 650, celular)
c.drawString(120, 638, email)
c.drawString(120, 624, obra_social)

# Guardar el archivo PDF temporal con el texto
c.save()

# Leer el PDF existente
reader = PdfReader(template_pdf)
writer = PdfWriter()

# Leer la primera página del PDF
page = reader.pages[0]

# Cargar el PDF temporal con el texto
text_layer = PdfReader(temp_pdf).pages[0]

# Fusionar el texto con la plantilla PDF
merger = PageMerge(page)
merger.add(text_layer).render()

# Agregar la página modificada al PDF final
writer.addpage(page)

# Escribir el nuevo PDF con los datos insertados
writer.write(output_pdf)
