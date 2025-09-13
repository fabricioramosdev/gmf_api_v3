import os
import hashlib
import time
import dropbox
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(override=True)


DROPBOX_REFRESH_TOKEN = os.environ.get('DROPBOX_REFRESH_TOKEN')
DROPBOX_CLIENT_ID = os.environ.get('DROPBOX_CLIENT_ID')
DROPBOX_CLIENT_SECRET = os.environ.get('DROPBOX_CLIENT_SECRET')


def generate_timestamp_hash():
    """Gera um hash único baseado no timestamp."""
    timestamp = str(int(time.time() * 1000))
    hash_object = hashlib.sha256(timestamp.encode())
    return hash_object.hexdigest()[:16]  # Usa apenas os primeiros 16 caracteres


def get_dropbox_access_token():
    """Obtém um novo access token usando o refresh token."""
    if not all([DROPBOX_REFRESH_TOKEN, DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET]):
        raise Exception("Variáveis de ambiente para token do Dropbox não estão configuradas corretamente.")

    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN,
            "client_id": DROPBOX_CLIENT_ID,
            "client_secret": DROPBOX_CLIENT_SECRET
        }
    )

    if response.status_code == 200:
        
        token_data = response.json()
        return token_data["access_token"]
    else:
        raise Exception(f"Erro ao obter access token: {response.text}")


def init_client_dbp():
    # Inicializar cliente Dropbox
   return dropbox.Dropbox(get_dropbox_access_token())


def get_shared_link(file_path):
    """Obtém ou cria um link compartilhável para um arquivo."""
    dbx = init_client_dbp()
    try:
        link_metadata = dbx.sharing_create_shared_link_with_settings(file_path)
        shared_url = link_metadata.url
    except dropbox.exceptions.ApiError as e:
        if isinstance(e.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and e.error.is_shared_link_already_exists():
            existing_links = dbx.sharing_list_shared_links(file_path).links
            if existing_links:
                shared_url = existing_links[0].url
            else:
                raise
        else:
            raise
    
    # Modifica a URL para ser usada diretamente em HTML
    return shared_url.replace("?dl=0", "?raw=1")


def create_folder_if_not_exists(folder_path):
    """Cria uma pasta no Dropbox apenas se ela não existir."""
    dbx = init_client_dbp()
    try:
        dbx.files_create_folder_v2(folder_path)
    except dropbox.exceptions.ApiError as e:
        if isinstance(e.error, dropbox.files.CreateFolderError) and e.error.is_path():
            return  # A pasta já existe, então não precisa recriar
        else:
            raise


def create_new_folder(folder_name=None):
    """Cria uma nova pasta no Dropbox e retorna o caminho da pasta."""
    try:
        folder_hash = folder_name if folder_name else generate_timestamp_hash()
        dropbox_folder = f"/uploads/{folder_hash}"
        create_folder_if_not_exists(dropbox_folder)
        return {"folder": folder_hash, "path": dropbox_folder}
    except Exception as e:
        raise Exception(f"Erro ao criar pasta: {str(e)}")


def upload_files_to_dropbox(files, folder_name=None):
    """Faz upload de múltiplos arquivos para o Dropbox e retorna os links compartilháveis."""
    dbx = init_client_dbp()
    try:
        # Se um diretório não for fornecido, gera um novo
        folder_hash = folder_name if folder_name else generate_timestamp_hash()
        dropbox_folder = f"/uploads/{folder_hash}"
        
        # Criar a pasta se não existir
        create_folder_if_not_exists(dropbox_folder)
        
        uploaded_files = {}
        for file_name, file_content in files.items():
            dropbox_path = f"{dropbox_folder}/{file_name}"
            dbx.files_upload(file_content, dropbox_path, mode=dropbox.files.WriteMode.overwrite)
            uploaded_files[file_name] = get_shared_link(dropbox_path)
        
        return folder_hash, uploaded_files
    except Exception as e:
        raise Exception(f"Erro ao fazer upload: {str(e)}")


def list_files_in_folder(folder_hash):
    """Lista os arquivos em uma pasta no Dropbox e retorna links diretos."""
    dbx = init_client_dbp()
    try:
        dropbox_folder = f"/uploads/{folder_hash}"
        response = dbx.files_list_folder(dropbox_folder)
        file_links = {}
        
        for entry in response.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                file_links[entry.name] = get_shared_link(entry.path_lower)
        
        return file_links
    except dropbox.exceptions.ApiError as e:
        raise Exception(f"Erro ao listar arquivos: {str(e)}")
