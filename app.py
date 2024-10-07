import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import os
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import json

# Carga de credenciales
path_creds = 'creds/creds_google.json'
with open('creds/config.json', 'r') as config_file:
    config = json.load(config_file)
folder_id_hc = config["folder_id_hc"]
folder_id_complete = config["folder_id_complete"]
url_sheets = config["google_sheets_url"]
scope_sheets = config["scopes_sheets"]
scope_drive = config["scopes_drive"]
temp_dir = "temporal"

# Autentificación
creds_sheets = ServiceAccountCredentials.from_json_keyfile_name(path_creds, scope_sheets)
client = gspread.authorize(creds_sheets)
spreadsheet = client.open_by_url(url_sheets)
creds = Credentials.from_service_account_file(path_creds, scopes=scope_drive)
service = build('drive', 'v3', credentials=creds)

# Lectura del sheets
worksheet = spreadsheet.sheet1
data = worksheet.get_all_values()
client_name = data[1][1].replace(' ','').lower()
file_name = f"{client_name}.pdf"
file_name_complete = f"{client_name}_completo.pdf"
output_pdf = output_pdf = os.path.join(temp_dir, file_name_complete)
temp_pdf = os.path.join(temp_dir, 'temp_text.pdf')

# Busqueda
query = f"'{folder_id_hc}' in parents and name = '{file_name}' and trashed = false"
results = service.files().list(q=query, fields="files(id, name)").execute()
items = results.get('files', [])
if not items:
    print('No se encontraron archivos con ese nombre.')
else:
    for item in items:
        print(f"Archivo encontrado: {item['name']} (ID: {item['id']})")

# Download
request = service.files().get_media(fileId=items[0]['id'])
fh = io.BytesIO()  # Crear un flujo de bytes para guardar el archivo
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print(f"Descargando: {int(status.progress() * 100)}%.")
fh.seek(0)  # Regresar al inicio del flujo
local_file_path = os.path.join(temp_dir, items[0]['name'])
with open(local_file_path, 'wb') as f:
    f.write(fh.read())
print(f"Archivo descargado: {items[0]['name']}")

# Completado
c = canvas.Canvas(temp_pdf, pagesize=A4)
nombre_y_apellido = data[1][1]
tipo_y_dni = data[1][2]
fecha_nac = data[1][3]
direccion = data[1][4]
localidad = data[1][5]
provincia = data[1][6]
codigo_postal = data[1][7]
tel_particular = data[1][8]
celular = data[1][9]
email = data[1][10]
obra_social = data[1][11]

c.setFont("Helvetica", 10)
c.drawString(120, 702, nombre_y_apellido)
c.drawString(120, 688, tipo_y_dni)
c.drawString(340, 688, fecha_nac)
c.drawString(120, 676, direccion)
c.drawString(120, 664, localidad)
c.drawString(340, 664, provincia)
c.drawString(465, 664, codigo_postal)
c.drawString(150, 650, tel_particular)
c.drawString(340, 650, celular)
c.drawString(120, 638, email)
c.drawString(120, 624, obra_social)
c.save()

reader = PdfReader(local_file_path)
writer = PdfWriter()
page = reader.pages[0]

text_layer = PdfReader(temp_pdf).pages[0]
merger = PageMerge(page)
merger.add(text_layer).render()
writer.addpage(page)
writer.write(output_pdf)

# Upload
file_metadata = {
    'name': f"{client_name}_completo.pdf",
    'parents': [folder_id_complete] #[folder_id]
}
file_path = output_pdf
media = MediaFileUpload(file_path, mimetype='application/pdf')
file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
print(f"Archivo subido con éxito: {output_pdf} (ID: {file['id']})")