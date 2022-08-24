import mimetypes
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import os
import shutil

import asyncio


# gauth = GoogleAuth()

# auth_url = gauth.GetAuthUrl()


# print(gauth.credentials)
# gauth.LocalWebserverAuth()
# gauth.LoadCredentialsFile("client_secrets.json")
# gauth.Authorize()
# print(gauth.credentials)


gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.LocalWebserverAuth()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile('mycreds.txt')


class GoogleDriveService:

    def __init__(self):
        self.folder = r'Netolody/'
        self.__creds_file = 'mycreds.txt'
        self._folder = 'Netology'
        self.drive = GoogleDrive(gauth)

    def create_folder(self):
        print('create_folder')
        drive = GoogleDrive(gauth)
        file_metadata = {
            'title': self._folder,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive.CreateFile(file_metadata)
        folder.Upload()

    async def get_folder_id(self):
        print('get_folder_id')
        folder = self._get_folder()
        if not folder:
            self.create_folder()
        folder = self._get_folder()
        return folder['id']

    async def _send_files(self, files, folder_id):
        print('_send_files')
        for file_name, file_content in files:
            my_file = self.drive.CreateFile({'parents': [{'id': folder_id}], 'title': file_name})
            with open(os.path.join('tmp', file_name), 'wb') as f:
                f.write(file_content)
            my_file.SetContentFile(os.path.join('tmp', file_name))
            my_file.Upload()

    def _get_folder(self):
        print('_get_folder')
        folders = self.drive .ListFile(
            {
                'q': "title='" + self._folder + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            }
        ).GetList()
        if folders:
            return folders[0]

    def upload(self, files):
        print('upload')
        if os.path.isdir('tmp'):
            shutil.rmtree('tmp')
        os.mkdir('tmp')
        folder_id = asyncio.run(self.get_folder_id())
        asyncio.run(self._send_files(files, folder_id))
        shutil.rmtree('tmp')

