# Docker: стек и переустановка

Сборка и запуск из **корня репозитория** (`DTP_Akaito`):

```bash
docker compose up -d --build
```

- Фронт: http://localhost:3000  
- API: http://localhost:8080/docs  

Зависимости Python для образа: **`backend/requirements-docker.txt`**.

---

## Пользователи и администратор

Обычные пользователи **не регистрируются сами**. Создавать учётки может только **администратор**.

### Первый администратор (деплой)

В **`compose.yaml`** для сервиса **`api`** раскомментируйте и задайте свой пароль:

```yaml
DTP_BOOTSTRAP_LOGIN: admin
DTP_BOOTSTRAP_PASSWORD: <сильный-пароль>
DTP_BOOTSTRAP_ADMIN: "1"
```

При **пустой** БД пользователь создаётся **один раз** при старте API. Пароли в git не храните.

### Дальнейшие пользователи (только админ)

1. **Через API** (нужна сессия админа): `POST /api/v1/admin/users` с телом  
   `{"login":"operator1","password":"...","is_admin":false}`

2. **Через CLI** в контейнере — только если задан секрет **`DTP_USER_CREATE_SECRET`** (в compose, не в репозитории):

   ```bash
   docker compose exec api sh -c "cd /app/backend && python create_test_user.py --login op1 --password 'Secret123' --secret 'ваш-секрет'"
   ```

   Администратора: добавьте **`--admin`**.

### Уведомления в UI

- В БД должен быть **хотя бы один пользователь**, и вы должны **войти** в UI под ним — иначе записи уведомлений не создаются / не отображаются.
- Скриншот кладите в **`data/screenshots/`** (новый файл, лучше уникальное имя).
- Смотрите логи: `docker compose logs -f watchdog api`

---

## Скриншоты и уведомления (watchdog)

Папка на **вашем ПК** (из корня репозитория):

`data/screenshots/`

Она смонтирована в контейнеры **`watchdog`** и **`api`** как `/app/data/screenshots`. Положите туда `.png` / `.jpg` — watchdog отправит кадр в API, при детекции ДТП появятся уведомления в UI.

Другой путь на хосте (опционально):

```bash
# .env рядом с compose.yaml или в shell
SCREENSHOTS_HOST_DIR=D:/MyFrames
```

После смены `compose.yaml` или пути:

```bash
docker compose up -d --build
docker compose logs -f watchdog
```

На Windows через Docker Desktop для bind mount включён **опрос каталога** (`WATCHDOG_USE_POLLING=1`), иначе события «новый файл» с диска хоста часто не доходят до watchdog.

---

## Меняется ли код в контейнере, если правите файлы на ПК

**По умолчанию — нет.** Образ собирается командой **`docker compose build`**: внутрь кладётся снимок **`backend/`** на момент сборки. Правки на диске **появятся в контейнере только после** **`docker compose build`** (или **`up --build`**) и перезапуска.

Для **разработки с live-изменениями** можно добавить в override том с монтированием исходников поверх `/app/backend` (отдельный `docker-compose.override.yml`) — тогда код в контейнере читается с хоста; в штатном compose этого нет.

Фронт в production-образе — только **`npm run build`** -> слой **`.next`**; правки в `frontend/` тоже требуют **пересборки** образа frontend.

---

## Переустановка контейнеров (пересобрать образы)

1. Остановить и удалить контейнеры сети проекта (тома по умолчанию **не** удаляются — база и скрины в `dtp_data` сохранятся):

   ```bash
   docker compose down
   ```

2. Пересобрать образы и поднять снова:

   ```bash
   docker compose up -d --build
   ```

Если нужна **чистая пересборка слоёв** (дольше, но без старого кэша сборки этого проекта):

```bash
docker compose build --no-cache
docker compose up -d
```

---

## Полный сброс вместе с данными (новая БД и пустые скрины)

Удаляет именованный том **`dtp_data`** (SQLite и содержимое `data/screenshots` внутри стека):

