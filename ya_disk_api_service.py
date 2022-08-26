import requests
import time
from typing import List
from cloud_disk_model import AbstractCloudDisk
from utils import progress
from progress.bar import Bar


class YaUploader(AbstractCloudDisk):

    _BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
    _GET_FILES_URL = '/files'
    _UPLOAD_LINK_URL = '/upload'
    _BAR_NAME = 'Yandex API: '

    def __init__(self, token: str, folder_name: str) -> None:
        self.token = token
        self.folder = folder_name

    @property
    def folder(self) -> str:
        return self._folder

    @folder.setter
    def folder(self, folder_name: str) -> None:
        self._folder = folder_name + r'/'

    def _get_headers(self) -> dict:
        """Возвращает заголовки, наобходимые для отправки запросов к API Яндекс диска"""
        headers = {
            "Authorization": self.token,
            "Content-type": "application/json"
        }
        return headers

    def _create_resource(self) -> None:
        """Создает папку на Яндекс диске, где в дальнейшем будут храниться фото."""
        url = self._BASE_URL
        params = {
            "path": self.folder,
        }
        response = requests.put(url, headers=self._get_headers(), params=params)
        response.raise_for_status()

    def _get_resource(self) -> requests.models.Response:
        """Возвращает информацию о ресурсе (папке для хранения фото)"""
        url = self._BASE_URL
        params = {
            "path": self.folder,
        }
        response = requests.get(url, headers=self._get_headers(), params=params)
        return response

    @progress(_BAR_NAME, 'Проверка папки', '_folder')
    def _create_folder_if_not_exist(self) -> None:
        """
        Проверяет, существует ли указанная папка на Яндекс диске.
        Если нет, то запускает ее создание.
        """
        reourse_response = self._get_resource()
        if reourse_response.status_code == 404:
            self._create_resource()
        else:
            reourse_response.raise_for_status()

    def _check_upload(self, upload_response: requests.models.Response) -> bool:
        """Проверяет текущий статус загрузки файла ни диск"""
        href = upload_response.json().get('href')
        status_response = requests.get(href, headers=self._get_headers())
        status_response.raise_for_status()
        status = status_response.json().get('status')
        if status == 'success':
            return True
        elif status == 'in-progress':
            time.sleep(1)
            return self._check_upload(upload_response)

    @progress(_BAR_NAME, 'Загрузка фотографий на Яндекс Диск')
    def upload(self, files_names_and_urls: List[tuple]) -> None:
        """Загружает переданные файлы на Яндекс диск по url"""
        self._create_folder_if_not_exist()
        url = self._BASE_URL + self._UPLOAD_LINK_URL
        with Bar(self._BAR_NAME + ' загрузка фотографий', max=len(files_names_and_urls)) as bar:
            for image_name, image_url in files_names_and_urls:
                path_to_file = self.folder + image_name
                params = {
                    "path": path_to_file,
                    "url": image_url
                }
                response = requests.post(
                    url,
                    headers=self._get_headers(),
                    params=params,
                )
                response.raise_for_status()
                if not self._check_upload(response):
                    print(f'Something wrong while uploading\n{image_url}\nCheck url and file path')
                bar.next()


class YAException(Exception):
    pass
