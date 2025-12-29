## Деплой через GitHub Actions → GHCR → SSH

Этот репозиторий содержит workflow `.github/workflows/deploy.yml`, который:

- **Job 1 (build_and_push)**: собирает Docker-образ и пушит его в **GitHub Container Registry (GHCR)**.
- **Job 2 (deploy_via_ssh)**: подключается по **SSH** к вашему серверу, делает `docker pull` образа из GHCR и перезапускает контейнер.

### 1) Требования на удалённом сервере

- Установлен **Docker**.
- Пользователь, под которым вы подключаетесь по SSH, имеет доступ к Docker:
  - либо в группе `docker`,
  - либо вы используете `sudo docker ...` (тогда нужно адаптировать `script` в workflow).
- Открыт **внешний порт сервиса** (по умолчанию **8001/tcp**), если сервис должен быть доступен извне.

### 2) Какие секреты нужно добавить в GitHub

Откройте: **Repository → Settings → Secrets and variables → Actions → New repository secret**.

#### SSH

- **`SSH_HOST`**: домен или IP сервера
- **`SSH_PORT`**: порт SSH (например `22`, можно не задавать — по умолчанию будет `22`)
- **`SSH_USER`**: пользователь на сервере
- **`SSH_PRIVATE_KEY`**: приватный ключ (формат OpenSSH, строка целиком с `-----BEGIN ...`)
- **`SSH_PASSPHRASE`**: passphrase от приватного ключа (если ключ зашифрован)

#### Частые ошибки с ключом (и как исправить)

- **`ssh.ParsePrivateKey: ssh: no key found`**:
  - **Причина**: в `SSH_PRIVATE_KEY` лежит **не приватный ключ**, либо он в **неподдерживаемом формате**.
  - **Проверьте**: содержимое секрета должно начинаться и заканчиваться так (пример):
    - `-----BEGIN OPENSSH PRIVATE KEY-----` ... `-----END OPENSSH PRIVATE KEY-----`
    - или `-----BEGIN RSA PRIVATE KEY-----` ... `-----END RSA PRIVATE KEY-----`
  - **Важно**: строка вида `ssh-ed25519 AAAA...` / `ssh-rsa AAAA...` — это **публичный ключ**, его в `SSH_PRIVATE_KEY` класть нельзя.
  - **Windows/PuTTY**: если у вас ключ в формате `.ppk`, GitHub Actions/`appleboy/ssh-action` его не прочитает — конвертируйте в OpenSSH:

```bash
puttygen key.ppk -O private-openssh -o id_deploy
```

- **`ssh: handshake failed: unable to authenticate, attempted methods [none publickey]`**:
  - **Причина**: приватный ключ распарсился, но сервер его не принимает (нет соответствующего public key в `~/.ssh/authorized_keys`, неверный `SSH_USER`, права/владение файлов `.ssh`).
  - **Проверьте на сервере**: публичный ключ (файл `*.pub`) добавлен в `~/.ssh/authorized_keys` пользователя `SSH_USER`.

#### Доступ к GHCR с сервера

Чтобы сервер мог скачивать образы из GHCR, добавьте:

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
- `HOST_PORT`: внешний порт на сервере (по умолчанию `8001`) — поставьте любой свободный
- `CONTAINER_PORT`: порт внутри контейнера (по умолчанию `8000`) — обычно не меняют

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