```bash
docker compose down -v
docker compose up -d --build
```

Флаг **`-v`** у `down` удаляет тома, объявленные в `compose.yaml` для этого проекта.

---

## Если меняли только `requirements-docker.txt`

Достаточно пересобрать backend-образ и перезапустить:

```bash
docker compose build --no-cache api yolo-worker watchdog
docker compose up -d
```

(Имена сервисов совпадают с `compose.yaml`: `api`, `yolo-worker`, `watchdog` используют один и тот же образ.)

---

## Логи и отладка

```bash
docker compose logs -f
docker compose logs -f api
```

Проверка конфигурации compose без запуска:

```bash
docker compose config
```

---

## Откуда берётся «transferring context: N GB»

В контекст сборки попадает **весь каталог репозитория на диске**, кроме путей из **`.dockerignore`**. Размер в логе — это **не** размер образа после `COPY`, а то, что Docker **передаёт демону** перед сборкой.

**Как проверить у себя на диске**, что раздувает папку (до и после правок `.dockerignore` на размер передачи это не влияет на «файлы на диске», но помогает понять, что исключить):

```bash
python docker/scripts/context_size_report.py
```

У вас основной объём давали **`backend/venv-api`**, **`backend/src/traffic_dtp/ml/venv-ml`** и **`backend/src/traffic_dtp/ml/dataset`** — они добавлены в `.dockerignore`, контекст должен упасть с **~2+ ГБ** до **сотен МБ** (плюс `frontend/` без `node_modules`).

**Что реально попадает в backend-образ** задаётся в `docker/Dockerfile.backend`: копируются только `backend/requirements-docker.txt`, `docker/backend-entrypoint.sh` и каталог **`backend/`** уже **после** применения `.dockerignore` (в образ не попадают venv, датасет и т.д.).

---

## Ошибка `unexpected EOF` при сборке

Чаще всего это **обрезанный слой** (не хватило места на диске Docker, обрыв сети, «битый» кэш).

1. Закройте **Docker Desktop** (Quit), освободите **10–20+ ГБ** на диске, где лежит виртуальный диск Docker.
2. Запустите Docker снова, выполните:

   ```bash
   docker builder prune -a -f
   docker pull python:3.11-slim
   ```

3. Повторите сборку:

   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

В **`.dockerignore`** исключены: venv; **обучение** (`ml/dataset`, `ml/train_n_check`, `ml/converts`, при наличии `ml/train`, `ml/val`); старые прогоны `dtp_krasnodar_light`…`light8`; все **`.pt`** кроме **`dtp_krasnodar_light9/weights/best.pt`**; растровые файлы под **`backend/`** (фронт не трогаем). **Скриншоты watchdog** — это рабочие кадры; в Docker они монтируются **томом** в **`/app/data/screenshots`**, а строки **`data/`** и **`**/screenshots`** убирают только **локальные копии из контекста сборки**, чтобы не гонять гигабайты в `docker build`, а не «отключать» watchdog.

---

## Ошибка pip: `Network is unreachable` / `Temporary failure in name resolution`

На шаге **`RUN pip install ...`** нужен **интернет** до **pypi.org** / **files.pythonhosted.org**. **Errno 101** / **-3** — нет маршрута или DNS (VPN, фаервол, Wi‑Fi, настройки Docker).

1. Отключите **VPN** или смените сеть, повторите `docker compose up -d --build`.
2. **Docker Desktop** -> *Settings* -> *Network* — DNS **8.8.8.8** / **1.1.1.1** или «использовать DNS хоста», перезапуск Docker.
3. В **`docker/Dockerfile.backend`** для pip заданы **больший таймаут и число повторов** — при кратких обрывах помогает пересобрать.

Если PyPI с вашей сети недоступен, нужен свой **индекс пакетов** (корпоративное зеркало) через **`PIP_INDEX_URL`** / **`PIP_EXTRA_INDEX_URL`** на этапе сборки.
