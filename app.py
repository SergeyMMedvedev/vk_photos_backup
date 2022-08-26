import os
import json
from dotenv import load_dotenv
from typing import List
from cloud_disk_model import AbstractCloudDisk
from ya_disk_api_service import YaUploader
from vk_api_service import VK
from google_drive_service import GoogleDriveService


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
            image_name += '_' + str(image['date'])
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

    def save_to_local_disk(self, images_names_and_urls: List[tuple]) -> None:
        """Сохраняет необходимые данные о фотографии на локальный диск"""
        photos_data = []
        for image_name, image_url in images_names_and_urls:
            image_size = image_url[image_url.rfind('/') + 1:image_url.rfind('_')]
            image = {
                "file_name": image_name,
                "size": image_size
            }
            photos_data.append(image)
        with open('back_up_photos_data.json', 'w', encoding='utf-8') as f:
            json.dump(photos_data, f, ensure_ascii=False, indent=4)

    def upload_to_cloud_disks(self, images_names_and_urls: List[tuple]) -> None:
        """Загружает файлы на облачные диски"""
        for cloud_disk in self.cloud_disks:
            cloud_disk.upload(images_names_and_urls)

    def back_up_photos(self, files_json: dict) -> None:
        """
        Создает резервные копии на виртуальных дисках 
        и записывает данные о сохраненных фотографиях в файл
        """
        images_names_and_urls = self._get_images_names_and_urls(files_json)
        self.save_to_local_disk(images_names_and_urls)
        self.upload_to_cloud_disks(images_names_and_urls)


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
    backup_service.back_up_photos(vk_photos)
