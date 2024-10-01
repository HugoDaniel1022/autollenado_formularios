from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Definir los alcances que permiten acceder a los archivos en Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def authenticate_google_drive():
    """Autenticar usando credenciales de servicio para Google Drive."""
    # Ruta al archivo .json con tus credenciales de servicio
    SERVICE_ACCOUNT_FILE = 'creds_google.json'
    
    # Crear las credenciales a partir del archivo JSON de servicio
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Construir el servicio de Google Drive
    service = build('drive', 'v3', credentials=creds)
    return service

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

