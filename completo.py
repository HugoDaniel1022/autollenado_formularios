import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

# Definir los alcances para Google Sheets y Google Drive
SCOPES_SHEETS = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive']

# Autenticar y acceder a Google Sheets
def authenticate_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds_google.json', SCOPES_SHEETS)
    client = gspread.authorize(creds)
    return client

# Autenticar y acceder a Google Drive
def authenticate_google_drive():
    creds = Credentials.from_service_account_file('creds_google.json', scopes=SCOPES_DRIVE)
    service = build('drive', 'v3', credentials=creds)
    return service

# Leer los datos del Google Sheets
def leer_datos_sheets():
    client = authenticate_google_sheets()
    spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bxmUtAywGtBaK0qZn6vy1sMLsJ4M_1VVpyMQ-hz4SjE/edit")
    worksheet = spreadsheet.sheet1  # Puedes cambiar a una hoja específica si lo deseas
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])  # Usar la primera fila como encabezados
    return df

# Buscar archivo PDF en una carpeta de Google Drive
def search_file_in_folder(service, folder_id, file_name):
    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No se encontraron archivos con ese nombre.')
        return None
    else:
        for item in items:
            print(f"Archivo encontrado: {item['name']} (ID: {item['id']})")
        return items[0]  # Devuelve el primer archivo encontrado

# Descargar archivo PDF desde Google Drive
def download_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    file_io = io.BytesIO()
    downloader = MediaIoBaseDownload(file_io, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f'Descargando {int(status.progress() * 100)}%.')

    file_io.seek(0)  # Rewind the BytesIO object for reading
    return file_io

# Crear el nuevo PDF con los datos del formulario
def crear_pdf_con_datos(fila, output_pdf, template_pdf_io):
    # Crear un archivo PDF temporal con el texto usando reportlab
    temp_pdf = 'temp_text.pdf'
    
    # Crear un canvas para generar el texto
    c = canvas.Canvas(temp_pdf, pagesize=A4)
    
    # Extraer los datos del DataFrame
    nombre_y_apellido = fila['Nombre y Apellido']
    tipo_y_dni = fila['DNI']
    fecha_nac = fila['Fecha de Nacimiento']
    direccion = fila['Dirección']
    localidad = fila['Localidad']
    tel_particular = fila['Teléfono Particular']
    celular = fila['Celular']
    email = fila['Email']
    obra_social = fila['Obra Social']

    c.setFont("Helvetica", 10)
    
    # Definir las posiciones donde agregar el texto en el PDF
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

    # Leer el PDF existente desde el BytesIO
    reader = PdfReader(template_pdf_io)
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

# Subir el archivo a una carpeta en Google Drive
def upload_pdf_to_drive(service, file_path, folder_id, file_name):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/pdf')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Archivo subido con éxito: {file_name} (ID: {file['id']})")

if __name__ == '__main__':
    # Leer los datos del Google Sheets
    df = leer_datos_sheets()
    
    # Leer la última fila del Google Sheets
    fila = df.iloc[-1]

    # Autenticar el acceso a Google Drive
    service_drive = authenticate_google_drive()
    
    # Nombre del archivo PDF basado en el nombre del formulario
    nombre_pdf = f"{fila['Nombre y Apellido']}.pdf"
    
    # Buscar si el archivo ya existe en la carpeta
    folder_id = '1xkAX8shCImzjUsPi_djKEnJu6a_eFnuR'  # Reemplaza con tu ID de carpeta
    archivo_encontrado = search_file_in_folder(service_drive, folder_id, nombre_pdf)

    if archivo_encontrado:
        file_id = archivo_encontrado['id']
        # Descargar el archivo PDF
        template_pdf_io = download_file(service_drive, file_id)
        
        # Crear un nuevo PDF con los datos del formulario
        output_pdf = f"./{nombre_pdf}"
        crear_pdf_con_datos(fila, output_pdf, template_pdf_io)
        
        # Subir el nuevo PDF a otra carpeta en Google Drive
        folder_id_upload = '1aVKSR_KWwjeoO2dYCTUo7fWU4hct7gjP'  # Reemplaza con el ID de la carpeta de destino
        upload_pdf_to_drive(service_drive, output_pdf, folder_id_upload, nombre_pdf)
    else:
        print(f"El archivo {nombre_pdf} no existe en la carpeta.")
