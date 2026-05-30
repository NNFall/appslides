# AppSlides: research по публикации в App Store

Дата: 2026-05-29

Статус: исследование. Работу по iOS/App Store пока не начинаем, пока не закрыта текущая Google Play-ветка.

## Короткий вывод

Технически приложение на Flutter можно вывести в App Store, но финальная iOS-сборка, подпись и загрузка в App Store Connect требуют macOS + Xcode. С Windows можно продолжать писать код, backend и Flutter UI, но `.ipa` для TestFlight/App Store на Windows штатно не собрать.

Рекомендованный путь для нас:

1. Закончить Google Play-версию.
2. Подготовить отдельную iOS-ветку.
3. Взять временный Mac-доступ или CI с macOS.
4. Перевести платежи iOS на Apple In-App Purchase.
5. Собрать `.ipa`, загрузить в TestFlight, протестировать подписки в Sandbox.
6. После тестов подавать в App Review.

## Что можно делать на Windows

- Редактировать Flutter-код.
- Редактировать backend.
- Готовить тексты, скриншоты, описание, privacy policy.
- Настраивать App Store Connect через браузер.
- Готовить документы, product IDs, тарифы, server API endpoints.
- Делать Android/Google Play сборки.

## Что нельзя полноценно сделать на Windows

- Собрать подписанный iOS `.ipa`.
- Запустить Xcode.
- Запустить iOS Simulator.
- Сделать Xcode Archive.
- Настроить automatic signing через Xcode локально.
- Загрузить build в App Store Connect через Transporter/Xcode с Windows.

Flutter официально указывает, что iOS release-сборка идет через `flutter build ipa`, Xcode archive и загрузку через Transporter, `xcrun altool` или Xcode. Эти инструменты относятся к macOS/Xcode.

## Варианты инфраструктуры для iOS-сборки

### Простыми словами: Xcode, TestFlight и как выглядят платформы

**Xcode** - это официальная программа Apple для сборки iOS-приложений. В нашем случае основной код остается Flutter, но финальный iPhone-билд все равно проходит через Xcode-инструменты: iOS SDK, подпись сертификатами, `Archive`, проверка Bundle ID, provisioning profile и загрузка в App Store Connect. Обычно на Mac открывают `app/ios/Runner.xcworkspace`, выбирают Apple Team, чинят signing, после этого собирают `flutter build ipa` или делают `Archive` прямо в Xcode.

**TestFlight** - это официальный тестовый канал Apple внутри App Store Connect. Мы загружаем подписанный `.ipa` в App Store Connect, после обработки build появляется в TestFlight. Внутренние тестировщики ставят приложение почти сразу, внешние тестировщики обычно проходят beta review от Apple. Это не отдельный магазин, а промежуточный этап перед публикацией в App Store.

**Что нужно для подписи и загрузки**:

- Apple Developer Program, сейчас $99/год.
- Доступ в App Store Connect.
- Bundle ID приложения.
- Apple Team ID.
- Сертификаты и provisioning profiles или automatic signing через Xcode.
- Для CI, например Codemagic: App Store Connect API Key (`issuer id`, `key id`, `.p8`) и signing assets, сохраненные как secrets.

**Ручной сценарий через удаленный Mac** выглядит так: арендуем Mac, подключаемся к рабочему столу macOS, ставим/проверяем Xcode, Flutter, CocoaPods, подтягиваем GitHub-репозиторий, собираем `.ipa`, загружаем build через Xcode/Transporter. Это похоже на обычную работу за Mac, только Mac находится в облаке.

**Автоматический сценарий через CI** выглядит иначе: рабочего стола macOS нет. Мы подключаем GitHub к сервису сборок, кладем секреты, описываем workflow, нажимаем `Start build` или пушим commit. Сервис сам поднимает macOS runner, собирает `.ipa`, сохраняет артефакт и может сам отправить build в TestFlight. С Windows вручную собрать `.ipa` нельзя, но можно из браузера запускать CI и смотреть логи.

#### MacInCloud

Что это: облачный Mac с удаленным доступом. По ощущениям это ближе всего к обычному серверу с macOS и графическим рабочим столом: подключились, открыли Xcode, терминал, браузер, Transporter и работаете руками.

Как будет выглядеть работа:

- покупаем временный доступ;
- заходим на удаленный Mac;
- подтягиваем проект из GitHub;
- запускаем `flutter doctor`, `pod install`, `flutter build ipa`;
- открываем Xcode/Transporter, логинимся в Apple аккаунт или используем ключи;
- загружаем build в TestFlight.

