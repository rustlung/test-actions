## Деплой через GitHub Actions → GHCR → SSH

Этот репозиторий содержит workflow `.github/workflows/deploy.yml`, который:

- **Job 1 (build_and_push)**: собирает Docker-образ и пушит его в **GitHub Container Registry (GHCR)**.
- **Job 2 (deploy_via_ssh)**: подключается по **SSH** к вашему серверу, делает `docker pull` образа из GHCR и перезапускает контейнер.

### 1) Требования на удалённом сервере

- Установлен **Docker**.
- Пользователь, под которым вы подключаетесь по SSH, имеет доступ к Docker:
  - либо в группе `docker`,
  - либо вы используете `sudo docker ...` (тогда нужно адаптировать `script` в workflow).
- Открыт порт приложения (по умолчанию **8000/tcp**), если сервис должен быть доступен извне.

### 2) Какие секреты нужно добавить в GitHub

Откройте: **Repository → Settings → Secrets and variables → Actions → New repository secret**.

#### SSH

- **`SSH_HOST`**: домен или IP сервера
- **`SSH_PORT`**: порт SSH (например `22`, можно не задавать — по умолчанию будет `22`)
- **`SSH_USER`**: пользователь на сервере
- **`SSH_PRIVATE_KEY`**: приватный ключ (формат OpenSSH, строка целиком с `-----BEGIN ...`)
- **`SSH_PASSPHRASE`**: passphrase от приватного ключа (если ключ зашифрован)

#### Доступ к GHCR с сервера

Чтобы сервер мог скачивать образы из GHCR, добавьте:

- **`GHCR_USERNAME`**: ваш GitHub username или org (владелец пакета)
- **`GHCR_TOKEN`**: GitHub PAT токен с правами:
  - **`read:packages`** (обязательно)
  - если пакет приватный и GitHub потребует — добавьте также `repo`

> Примечание: в job сборки используется `GITHUB_TOKEN`, поэтому отдельный PAT для **push** не нужен.

### 3) Как работает деплой

Workflow собирает и пушит образы с тегами:

- `ghcr.io/<owner>/<repo>:<sha>`
- `ghcr.io/<owner>/<repo>:latest`

На сервере деплой использует **точный** образ по SHA (повторяемость релизов).

### 4) Как запустить

- **Автоматически**: при пуше в ветку `main`.
- **Вручную**: вкладка **Actions** → workflow **Build & Deploy (GHCR)** → **Run workflow**.

### 5) Настройки, которые чаще всего меняют

В `.github/workflows/deploy.yml` можно поменять (секция `env`):

- `CONTAINER_NAME`: имя контейнера на сервере (по умолчанию `time-api`)
- `APP_PORT`: порт, на который пробрасывается сервис (по умолчанию `8000`)

Если нужно передавать переменные окружения контейнеру — добавьте в `docker run` строки вида:

```bash
-e KEY=value \
```

Если контейнер должен быть в сети Docker/Compose или нужно несколько сервисов — лучше перейти на `docker compose` и запускать `docker compose pull && docker compose up -d`.

### 6) Быстрая проверка после деплоя

На сервере:

```bash
docker ps --filter "name=time-api"
docker logs --tail 200 time-api
```

Снаружи (если порт доступен):

- `GET /health`
- `GET /time`


