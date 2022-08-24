import os
import requests
from pprint import pprint
from dotenv import load_dotenv
from ya_disk_api_service import YaUploader
from vk_api_service import VK
from google_drive_service import GoogleDriveService


class BackupServise:

    def download_files(self, files_name_and_url):
        files_list = []
        for f_name, f_url in files_name_and_url:
            response = requests.get(f_url)
            response.raise_for_status()
            file = response.content
            files_list.append((f_name, file))
        return files_list



if __name__ == '__main__':
    load_dotenv()
    vk = VK(os.getenv('vk_token_photos'), os.getenv('user_id'))
    images_names_and_urls = vk.get_images_names_and_urls()

    YA_TOKEN = os.getenv('YA_TOKEN')
    ya = YaUploader(YA_TOKEN)

    # for image_name, image_url in images_names_and_urls:
    #     print(image_name)
    #     ya.upload(image_name, image_url)

    backup_service = BackupServise()
    files = backup_service.download_files(images_names_and_urls)
    g_drive_service = GoogleDriveService()
    g_drive_service.upload(files)

