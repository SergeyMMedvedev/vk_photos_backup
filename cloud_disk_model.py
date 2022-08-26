import abc
from typing import List


class AbstractCloudDisk(abc.ABC):
    @abc.abstractmethod
    def upload(self, files: List[tuple]):
        """Метод для загрузки файлов в облачное хранилище"""
        raise NotImplementedError
