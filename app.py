import os
from dotenv import load_dotenv
from typing import List
from cloud_disk_model import AbstractCloudDisk
from ya_disk_api_service import YaUploader
from vk_api_service import VK
from google_drive_service import GoogleDriveService
from datetime import date


class BackupServiceException(Exception):
    pass


class BackupService:

    def __init__(self, cloud_disks: List[AbstractCloudDisk]) -> None:
        self.cloud_disks = cloud_disks
        self.image_likes_set = set()

    def _create_image_name(self, image: dict, image_url: str) -> str:
        """Возвращает имя файла на основе количества лайков, а также дате, если количество лайков у файлов совпадает"""
        image_likes = image['likes']['count']
        image_name = str(image_likes)
        if image_likes in self.image_likes_set:
            image_upload_date = str(date.fromtimestamp(image['date']))
            image_name += '_' + image_upload_date
        self.image_likes_set.add(image_likes)
        image_extension = image_url[image_url.rfind('.'):]
        image_name += image_extension
        return image_name

    def _get_images_names_and_urls(self, photos_json) -> List[tuple]:
        """Возвращает список кортежей с названием файла и ссылки для скачивания"""
        images_urls_list = []
        photos = photos_json.get('response', {})
        if not photos.get('count'):
            raise BackupServiceException('Photos not found')

        for item in photos.get('items', []):
            image_url = item['sizes'][-1]['url']
            image_name = self._create_image_name(item, image_url)
            images_urls_list.append((image_name, image_url))
        self.image_likes_set.clear()
        return images_urls_list

    def upload_to_cloud_disks(self, files_json: dict) -> None:
        """Загружает файлы на облачные диски"""
        images_names_and_urls = self._get_images_names_and_urls(files_json)

        # TODO удалить
        p1_url = 'https://sun9-30.userapi.com/c9884/u4470114/-6/x_a4439d91.jpg'
        p1_name = '17_1.jpg'
        images_names_and_urls.append((p1_name, p1_url))

        p1_url = 'https://sun9-30.userapi.com/c9884/u4470114/-6/x_a4439d91.jpg'
        p1_name = '17_2.jpg'
        images_names_and_urls.append((p1_name, p1_url))

        for cloud_disk in self.cloud_disks:
            cloud_disk.upload(images_names_and_urls)


if __name__ == '__main__':
    load_dotenv()
    VK_TOKEN = os.getenv('VK_TOKEN')
    VK_USER_ID = os.getenv('VK_USER_ID')
    YA_TOKEN = os.getenv('YA_TOKEN')
    FOLDER_NAME = 'Netology'
    cloud_disks = []

    vk = VK(VK_TOKEN, VK_USER_ID)
    vk_photos = vk.get_photos()

    ya = YaUploader(YA_TOKEN, FOLDER_NAME)
    cloud_disks.append(ya)

    """СОХРАНЕНИЕ НА GOOGLE DISK"""
    # g_drive = GoogleDriveService(FOLDER_NAME)
    # cloud_disks.append(g_drive)

    backup_service = BackupService(cloud_disks)
    backup_service.upload_to_cloud_disks(vk_photos)