По ценам на текущей странице Pay-As-You-Go:

- 25 часов: $25;
- 50 часов: $50;
- 100 часов: $100;
- 7 дней: $28;
- 14 дней: $56;
- 30 дней: $120.

Важное ограничение: на managed Pay-As-You-Go обычно нет admin/root-доступа. Для полного контроля нужен Dedicated Server Plan. Итоговая цена может меняться от выбранного региона, железа, RAM, SSH/Remote Build Port и других add-ons. Для первого ручного TestFlight-прогона это самый понятный вариант.

#### MacStadium

Что это: аренда выделенного Mac mini или Mac Studio в дата-центре. Это не “сайт для сборки”, а полноценная постоянная машина Apple, к которой можно подключаться удаленно и держать окружение сколько нужно.

Как будет выглядеть работа:

- арендуем конкретный Mac mini/Mac Studio;
- настраиваем Xcode, Flutter, сертификаты;
- либо собираем руками, либо ставим свой CI runner;
- окружение остается постоянным между сборками.

Текущие месячные цены на pricing-странице:

- Mac mini M2.S: $109/месяц;
- Mac mini M4.S: $119/месяц;
- Mac mini M2.M: $199/месяц;
- Mac mini M4.M: $199/месяц;
- Mac mini M2.L: $249/месяц;
- Mac mini M4.L: $299/месяц;
- Mac mini M2.XL: $349/месяц;
- Mac mini M4.XL: $399/месяц;
- Mac Studio S1.M: $249/месяц;
- Mac Studio S2.M: $369/месяц;
- Mac Studio S2.L: $449/месяц.

MacStadium больше подходит, когда iOS становится постоянным направлением и нужно регулярно собирать, тестировать и хранить стабильную среду. Для пары первых билдов это обычно избыточно.

#### Codemagic

Что это: CI/CD-сервис для мобильных приложений, особенно удобный для Flutter. Рабочего стола macOS там нет: мы не “заходим на Mac”, а запускаем сборку через сайт или по push в GitHub. Результат - `.ipa`-файл, логи, артефакты и, при настройке, автоматическая отправка в TestFlight.

Как будет выглядеть работа:

- подключаем GitHub-репозиторий;
- добавляем `codemagic.yaml`;
- загружаем Apple signing secrets и App Store Connect API key;
- запускаем build вручную или автоматически;
- Codemagic собирает `.ipa`;
- build можно скачать руками или автоматически отправить в TestFlight.

Текущие цены:

- individual tier: 500 бесплатных macOS M2 минут в месяц;
- Mac mini M2: $0.095/минута;
- Mac mini M4: $0.114/минута;
- Linux X2 и Windows: $0.045/минута;
- дополнительная параллельная сборка: $49/concurrency;
- fixed annual M2: $3,990/год;
- fixed annual M4: $5,400/год;
- fixed annual M4 Max: $9,000/год.

Цены указаны без налогов. Для первых тестов Codemagic может быть самым дешевым вариантом, если хватит бесплатных 500 минут. Минус: первую настройку signing и App Store Connect API придется сделать аккуратно, потому что ошибки видны только в логах, без ручного Xcode-интерфейса.

#### Что выбрать практически

Для первого iOS-прогона я бы выбрал один из двух путей:

- MacInCloud, если нужно руками увидеть Xcode, signing, Transporter и быстро разобраться с первыми ошибками.
- Codemagic, если хотим сразу сделать повторяемую сборку: commit -> build -> TestFlight.

MacStadium сейчас не нужен, пока нет постоянного iOS-потока. Он имеет смысл позже, если iOS станет регулярным направлением и будет выгоднее держать свой постоянный Mac в облаке.

### Вариант 1. Арендованный Mac, например MacInCloud

Схема:

- арендовать macOS-доступ;
- установить/использовать Xcode, Flutter, CocoaPods;
- подтянуть репозиторий;
- открыть `app/ios/Runner.xcworkspace`;
- настроить Team ID/signing;
- собрать `flutter build ipa`;
- загрузить через Transporter или Xcode.

Плюсы:

- максимально похоже на обычную разработку на Mac;
- удобно вручную пройти первые ошибки Xcode/signing;
- можно открыть симулятор, Xcode, Transporter.

Минусы:

