# AppSlides App Store Track

## Codemagic iOS/TestFlight scaffold

The repository root contains a safe `codemagic.yaml` scaffold for a signed Flutter iOS IPA build. It is intentionally configured with placeholder Codemagic groups only:

- `codemagic_app_store_connect`
- `codemagic_ios_signing`

Do not commit real Apple secrets. Configure these values in Codemagic UI as encrypted variables or signing assets:

- `APP_STORE_CONNECT_PRIVATE_KEY`
- `APP_STORE_CONNECT_KEY_IDENTIFIER`
- `APP_STORE_CONNECT_ISSUER_ID`
- Apple Distribution certificate and provisioning profile/signing access for `com.appslides.slideai`

The workflow builds from `app/`, runs `flutter analyze` and `flutter test`, uses `APPSLIDES_BILLING_PROVIDER=app_store`, and passes the Codemagic build number into the iOS build. `submit_to_testflight` and `submit_to_app_store` are both false until the App Store Connect record, signing, privacy URLs, screenshots, and review metadata are ready.

The App Store build also exposes a visible **Restore App Store purchase** action in the balance/subscription chat screen. It calls StoreKit restore, verifies the restored transaction on the backend, and refreshes the local entitlement state.

The iOS project includes `app/ios/Runner/PrivacyInfo.xcprivacy` and a local validator:

```powershell
python scripts\validate_ios_privacy_manifest.py
```

This covers the App Store privacy manifest file required by Apple for required-reason APIs used by app-local preferences and local files. App Store Connect privacy labels are filled separately in the Apple web console.

Эта копия проекта находится в `ASappslides` и готовится как отдельный App Store/TestFlight track.

Главное отличие от Android/Google Play версии:

- iOS Bundle ID: `com.appslides.slideai`;
- имя приложения на устройстве: `Slide AI`;
- iOS-подписки должны идти через Apple In-App Purchase / StoreKit;
- backend получает отдельные App Store endpoints: `/v1/billing/app-store/verify`, `/restore`, `/notifications`;
- Apple ключи, Team ID и signing не хранятся в репозитории и понадобятся только на этапе TestFlight/upload;
- финальная `.ipa` сборка требует macOS + Xcode, MacInCloud или CI вроде Codemagic.

Текущий статус App Store подготовки:

- Flutter iOS shell приведён к App Store Bundle ID.
- Добавлен iOS `Podfile` для CocoaPods/Flutter plugins.
- В клиент добавлен billing-provider split: `google_play` для Android и `app_store` для iOS.
- В backend добавлен testable App Store billing skeleton и env-настройки для будущей App Store Server API verification.
- Локальная Windows-разработка может проверять Dart/Python код, но не может собрать финальный подписанный `.ipa`.

Мобильное приложение и backend-сервис для создания презентаций в формате чат-бота.

`AppSlides` делает генерацию презентаций простой для обычного пользователя: человек пишет тему, выбирает количество слайдов и стиль, а приложение собирает готовые файлы `PPTX` и `PDF`. Весь сценарий выглядит как диалог в Telegram-боте, но работает внутри отдельного Android-приложения с собственным backend.

## Что умеет проект

- Генерировать презентации по теме и пожеланиям пользователя.
- Предлагать план будущей презентации перед сборкой.
- Давать выбор из нескольких шаблонов оформления.
- Собирать готовые `PPTX` и `PDF`.
- Конвертировать файлы между `PDF`, `DOCX` и `PPTX`.
- Показывать историю переписки прямо в приложении.
- Сохранять историю чата локально на устройстве между перезапусками.
- Работать с подписками через native store billing: Google Play для Android и Apple In-App Purchase для iOS/App Store track.

## Как это выглядит

### Главный экран

![Главный экран AppSlides](docs/images/readme_home.png)

### Сценарий создания презентации

![Выбор количества слайдов](docs/images/readme_generation_step.png)

### Подписка

![Экран подписки YooKassa](docs/images/readme_subscription.png)

## Как это работает

1. Пользователь открывает приложение и попадает в единое окно чата.
2. Нажимает `Создать презентацию` или просто пишет тему текстом.
3. Приложение уточняет количество слайдов и собирает план.
4. Пользователь подтверждает план или редактирует его.
5. Выбирает шаблон оформления.
6. Backend собирает презентацию и возвращает готовые файлы.
7. Файлы можно открыть на устройстве, а история диалога остаётся в приложении.

## Почему формат чата

Вместо сложного интерфейса с вкладками и формами проект специально сделан как чат:

- пользователю проще понимать следующий шаг;
- диалог похож на привычный Telegram-бот;
- в одной ленте видны сообщения, действия, файлы и статусы;
- такой интерфейс хорошо подходит для MVP и быстрых итераций.

## Из чего состоит проект

### `app/`

Flutter-приложение для Android/iOS.
Именно здесь находится интерфейс чата, локальная история, работа с файлами и взаимодействие с backend.

### `backend/`

Python backend на `FastAPI`.  
Он отвечает за генерацию контента, сборку презентаций, конвертацию файлов, проверку подписок и выдачу артефактов приложению.

### `telegrambot/`

Исходная рабочая база Telegram-бота, на основе которой проект был перенесён в формат мобильного приложения.

## Текущее состояние

Сейчас проект уже умеет:

- работать как реальное Android-приложение;
- подключаться к удалённому backend на сервере;
- генерировать презентации и собирать файлы;
- показывать и восстанавливать чат после перезапуска приложения;
- работать с подпиской через store billing в зависимости от сборки;
- использовать реальные шаблоны презентаций на backend.

## Для кого это

`AppSlides` подходит для сценариев, где нужно быстро получить аккуратную презентацию без ручной верстки:

- учёба;
- выступления;
- отчёты;
- простые коммерческие презентации;
- быстрые черновики для дальнейшей доработки.

## Что дальше

План развития проекта:

- дальнейшая доводка chat UX;
- улучшение визуального стиля и шаблонов;
- push-уведомления о готовности презентации;
- развитие системы подписок;
- дополнительные шаблоны и сценарии генерации;
- публикация и эксплуатация как полноценного мобильного продукта.

## Статус репозитория

Репозиторий содержит полный рабочий контур:

- Flutter-клиент;
- backend;
- docker-deploy на сервер;
- рабочие шаблоны презентаций;
- документацию по разработке и эксплуатации.

---

Если нужен технический уровень описания, смотри отдельные документы в [app/README.md](app/README.md), [backend/README.md](backend/README.md), [APPSLIDES_PLAN.md](APPSLIDES_PLAN.md) и [OPERATIONS.md](OPERATIONS.md).
