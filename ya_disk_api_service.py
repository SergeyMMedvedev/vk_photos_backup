import requests
import os
from dotenv import load_dotenv
import time

class YaUploader:

    BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
    GET_FILES = '/files'
    UPLOAD_LINK = '/upload'

    def __init__(self, token) -> None:
        self.token = token
        self.folder = r'Netolody/'

    def get_headers(self):
        headers = {
            "Authorization": self.token,
            "Content-type": "application/json"
        }
        return headers

    def get_files(self):
        url = self.BASE_URL + self.GET_FILES
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json()

    def _get_upload_link(self, params):
        url = self.BASE_URL + self.UPLOAD_LINK
        response = requests.get(url, headers=self.get_headers(), params=params)
        response.raise_for_status()
        response_body = response.json()
        href = response_body.get('href', '')
        return href

    def create_resource(self):
        url = self.BASE_URL
        params = {
            "path": self.folder,
        }
        response = requests.put(url, headers=self.get_headers(), params=params)
        response.raise_for_status()
        if response.status_code == 201:
            print(f'Folder {self.folder} successfully created!')

    def get_resource(self):
        url = self.BASE_URL
        params = {
            "path": self.folder,
        }
        response = requests.get(url, headers=self.get_headers(), params=params)
        return response


    def check_folder(self):
        reourse_response = self.get_resource()
        print('reourse_response.status_code', reourse_response.status_code)
        if reourse_response.status_code == 404:
            print(f'Creating new folder: {self.folder}...')
            self.create_resource()
        else:
            reourse_response.raise_for_status()

    def upload_by_link(self, image_file, image_name):
        self.check_folder()
        path_to_file = self.folder + image_name
        params = {
            "path": path_to_file,
            "overwrite": "true"
        }
        url = self._get_upload_link(params)
        response = requests.put(
            url,
            headers=self.get_headers(),
            params=params,
            data=image_file
        )
        response.raise_for_status()
        if response.status_code == 201:
            print(f'{params["path"]} successfully created!')

    def upload(self, image_name, image_url):
        self.check_folder()
        url = self.BASE_URL + self.UPLOAD_LINK
        path_to_file = self.folder + image_name
        params = {
            "path": path_to_file,
            "url": image_url
        }
        print(f'Uploading {image_name} to {self.folder}...')
        response = requests.post(
            url,
            headers=self.get_headers(),
            params=params,
        )
        response.raise_for_status()
        if self.check_upload(response):
            print(f'Upload complete successfully:\n{path_to_file}')
        else:
            print(f'Something wrong. Check url and file path')


    def check_upload(self, upload_response):
        href = upload_response.json().get('href')
        status_response = requests.get(href, headers=self.get_headers())
        status_response.raise_for_status()
        print(status_response.json())
        status = status_response.json().get('status')
        if status == 'success':
            return True
        elif status == 'in-progress':
            print('Photo downloading to disk in progress...')
            time.sleep(1)
            return self.check_upload(upload_response)
            

