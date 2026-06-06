# Чеклист публикации App Store

Документ описывает, что нужно сделать в App Store Connect, чтобы перейти от TestFlight к реальной публикации приложения `Slide AI: PPTX & PDF Maker`.

## 0. Проверь права

Для настройки подписок и отправки приложения нужны права не ниже `Account Holder`, `Admin` или `App Manager`.

Если у аккаунта только роль `Developer`, часть разделов In-App Purchase может быть доступна только для просмотра, без сохранения и отправки.

## 1. Прими платные соглашения Apple

Без платных соглашений подписки не выйдут в production.

Путь:

```text
App Store Connect -> Business -> Agreements
```

Проверь:

- `Paid Apps Agreement` принят.
- Banking заполнен.
- Tax forms заполнены.
- Нет красных или жёлтых предупреждений по договорам.

Это обязательно для In-App Purchases и подписок.

## 2. Проверь карточку приложения

Путь:

```text
Apps -> Slide AI: PPTX & PDF Maker
```

Открой `App Information` и проверь:

- Name: `Slide AI: PPTX & PDF Maker`
- Bundle ID: `com.appslides.slideai`
- Category: выбранная категория, например `Productivity` или `Education`
- Age Rating заполнен
- Privacy Policy URL заполнен
- Support URL заполнен
- Marketing URL можно оставить пустым, если он не нужен

## 3. Заполни App Privacy

Путь:

```text
Apps -> Slide AI: PPTX & PDF Maker -> App Privacy
```

Нужно честно заполнить ответы по данным, которые собирает приложение.

Что важно для нашего приложения:

- Приложение взаимодействует с backend.
- Есть анонимный `client_id` установки.
- Backend хранит данные подписки, лимиты генераций и историю серверных операций.
- Карточные данные Apple обрабатывает сама, мы их не видим.

Если Apple спрашивает про payment data, важно понимать: мы не собираем номер карты или банковские данные пользователя. Оплата проходит через Apple.

## 4. Проверь подписки

Путь:

```text
Apps -> Slide AI: PPTX & PDF Maker -> Monetization -> Subscriptions
```

Должны быть созданы:

- Subscription Group: `Slide AI Subscriptions`
- Product ID: `slide_ai_week`
- Product ID: `slide_ai_month`

### Weekly Subscription

Для `slide_ai_week` проверь:

- Duration: `1 week`
- Price point: примерно `$1.99`
- Display Name: `Weekly Subscription`
- Description: `10 presentation generations per week. Auto-renewable subscription.`
- Status: `Ready to Submit`

### Monthly Subscription

Для `slide_ai_month` проверь:

- Duration: `1 month`
- Price point: примерно `$4.99`
- Display Name: `Monthly Subscription`
- Description: `50 presentation generations per month. Auto-renewable subscription.`
- Status: `Ready to Submit`

### Цены и валюты

В App Store Connect задаётся price point. Apple сама показывает пользователю локальную валюту по региону Apple ID.

Например:

- для США пользователь увидит доллары;
- для Европы пользователь увидит евро;
- для российского или другого локального storefront Apple может показать локальную валюту, если она поддерживается для аккаунта.

Принудительно показывать всем пользователям одну валюту в системном окне Apple нельзя.

## 5. Добавь Review Information для подписок

В карточке каждой подписки заполни review information, если Apple просит.

Пример текста:

```text
The app offers AI-powered presentation generation. Users can create an outline, choose a template, and generate PPTX/PDF files.

The subscriptions unlock generation limits:
- Weekly Subscription: 10 presentation generations
- Monthly Subscription: 50 presentation generations

To test:
1. Open the app.
2. Tap Menu.
3. Tap Balance / Subscription.
4. Choose a subscription.
5. Complete the sandbox App Store purchase.
6. The app verifies the transaction with our backend and unlocks generations.
```

## 6. Прикрепи подписки к версии приложения

Для первой отправки подписок Apple обычно требует отправлять их вместе с новой версией приложения.

Путь:

```text
Apps -> Slide AI: PPTX & PDF Maker -> iOS version 0.1.0
```

На странице версии найди блок:

```text
In-App Purchases and Subscriptions
```

Нажми:

```text
Select In-App Purchases or Subscriptions
```

Выбери:

- `slide_ai_week`
- `slide_ai_month`

Нажми `Done`.

Если блока или кнопки нет, проверь:

- права аккаунта;
- статус подписок;
- принят ли `Paid Apps Agreement`;
- заполнены ли banking и tax forms.

## 7. Выбери build

Путь:

```text
Apps -> Slide AI: PPTX & PDF Maker -> iOS version 0.1.0
```

В блоке `Build` нажми `+` или `Add Build`.

Выбери:

```text
0.1.0 (27)
```

Build `27` нужен потому что в нём:

