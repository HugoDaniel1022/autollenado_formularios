import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 1. Definir el alcance (scope) de la API de Google
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 2. Cargar las credenciales del archivo JSON
creds = ServiceAccountCredentials.from_json_keyfile_name('creds_google.json', scope)

# 3. Autenticación y acceso a Google Sheets
client = gspread.authorize(creds)

# 4. Abrir el Google Sheets por URL
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bxmUtAywGtBaK0qZn6vy1sMLsJ4M_1VVpyMQ-hz4SjE/edit?resourcekey=&gid=440227584#gid=440227584")

# 5. Seleccionar la hoja (Worksheet) que quieres leer
worksheet = spreadsheet.sheet1  # Usa 'sheet1' para la primera hoja o pon el nombre específico de la hoja

# 6. Obtener todos los valores de la hoja
data = worksheet.get_all_values()

# 7. Convertir los datos en un DataFrame de pandas
df = pd.DataFrame(data[1:], columns=data[0])  # Usa la primera fila como encabezados

# 8. Mostrar los primeros registros del DataFrame
print(df.head())

for i in df.columns:
    print(i)