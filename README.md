# Курсовой проект «Резервное копирование»

## Подготовка к работе
---

Клонирование проекта:
```
git clone git@github.com:SergeyMMedvedev/vk_photos_backup.git
```

Переход в папку проекта:
```
cd vk_photos_backup
```

Создание виртуального окружения:
```
python -m venv venv
```

Активация виртуального окружения (Windows):
```
source venv/Scripts/activate
```

Установка зависимостей:
```
pip install -r requirements.txt
```

Создание файла .env с секретами:
```
touch .env
```

Добавление необходимых переменных:
* Открыть редактор:
    ```
    nano .env
    ```
* Добавить необходимые переменные (со значениями заглушками)
    ```
    VK_USER_ID=some_user_id
    VK_TOKEN=some_vk_token
    YA_TOKEN=some_yandex_token
    ```
* Для сохранения нажать:

    * ctr + x
    * y
    * enter
    
Далее необходимо подставить собственные значения вместо заглушек.

Инструкция по получению токена Вконтакте:
https://docs.google.com/document/d/1_xt16CMeaEir-tWLbUFyleZl6woEdJt-7eyva1coT3w/edit

Ссылка на получение токена Полигона Яндекс Диска:
https://yandex.ru/dev/disk/poligon/

## Проверка сохраниния фотографий на Яндекс Диск
---

Для проверки сохранения на Яндекс Диск необходимо запустить
```
app.py
```

## Проверка сохраниния фотографий на Яндекс Диск и Google Drive
---

В **app.py** раскоментировать строки:
```
    # g_drive = GoogleDriveService(FOLDER_NAME)
    # cloud_disks.append(g_drive)
```


### Подготовка к работе Google Drive
---
Для взаимодействия с Google Drive необходимо создать приложение.
Для этого нужно выполнить следующие шаги:

Перейти в **Google cloud console**:

**https://console.cloud.google.com/**

Создаем приложение (кнопка справа сверху): **create project**

Сконфигурировать доступ:

Для этого слева в меню выбирать: **APIs & Services** -> **OAuth consent screen**

Выбирать: **external**. Указывать **имя**, а также **почту в двух местах**.
**Добавить пользователя**.

Перейти в **credentials** -> **Create credentials**

Выбирать **OAuth client ID**. Выбирать **Web App**.

Теперь нужно прописать url адреса для авторизации.

Для этого переходим к документации библиотеки, которую установили:

**https://pythonhosted.org/PyDrive/quickstart.html**

Скопировать указанные примеры и указать в настройках Web application:

* **Authorized JavaScript origins: http://localhost:8080**

* **Authorized redirect URIs: http://localhost:8080/**

При нажатии на **save** появится возможность скачать json-файл с данными, 
необходимыми для предоставления доступа приложения к аккаунту Goggle drive.

Файл необходимо скачать и сохранить внутри папки приложения (vk_photos_backup),
а также переименовать в **client_secrets.json**

Далее запустить
```
app.py
```

### Примечания

Если progress bar не отображается в Pycharm:
* Перейти в **Edit run configuration**
* поставить галочку **Emulate terminal in output console**