- новая красная иконка `Slide AI`;
- правильное название `Slide AI: PPTX & PDF Maker`;
- исправленная чистая iOS-сборка.

## 8. Заполни страницу версии

На странице версии приложения нужно заполнить публичные данные.

### Promotional Text

```text
Create AI-powered presentations and convert files in minutes.
```

### Description

```text
Slide AI helps you create presentations quickly using AI.

Enter a topic, choose the number of slides, review the outline, select a design template, and receive ready-to-use PPTX and PDF files.

The app also includes file conversion tools for PDF, DOCX, and PPTX workflows.

Subscriptions unlock presentation generation limits:
- Weekly subscription: 10 generations
- Monthly subscription: 50 generations

Payment is handled securely through the App Store. Subscriptions renew automatically unless canceled in Apple ID settings.
```

### Keywords

```text
presentation,slides,pptx,pdf,ai,converter,documents
```

### Copyright

```text
2026 Nexwit Ltd
```

### Screenshots

Нужно загрузить скриншоты приложения.

Минимально:

- iPhone screenshots обязательны;
- iPad screenshots могут понадобиться, если App Store Connect считает build совместимым с iPad.

Если Apple требует iPad screenshots, их нужно добавить или отдельно ограничивать приложение только iPhone в iOS-проекте.

## 9. Заполни App Review Information

На странице версии найди блок:

```text
App Review Information
```

Заполни:

- First name
- Last name
- Phone
- Email
- Notes

Пример notes:

```text
This app creates AI-generated presentations and converts files.

No login is required. The app identifies the installation with an anonymous client ID.

To test subscriptions:
1. Open the app.
2. Tap Menu.
3. Tap Balance / Subscription.
4. Select Weekly or Monthly Subscription.
5. Complete the sandbox purchase.
6. The app will verify the transaction and unlock generation limits.

The backend for this build is configured for App Store sandbox/TestFlight verification during review.
```

Если Apple просит demo account, укажи:

```text
No login required.
```

## 10. Export Compliance / Encryption

Если App Store Connect спрашивает про шифрование:

- приложение использует стандартный HTTPS/TLS для связи с backend;
- собственной криптографии мы не реализуем;
- используются стандартные механизмы операционной системы и сетевых библиотек.

Обычно выбирается вариант про стандартные алгоритмы шифрования, а не custom encryption.

Если появится отдельный вопрос про Францию или требование документации, нужно смотреть конкретный экран и выбирать аккуратно по формулировке Apple.

## 11. Добавь в Review и отправь

На странице версии нажми:

```text
Add for Review
```

Затем открой:

```text
Draft Submissions
```

Проверь, что в отправку попали:

- app version `0.1.0`;
- build `27`;
- подписка `slide_ai_week`;
- подписка `slide_ai_month`.

После проверки нажми:

```text
Submit for Review
```

После отправки статус станет `In Review`.

## 12. Backend перед production

Сейчас backend временно настроен для TestFlight:

```env
APP_STORE_ENVIRONMENT=sandbox
APP_STORE_TEST_MODE=1
```

Для реального App Store так оставлять нельзя.

Перед production нужно создать Apple In-App Purchase key.

Путь:

```text
Users and Access -> Integrations -> Keys -> In-App Purchase -> Generate In-App Purchase Key
```

После создания будут нужны:

- `Issuer ID`
- `Key ID`
- `.p8` private key file

После этого на backend нужно поставить:

```env
APP_STORE_TEST_MODE=0
APP_STORE_ENVIRONMENT=production
APP_STORE_ISSUER_ID=...
APP_STORE_KEY_ID=...
APP_STORE_PRIVATE_KEY_FILE=/data/appstore/AuthKey_....p8
```

`.p8` файл нельзя коммитить в git. Его нужно хранить только на сервере.

## 13. Что сделать прямо сейчас

1. Проверить `Business -> Agreements`, banking и tax.
2. Довести `slide_ai_week` и `slide_ai_month` до `Ready to Submit`.
3. На странице версии `0.1.0` прикрепить build `27`.
4. На странице версии `0.1.0` прикрепить обе подписки.
5. Заполнить screenshots, description, privacy и review info.
6. Нажать `Add for Review`.
7. Проверить `Draft Submissions`.
8. Нажать `Submit for Review`.

## Полезные ссылки Apple

- [Submit an app](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app)
- [Choose a build to submit](https://developer.apple.com/help/app-store-connect/manage-builds/choose-a-build-to-submit/)
- [Submit an In-App Purchase](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-in-app-purchase)
- [Set a price for an In-App Purchase](https://developer.apple.com/help/app-store-connect/manage-in-app-purchases/set-a-price-for-an-in-app-purchase/)
- [App privacy details](https://developer.apple.com/app-store/app-privacy-details/)
