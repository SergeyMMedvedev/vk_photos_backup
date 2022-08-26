import requests
import os
import shutil
import asyncio
from typing import List
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cloud_disk_model import AbstractCloudDisk
from utils import progress
from progress.bar import Bar


class GoogleDriveService(AbstractCloudDisk):

    _FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
    _BAR_NAME = 'Google drive API: '

    def __init__(self, folder_name: str) -> None:
        self.__creds_file = 'mycreds.txt'
        self._folder = folder_name
        self._gauth = GoogleAuth()
        self._drive = GoogleDrive(self._gauth)

    @classmethod
    def _check_client_secrets(cls):
        """Проверка наличия client_secrets.json"""
        if not os.path.exists('client_secrets.json'):
            raise GoogleDriveServiceException(
                f'\nДля работы с Google drive необходимо загрузить файл с данными для аутентификации client_secrets.json'
            )

    def _authorize(self) -> None:
        """Предоставление доступа текущего приложения к аккаунту Goggle drive"""
        self._gauth.LoadCredentialsFile(self.__creds_file)
        if self._gauth.credentials is None or self._gauth.access_token_expired:
            self._gauth.LocalWebserverAuth()
        else:
            self._gauth.Authorize()
        self._gauth.SaveCredentialsFile(self.__creds_file)

    @progress(_BAR_NAME, 'Загрузка файлов')
    def _download_files(self, files_name_and_url: List[tuple]) -> List[tuple]:
        """Возвращает список загруженных по ссылкам файлов"""
        files_list = []
        with Bar(self._BAR_NAME + ' загрузка файлов по url', max=len(files_name_and_url)) as iter_bar:
            for f_name, f_url in files_name_and_url:
                response = requests.get(f_url)
                response.raise_for_status()
                file = response.content
                files_list.append((f_name, file))
                iter_bar.next()
        return files_list

    def _create_folder(self) -> None:
        """Создание папки на Google диске для дальнейшего сохранения в нее фотографий"""
        file_metadata = {
            'title': self._folder,
            'mimeType': self._FOLDER_MIMETYPE
        }
        folder = self._drive.CreateFile(file_metadata)
        folder.Upload()

    def _get_folder(self) -> any:
        """Возвращает информацию о папке, в которую будут загружаться фотографии"""
        folders = self._drive.ListFile(
            {'q': f'title="{self._folder}" and mimeType="{self._FOLDER_MIMETYPE}" and trashed=false'}
        ).GetList()
        if folders:
            return folders[0]

    @progress(_BAR_NAME, 'Получение Id папки на Google диске')
    async def _get_folder_id(self):
        """Возвращает Id папки, в которую будут сохраняться фотографии"""
        folder = self._get_folder()
        if not folder:
            self._create_folder()
        folder = self._get_folder()
        return folder['id']

    async def _send_files(self, files, folder_id):
        """Отправка файлов из временной папки tmp на Google диск"""
        with Bar(self._BAR_NAME + ' отправка на Google диск', max=len(files)) as iter_bar:
            for file_name, file_content in files:
                my_file = self._drive.CreateFile({'parents': [{'id': folder_id}], 'title': file_name})
                with open(os.path.join('tmp', file_name), 'wb') as f:
                    f.write(file_content)
                my_file.SetContentFile(os.path.join('tmp', file_name))
                my_file.Upload()
                iter_bar.next()

    @progress(_BAR_NAME, 'Загрузка фотографий на Google диск')
    def upload(self, files_name_and_url):
        """Загрузка файлов на Google диск"""
        self._check_client_secrets()
        self._authorize()
        files = self._download_files(files_name_and_url)
        if os.path.isdir('tmp'):
            shutil.rmtree('tmp')
        os.mkdir('tmp')
        folder_id = asyncio.run(self._get_folder_id())
        asyncio.run(self._send_files(files, folder_id))
        shutil.rmtree('tmp')


class GoogleDriveServiceException(Exception):
    pass