- нужна зарубежная карта или другой способ оплаты;
- доступы Apple Developer/App Store Connect придется вводить на удаленной машине;
- надо аккуратно работать с сертификатами и ключами;
- ручной процесс, сложнее повторять регулярно.

Вывод: хороший вариант для первого TestFlight-релиза, если нет своего Mac.

### Вариант 2. Codemagic или другой Flutter CI

Схема:

- подключить GitHub-репозиторий;
- загрузить signing assets или подключить App Store Connect API;
- настроить `codemagic.yaml`;
- CI сам собирает `.ipa` и может загрузить в TestFlight.

Плюсы:

- хорошо подходит для Flutter;
- не нужно вручную держать Mac;
- повторяемый процесс сборки;
- можно автоматизировать номер build и upload.

Минусы:

- первый setup signing/App Store Connect может занять время;
- нужно доверять CI секреты;
- если нужно вручную debug-ить Xcode, удаленный Mac удобнее.

Codemagic на момент research показывает free tier с 500 macOS M2 минутами в месяц для individual и pay-as-you-go для macOS M2/M4 минут. Этого может хватить на первые сборки, если не делать десятки билдов подряд.

Вывод: лучший долгосрочный вариант после первого ручного прогона.

### Вариант 3. MacStadium

Схема: выделенный Mac mini/Mac Studio в облаке.

Плюсы:

- полноценный выделенный Mac;
- стабильнее для постоянной команды/CI;
- можно держать окружение постоянно.

Минусы:

- дороже для нашего текущего этапа;
- на странице pricing Mac mini начинается примерно от $109/месяц;
- избыточно, если нужно только несколько iOS-релизов.

Вывод: пока не нужно, если нет постоянного iOS-потока.

### Вариант 4. Физический Mac mini

Плюсы:

- один раз купили и всегда есть;
- безопаснее для Apple-аккаунтов и сертификатов;
- удобно для ручного Xcode debug.

Минусы:

- дороже на старте;
- нужно физически настраивать/обслуживать.

Вывод: имеет смысл, если проект будет активно поддерживаться на iOS.

## Что нужно от заказчика/владельца

Минимум:

- Apple Developer Program аккаунт, $99/год.
- Доступ в App Store Connect.
- Bundle ID, например `com.appslides.slideai` или другой финальный.
- App Store app record.
- Privacy Policy URL.
- Support URL.
- Marketing URL, если есть.
- Юридическое имя/компания для Apple.
- Банковские и налоговые настройки в App Store Connect.
- Решение по странам публикации.
- Решение по ценам подписок.
- Тестовые Apple ID для Sandbox/TestFlight.

Для сборки:

- Apple Team ID.
- App Store Connect API Key: issuer ID, key ID, `.p8` key.
- Signing certificate/provisioning profile, если не используем automatic signing.

Для backend-проверки подписок:

- App Store Server API key: issuer ID, key ID, private `.p8`.
- Bundle ID.
- Environment: Sandbox/Production.
- App Store Server Notifications V2 URL после реализации endpoint.

## Текущее состояние PMappslides

Актуально для папки `PMappslides`, не для старого `appslides`.

- Flutter-приложение уже содержит `in_app_purchase` в `app/pubspec.yaml`.
- Android/Google Play product IDs сейчас:
  - `slide_ai_week`
  - `slide_ai_month`
- Backend уже умеет Google Play verification через Google Play Developer API.
- iOS-папка есть: `app/ios`.
- Текущий iOS bundle id в Xcode project: `com.appslides.appslides`.
- Нужно решить финальный iOS bundle id. Логичнее использовать `com.appslides.slideai`, если он свободен в Apple Developer.
- iOS-specific StoreKit flow для Apple подписок еще нужно проверить и доработать.
- Backend App Store Server API verification еще не реализован.
- App Store Server Notifications V2 endpoint еще не реализован.

## Что надо будет поменять в приложении для App Store

### Платежи

Apple почти наверняка потребует In-App Purchase для подписок, потому что приложение продает цифровую функциональность: генерации, экспорт файлов, доступ к AI-сервису. ЮKassa или внешняя оплата внутри iOS-приложения для этого сценария будет высоким риском отказа.

Нужно:

- оставить Google Play Billing для Android;
- добавить/проверить StoreKit/In-App Purchase flow для iOS;
- сделать provider switch:
  - Android: `google_play`;
  - iOS: `app_store`;
  - RuStore build: `yookassa`, если отдельная ветка/сборка.

