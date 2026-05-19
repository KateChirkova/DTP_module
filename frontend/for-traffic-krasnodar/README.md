# Внедрение модуля DTP в ваш сервис traffic_krasnodar

Инструкция для сотрудников. Вы переносите в репозиторий [traffic_krasnodar](https://github.com/Predatorevil666/traffic_krasnodar) **весь** модуль DTP: API, обработку скриншотов, уведомления и UI поверх **вашей** уже существующей карты и шапки.

Исходник модуля: репозиторий **DTP_Akaito** (отдаёте коллегам архив или submodule).

---

## Два контура: демо в DTP_Akaito и внедрение у вас

Пока идёт внедрение, **оба варианта живут параллельно**. Это нормально.

| | DTP_Akaito (демо, промежуточный показ) | traffic_krasnodar (целевой продукт) |
|---|----------------------------------------|-------------------------------------|
| Зачем | Показать заказчику/команде работающий модуль без ожидания слияния репозиториев | Боевой сервис с **вашей** картой и шапкой |
| Карта и шапка | `traffic-shell/`, `embed-ui/`, `app/page.tsx` — упрощённый макет «как у вас» | Ваши `header.tsx`, `yandex-map-iframe.tsx`, `TrafficLegend` — **не заменяем** |
| Модуль DTP | Уже подключён: login, API, FAB, панель, toast, docker compose | Переносите **только слой DTP** (шаги ниже) |
| Запуск | `docker compose up` в корне DTP_Akaito → http://localhost:3000 | Ваш frontend + backend DTP из submodule |

**В DTP_Akaito намеренно остаётся то, что в traffic_krasnodar не внедряется:** оболочка `traffic-shell`, декоративные кнопки в `embed-ui`, отдельная вёрстка главной. Это не ошибка — это **стенд для демонстрации**, пока вы встраиваете ядро в свой `frontend/`.

**В traffic_krasnodar внедряется:** backend (api, watchdog, yolo), auth, уведомления, правки ваших `header` / карты. Оболочку из DTP туда не копируйте.

### Что показывать на промежуточных этапах

1. **Только backend** — Swagger http://localhost:8080/docs, health, тестовый кадр в `data/screenshots/` (можно без вашего фронта).
2. **Демо-фронт DTP_Akaito** — полный UI модуля на localhost:3000 в этом репозитории (вход, FAB, панель, WS). Карта — макет, не ваш прод.
3. **Гибрид** — backend из DTP + ваш сайт с одной добавкой (например только FAB на карте).
4. **Цель** — всё в traffic_krasnodar: ваш UI + модуль DTP, демо-стенд DTP_Akaito можно не показывать заказчику.

На совещании честно говорите: «сейчас на стенде DTP_Akaito — готовый модуль; в traffic_krasnodar переносим по шагам, карта и шапка остаются вашими».

---

## Что у вас уже есть (не трогать без нужды)

В [traffic_krasnodar](https://github.com/Predatorevil666/traffic_krasnodar) сейчас:

- `frontend/app/page.tsx` — главная: ваш `Header` + ваш `MapWrapper`
- `frontend/components/header.tsx` — заголовок «Управление дорожным движением», справа **две рабочие** кнопки: камера (настройки скриншота) и экспорт (панели `ScreenshotSettings`, `TrafficExport`)
- `frontend/components/map-wrapper.tsx` → `yandex-map-iframe.tsx` — iframe Яндекс.Карт и **легенда пробок** (`TrafficLegend`)
- `frontend/components/ui/*` — полный набор shadcn (включая drawer, toast)
- `backend/index.html`, `server.js` — старый вариант с картой через Express; для модуля DTP **не используется**

Модуль DTP **не заменяет** вашу карту и шапку. Он добавляет вход, API, уведомления о ДТП и кнопку на карте.

---

## Чем отличается DTP_Akaito (что не копировать слепо)

| У вас в traffic_krasnodar | В DTP_Akaito (эталон, не подменяет ваш UI) |
|---------------------------|--------------------------------------------|
| `components/header.tsx` с Popover и реальной логикой | `traffic-shell/` + `modules/embed-ui/` — упрощённые иконки Camera/FileDown **без** ваших панелей |
| `yandex-map-iframe.tsx` + `TrafficLegend` | `traffic-shell/map-wrapper.tsx` — только iframe, без легенды |
| Нет уведомлений и входа | `NotificationIcon`, панель `notification-drawer`, `/login`, auth |
| Нет FastAPI | `backend/src/traffic_dtp/`, watchdog, yolo-worker |

**Не копируйте** в ваш проект:

- `components/traffic-shell/`
- `modules/embed-ui/`
- `components/dtp-on-map/DtpMapOverlayDemo` (демо без API)

**Копируйте** только слой DTP (auth, API, уведомления) и встройте в **ваши** `header.tsx` и `map-wrapper.tsx`.

---

## Что входит в модуль целиком

1. **frontend (добавка)** — вход, FAB уведомлений, боковая панель, toast о новых ДТП  
2. **backend** — FastAPI: пользователи, сессии, уведомления, WebSocket  
3. **watchdog** — следит за `data/screenshots/`  
4. **yolo-worker** — распознавание на кадрах  
5. **data** — SQLite и папка скриншотов  

Только frontend без backend не даст рабочих уведомлений.

---

## Шаг 1. Положить код DTP в ваш репозиторий

Рекомендуется submodule:

```bash
cd traffic_krasnodar
git submodule add <url-DTP_Akaito> vendor/dtp-akaito
```

Либо один раз скопировать:

- `vendor/dtp-akaito/backend/` — весь backend DTP  
- `vendor/dtp-akaito/docker/` — Dockerfile.backend, entrypoint  
- из корня DTP_Akaito: `compose.yaml`, `.env.example` — в ваш `deploy/` или корень  

В README вашего репозитория зафиксируйте коммит DTP_Akaito.

Папку `backend/index.html` и корневой `server.js` для модуля DTP можно оставить для старых ссылок; продакшен-схема — Next.js + Docker из шага 2.

---

## Шаг 2. Docker: один compose на весь сервис

Возьмите `compose.yaml` из DTP_Akaito. Сервисы:

- **frontend** — ваш Next.js из `frontend/` (у вас уже есть `frontend/Dockerfile`)  
- **api**, **watchdog**, **yolo-worker** — из DTP  
- общий volume **data** (БД + `screenshots`)

Минимум в `.env`:

```
DTP_INTERNAL_API_KEY=длинная-случайная-строка
DTP_BOOTSTRAP_LOGIN=admin
DTP_BOOTSTRAP_PASSWORD=надёжный-пароль
DTP_BOOTSTRAP_ADMIN=1
CORS_ORIGINS=https://ваш-домен,http://localhost:3000
```

Проверка:

```bash
docker compose up -d --build
```

- `http://localhost:8080/health` — healthy  
- `http://localhost:3000` — ваш фронт  

Ключи карт (`YANDEX_MAPS_API_KEY` и т.д.) остаются вашими, как в README traffic_krasnodar.

---

## Шаг 3. Скриншоты

Папка `data/screenshots/` на сервере (как в compose DTP). Watchdog и api должны видеть **одну** папку.

Тест: положите `.png` в папку, смотрите логи:

```bash
docker compose logs -f watchdog api
```

Не должно быть 403 на `POST /detections`.

---

## Шаг 4. Скопировать файлы DTP во frontend (новые папки)

Из `DTP_Akaito/frontend` в ваш `frontend/`:

**Новые компоненты:**

- `components/notification-icon.tsx`
- `components/notification-drawer.tsx`

**Новые каталоги:**

- `contexts/AuthContext.tsx`, `contexts/NotificationsContext.tsx`
- `hooks/use-notifications.tsx`, `hooks/accident-notifications.tsx`
- `lib/api.ts`, `http.ts`, `session.ts`, `session-events.ts`, `storage.ts`, `auth-cookie.ts`, `datetime.ts`, `ui-events.ts`, `app-log.ts`, `dev-log.ts`

**Страница входа и защита маршрутов:**

- `app/login/page.tsx`
- `middleware.ts` в корень `frontend/`

**UI:** ваш `components/ui/` уже большой. Добавьте из DTP только то, чего нет:

- `components/ui/page-spinner.tsx` — если нет аналога

`badge`, `button`, `card`, `drawer`, `input`, `toast`, `toaster` — **не перезаписывайте**, если у вас они уже есть; панель уведомлений использует ваш `drawer` + классы `dtp-*` из CSS.

**Пакеты** (если чего-то нет в `package.json`):

```bash
cd frontend
npm install vaul @radix-ui/react-dialog @radix-ui/react-slot @radix-ui/react-toast
```

`lucide-react`, `clsx`, `tailwind-merge` у вас, скорее всего, уже стоят.

**Стили:** в `app/globals.css` **добавьте** блоки из DTP_Akaito `globals.css`:

- переменные `:root` для shadcn (если конфликтуют с вашими — слейте вручную)
- все классы `dtp-fab`, `dtp-drawer`, `dtp-toast`, `dtp-login-page`
- при необходимости `app-body-layout`, `app-viewport` для layout

Ваши `calendar-styles.css` и стили карты **не удаляйте**.

---

## Шаг 5. Правки ваших файлов (главное)

### 5.1. `components/map-wrapper.tsx` и `yandex-map-iframe.tsx`

Сейчас карта без слота для overlay. Нужно повесить `NotificationIcon` **поверх** iframe (как в DTP: контейнер `position: relative`).

Вариант А — в `yandex-map-iframe.tsx` в конец `div className="relative w-full h-full"`:

```tsx
import { NotificationIcon } from "@/components/notification-icon"

// внутри return, после TrafficLegend:
<NotificationIcon />
```

Вариант Б — проп `overlay` в `MapWrapper` и передать `<NotificationIcon />` из `page.tsx` (см. `DTP_Akaito/frontend/components/traffic-shell/map-wrapper.tsx` — только идея overlay, папку `traffic-shell` не копируйте).

Легенду пробок **оставьте** как есть.

### 5.2. `components/header.tsx`

**Не заменяйте** файл на DTP-шапку. Добавьте третью кнопку — **Выйти** — рядом с Camera и FileDown:

```tsx
import { LogOut } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"

// внутри Header:
const { logout } = useAuth()

// в блок с кнопками справа, после Popover экспорта:
<Button variant="outline" size="icon" onClick={() => void logout()} title="Выйти">
  <LogOut className="h-4 w-4" />
</Button>
```

Иконки Camera / FileDown и ваши панели **не трогайте** — это ваш функционал, в DTP они только нарисованы декоративно.

### 5.3. `app/layout.tsx`

По образцу `DTP_Akaito/frontend/app/layout.tsx`, **внутри** вашего `ThemeProvider`:

- `AuthProvider`
- `NotificationsProvider`
- `AccidentNotifications`
- `Toaster` (ваш из `components/ui/toaster` — проверьте, что подключён один раз)

Метаданные title/description можно оставить ваши.

### 5.4. `app/page.tsx`

Оберните страницу в `RequireAuth`:

```tsx
import { RequireAuth } from "@/contexts/AuthContext"
// ...
export default function Home() {
  return (
    <RequireAuth>
      <main className="h-screen w-full flex flex-col">
        <Header />
        <MapWrapper />
      </main>
    </RequireAuth>
  )
}
```

Структура `Header` + `MapWrapper` **остаётся вашей**.

### 5.5. `middleware.ts`

Скопированный из DTP: без cookie `dtp_auth` редирект на `/login`. Пути `/login` и статику исключите так же, как в DTP_Akaito.

---

## Шаг 6. Адрес API

`frontend/.env.local`:

```
NEXT_PUBLIC_API_BASE=http://localhost:8080
```

На проде — URL, с которого браузер достучится до API (часто тот же домен, что и сайт).

После смены — `npm run build` и пересборка образа frontend.

Прокси `/api/v1` на api:8080 — см. шаг 7.

---

## Шаг 7. Один домен (прод)

На nginx или в `next.config.mjs`:

- `/` → ваш Next.js  
- `/api/v1/` → контейнер api:8080  
- WebSocket `/api/v1/ws/` с upgrade  

Тогда:

```
NEXT_PUBLIC_API_BASE=https://ваш-домен
```

В `CORS_ORIGINS` API укажите `https://ваш-домен`.

---

## Шаг 8. Приёмка

1. `docker compose up` — api healthy, все сервисы running  
2. Открывается ваш сайт, редирект на `/login`, вход bootstrap-логином  
3. Видны **ваша** шапка (камера, экспорт) + **новая** кнопка выхода  
4. На карте — **ваша** легенда пробок + FAB уведомлений (треугольник, счётчик)  
5. Панель уведомлений открывается справа (drawer)  
6. DevTools: `verify`, `notifications` — 200, есть WebSocket  
7. Файл в `data/screenshots/` → toast «Новое ДТП»  
8. Выход → снова `/login`  

---

## Если не работает

- FAB не на карте — нет `relative` у обёртки iframe в `yandex-map-iframe.tsx`  
- Панель без стилей — не добавили `dtp-*` в `globals.css`  
- CORS — домен фронта в `CORS_ORIGINS`, перезапуск api  
- 401 — войти снова (сессия ~24 ч)  
- Нет событий после скрина — одинаковый `DTP_INTERNAL_API_KEY` в api и watchdog  
- Конфликт toast — у вас `hooks/use-toast.ts` и `ui/use-toast.ts`; для DTP используйте импорты как в скопированных `accident-notifications.tsx` и `notification-drawer.tsx`  

---

## Эталоны в DTP_Akaito

- `frontend/components/notification-icon.tsx`, `notification-drawer.tsx`  
- `frontend/contexts/`, `frontend/hooks/accident-notifications.tsx`  
- `frontend/app/login/page.tsx`, `app/layout.tsx` (провайдеры)  
- `compose.yaml`, `docker/README.md`, `.env.example`  

Сначала поднимите стек в чистом DTP_Akaito (`docker compose up`), затем повторите те же шаги у себя в traffic_krasnodar.
