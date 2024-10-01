from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Definir los alcances que permiten acceder a los archivos en Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive():
    """Autenticar usando credenciales de servicio para Google Drive."""
    # Ruta al archivo .json con tus credenciales de servicio
    SERVICE_ACCOUNT_FILE = 'creds_google.json'
    
    # Crear las credenciales a partir del archivo JSON de servicio
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Construir el servicio de Google Drive
    service = build('drive', 'v3', credentials=creds)
    return service

def download_file(service, file_id, file_name):
    """Descargar un archivo de Google Drive dado su ID."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()  # Crear un flujo de bytes para guardar el archivo

    # Descargar el archivo
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Descargando: {int(status.progress() * 100)}%.")

    # Guardar el archivo en el sistema local
    fh.seek(0)  # Regresar al inicio del flujo
    with open(file_name, 'wb') as f:
        f.write(fh.read())
    print(f"Archivo descargado: {file_name}")

def search_file_in_folder(service, folder_id, file_name):
    """Buscar un archivo por nombre en una carpeta específica."""
    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No se encontraron archivos con ese nombre.')
    else:
        for item in items:
            print(f"Archivo encontrado: {item['name']} (ID: {item['id']})")
            # Llamar a la función para descargar el archivo
            download_file(service, item['id'], item['name'])
        return items

if __name__ == '__main__':
    # Autenticar el acceso a Google Drive
    service = authenticate_google_drive()
    
    # ID de la carpeta donde quieres buscar
    folder_id = '1xkAX8shCImzjUsPi_djKEnJu6a_eFnuR'
    
    # Nombre del archivo que estás buscando
    file_name = 'Facundo_Minervini.pdf'
    
    # Buscar el archivo
    search_file_in_folder(service, folder_id, file_name)