### Product IDs

Рекомендованные iOS product IDs:

```text
slide_ai_week
slide_ai_month
```

Можно использовать те же ID, что и в Google Play, но это отдельные продукты в App Store Connect.

Рекомендованная subscription group:

```text
Slide AI Subscriptions
```

Тарифы:

- Weekly Subscription: 10 generations / week.
- Monthly Subscription: 50 generations / month.

### Restore purchases

На iOS нужна явная возможность восстановить покупки. Это требование пользовательского опыта и частый пункт review.

В интерфейсе нужно добавить кнопку:

```text
Restore purchases
```

Логика:

- приложение вызывает StoreKit restore;
- получает активные транзакции;
- отправляет transaction data/backend token на backend;
- backend восстанавливает entitlement для текущего `client_id`.

### Account / client_id

Сейчас учет в приложении идет через локальный `client_id`, без регистрации.

Для iOS это допустимо, если:

- нет аккаунта, который пользователь создает через email/телефон;
- подписка восстанавливается через Apple purchase history;
- есть понятная поддержка, как перенести/восстановить доступ.

Риск:

- если пользователь удалит приложение и `client_id` потеряется, backend должен восстановить доступ по Apple original transaction ID.

Что нужно в backend:

- хранить `originalTransactionId`;
- уметь связывать восстановленную покупку с новым `client_id`;
- не выдавать бесконечные дубли, а переносить entitlement.

## Что надо будет поменять в backend

Добавить App Store provider рядом с Google Play:

```text
/v1/billing/app-store/verify
/v1/billing/app-store/restore
/v1/billing/app-store/notifications
```

Хранить:

- provider: `app_store`;
- product_id;
- transaction_id;
- original_transaction_id;
- web_order_line_item_id, если нужен;
- environment: `Sandbox` / `Production`;
- expires_at;
- revocation/refund status;
- raw signed transaction, если нужно для аудита;
- client_id;
- purchase token / signed JWS identifier.

Проверка:

- backend получает транзакцию/receipt/JWS от приложения;
- проверяет через App Store Server API;
- сверяет bundle id и product id;
- проверяет expiration/revocation;
- выдает лимит генераций.

Notifications:

- Apple Server Notifications V2 будут сообщать о продлениях, отменах, billing retry, refund, expiration.
- Endpoint должен отвечать HTTP 200-206 при успешной обработке.
- Нужно idempotency, чтобы повторные уведомления не начисляли токены дважды.

## App Store Review: основные риски

### Внешняя оплата

Высокий риск отказа, если в iOS-приложении будет ЮKassa или ссылка на оплату цифровой подписки вне Apple IAP.

Решение: для App Store build показывать только Apple In-App Purchase.

### AI/нейросети

Нужно раскрыть:

- пользователь вводит темы/пожелания;
- данные отправляются на backend и внешние AI-сервисы;
- файлы могут загружаться для конвертации;
- результат генерируется автоматически.

Нужно privacy policy, где это описано.

### User-generated content

Если нет публичной ленты/сообщества/публикаций, риск ниже. Если пользователь только создает личные презентации, moderation/report/block обычно не нужны.

### Account deletion

Если аккаунтов нет, отдельная account deletion flow может не требоваться. Но privacy policy должна объяснять, как удалить локальные данные и как запросить удаление серверных данных по `client_id`.

### Restore purchases

Нужно реализовать для iOS.

### Review notes

В App Review notes надо прямо написать:

- приложение создает презентации по теме пользователя;
- подписки открывают лимит AI-генераций;
- тестовый аккаунт не нужен, если нет регистрации;
- как открыть экран подписки;
- что использовать Sandbox purchase.

## App Store metadata

Нужно подготовить:

- App Name.
- Subtitle.
- Description.
- Keywords.
- Promotional text.
- Privacy Policy URL.
- Support URL.
- Category: Productivity или Education.
- Age rating.
- Screenshots для iPhone.
- Screenshots для iPad, если iPad поддерживается.
- App icon 1024x1024.
- Copyright.
- Review contact.
- Review notes.
- Subscription display names/descriptions.
- Subscription review screenshot.

Черновик названия:

```text
Slide AI: PPTX PDF Maker
```

Черновик subtitle:

```text
Create AI presentations fast
```

Черновик keywords:

```text
presentation,slides,pptx,pdf,ai,school,business,converter
```

## Черновики подписок для App Store

