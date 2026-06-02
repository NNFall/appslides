# iOS / App Store Build Status

Дата: 2026-06-02

## Текущий результат

MacInCloud SSH-доступ работает.

Проверенное окружение Mac:

- macOS: `26.3.1`
- Xcode: `26.5`
- Flutter: `3.44.1`
- CocoaPods: `1.15.2`, установлен локально в user gem-папку без `sudo`
- Проект на Mac: `~/ASappslides`
- Ветка: `codex/app-store-prep`
- iOS bundle id: `com.appslides.slideai`
- Backend для iOS/App Store: `http://185.171.83.116:8031`
- Billing provider для iOS: `app_store`
- Product IDs: `slide_ai_week`, `slide_ai_month`

## Что прошло

На MacInCloud успешно выполнены:

```bash
flutter analyze
flutter test
flutter build ios --release --no-codesign \
  --dart-define=APPSLIDES_BACKEND_BASE_URL=http://185.171.83.116:8031 \
  --dart-define=APPSLIDES_BILLING_PROVIDER=app_store \
  --dart-define=APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week \
  --dart-define=APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month
```

Результат:

```text
Built build/ios/iphoneos/Runner.app (29.5MB)
```

Локально скачан unsigned artifact:

```text
build_artifacts/ios/Runner_unsigned_no_codesign.app.zip
```

SHA-256:

```text
a65d3b36dbd5152a2694ceba4f5b838a80b8ac2700928231d161a78f5932e39c
```

Важно: это не App Store `.ipa`. Это unsigned iOS `.app`-сборка для проверки компиляции. Для TestFlight/App Store нужен подписанный `.ipa`.

## Что не прошло

Полная команда:

```bash
flutter build ipa --release
```

остановилась на signing:

```text
No valid code signing certificates were found
No development certificates available to code sign app for device deployment
```

Причина: на MacInCloud пока не настроены Apple Developer certificate, provisioning profile и Team в Xcode для `com.appslides.slideai`.

## Следующие шаги для подписанного IPA

1. На MacInCloud открыть проект в Xcode:

```bash
cd ~/ASappslides/app
open ios/Runner.xcworkspace
```

2. В Xcode войти в Apple ID:

```text
Xcode -> Settings -> Accounts -> Add Apple ID
```

3. Открыть:

```text
Runner project -> Runner target -> Signing & Capabilities
```

4. Установить:

```text
Bundle Identifier: com.appslides.slideai
Team: Apple Developer team владельца приложения
Automatically manage signing: enabled
```

5. Убедиться, что в Apple Developer / App Store Connect существует App ID / Bundle ID:

```text
com.appslides.slideai
```

6. После настройки signing запустить:

```bash
cd ~/ASappslides
BUILD_SIGNED_IPA=1 BUILD_NUMBER=<NEXT_BUILD_NUMBER> ./scripts/macos/build_ios_app_store.sh
```

Ожидаемый файл после успешной подписи:

```text
app/build/ios/ipa/*.ipa
```

## Замечания

- Android SDK на Mac не установлен, но для iOS/App Store сборки это не блокер.
- `flutter doctor` предупреждает, что CocoaPods `1.15.2` старее рекомендованной `1.16.2`. На текущем MacInCloud без `sudo` используется Ruby `2.6`, поэтому CocoaPods установлен в максимально совместимом user-local режиме.
- `open_filex` пока не поддерживает Swift Package Manager для iOS. Сейчас это предупреждение Flutter, не ошибка. В будущих версиях Flutter это может стать ошибкой, тогда нужно будет обновлять зависимость или оставаться на CocoaPods-интеграции.