Subscription group display name:

```text
Slide AI Subscriptions
```

Weekly display name:

```text
Weekly Subscription
```

Weekly description:

```text
Includes 10 AI presentation generations per week, PPTX and PDF export, presentation templates, and file conversion tools.
```

Monthly display name:

```text
Monthly Subscription
```

Monthly description:

```text
Includes 50 AI presentation generations per month, PPTX and PDF export, presentation templates, and file conversion tools.
```

## Рекомендуемый рабочий план, когда начнем

### Этап 1. Apple account и App Store Connect

1. Оформить Apple Developer Program.
2. Создать Bundle ID.
3. Создать App Store app record.
4. Настроить Agreements, Tax and Banking.
5. Создать subscription group.
6. Создать `slide_ai_week` и `slide_ai_month`.
7. Создать Sandbox testers.

### Этап 2. Mac build environment

1. Выбрать MacInCloud/Codemagic/физический Mac.
2. Установить Xcode, Flutter, CocoaPods.
3. Подтянуть repo.
4. Проверить `flutter doctor`.
5. Запустить `flutter build ios --release --no-codesign`.
6. Настроить signing.
7. Собрать `flutter build ipa`.

### Этап 3. iOS billing

1. Добавить provider `app_store` в backend.
2. Добавить App Store verification endpoint.
3. Добавить StoreKit purchase/restore в Flutter.
4. Добавить App Store Server Notifications V2.
5. Покрыть тестами:
   - первая покупка;
   - restore;
   - renewal;
   - cancellation;
   - refund/revocation;
   - повторные уведомления.

### Этап 4. TestFlight

1. Загрузить первый build.
2. Дождаться обработки.
3. Добавить Internal Testers.
4. Проверить Sandbox-покупку.
5. Проверить restore после удаления приложения.
6. Проверить генерацию после покупки.
7. Проверить server notifications.

### Этап 5. Review

1. Заполнить metadata.
2. Заполнить privacy.
3. Добавить screenshots.
4. Приложить подписки к первой версии.
5. Написать review notes.
6. Отправить на review.

## Рекомендация по выбору Mac/CI

Для первого релиза я бы выбрал один из двух путей:

1. MacInCloud/арендованный Mac на короткий срок, чтобы руками пройти Xcode/signing/TestFlight.
2. Codemagic, если хотим сразу автоматизировать сборки и не вводить Apple ID на удаленном desktop.

Практически:

- если нужна скорость и ручной контроль: MacInCloud;
- если нужна повторяемость и меньше ручных действий: Codemagic;
- если iOS станет постоянным направлением: купить Mac mini или взять MacStadium.

## Открытые вопросы

- Финальный iOS Bundle ID: `com.appslides.slideai` или оставить `com.appslides.appslides`.
- Будет ли iPad поддерживаться или ограничиваемся iPhone.
- Какая страна/язык первой публикации.
- Цены в Apple tiers.
- Нужны ли one-time packs на iOS. Если да, Apple лучше делать consumable IAP, но это отдельная логика. Для MVP лучше только weekly/monthly auto-renewable subscriptions.
- Какую схему восстановления доступа выбираем без регистрации.
- Где будет privacy policy URL для App Store.

## Источники

- Flutter: Build and release an iOS app: https://docs.flutter.dev/deployment/ios
- Apple Xcode: https://developer.apple.com/xcode/
- Apple TestFlight: https://developer.apple.com/testflight/
- Apple: Upload builds: https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/
- Apple Developer Program: https://developer.apple.com/programs/
- Apple membership details: https://developer.apple.com/programs/whats-included/
- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Apple: Submit an In-App Purchase: https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-in-app-purchase/
- Apple: Offer auto-renewable subscriptions: https://developer.apple.com/help/app-store-connect/manage-subscriptions/offer-auto-renewable-subscriptions/
- Apple: App Store Server API: https://developer.apple.com/documentation/appstoreserverapi/
- Apple: App Store Server Notifications V2: https://developer.apple.com/documentation/appstoreservernotifications/app-store-server-notifications-v2
- Codemagic pricing: https://codemagic.io/pricing/
- Codemagic iOS CI/CD: https://codemagic.io/ios-continuous-integration
- MacStadium pricing: https://macstadium.com/pricing
- MacInCloud checkout/features: https://checkout.macincloud.com/select
- MacInCloud Pay-As-You-Go checkout: https://checkout.macincloud.com/select/payg
