# iOS / App Store Build Status

Дата обновления: 2026-06-04

## Текущий результат

Подписанный App Store IPA успешно собран на MacInCloud.

Финальный локальный артефакт после скачивания с Mac:

```text
build_artifacts/ios/SlideAI_build_24.ipa
```

Размер:

```text
24,974,191 bytes
```

SHA-256:

```text
43ddfee6298964ed7b4998dadce385566ad1dd2327e4919673616565c0031ed0
```

Параметры сборки:

- macOS: `26.3.1`
- Xcode: `26.5`
- Flutter: `3.44.1`
- CocoaPods: `1.15.2`, установлен локально в user gem-папку без `sudo`
- Проект на Mac: `~/ASappslides`
- Ветка: `codex/app-store-prep`
- iOS bundle id: `com.appslides.slideai`
- Team ID: `WH73RJDJXC`
- Provisioning profile: `Macin`
- Export method: `app-store-connect`
- Build number: `24`
- Backend для iOS/App Store: `http://185.171.83.116:8031`
- Billing provider для iOS: `app_store`
- Product IDs: `slide_ai_week`, `slide_ai_month`

## Что было исправлено

Сначала `flutter build ipa` падал на подписи:

```text
errSecInternalComponent
User interaction is not allowed
```

Причина была не в Flutter и не в provisioning profile. Через SSH `codesign` не мог получить доступ к приватному ключу сертификата `Apple Distribution: Nexwit ltd (WH73RJDJXC)` в `login.keychain-db`.

Проверка корня проблемы:

```bash
codesign --force --sign "Apple Distribution: Nexwit ltd (WH73RJDJXC)" test.sh
```

До исправления простой тест подписи падал с `errSecInternalComponent`.

Исправление на Mac:

```bash
security unlock-keychain -p '<MAC_PASSWORD>' "$HOME/Library/Keychains/login.keychain-db"
security set-keychain-settings -lut 21600 "$HOME/Library/Keychains/login.keychain-db"
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k '<MAC_PASSWORD>' "$HOME/Library/Keychains/login.keychain-db"
```

После этого минимальный `codesign` стал проходить, и Xcode смог собрать архив.

Второй сбой был уже на экспорте:

```text
exportArchive "Runner.app" requires a provisioning profile
```

Архив был подписан правильно и содержал `embedded.mobileprovision`, но Flutter/Xcode не получил явное соответствие bundle id -> provisioning profile на этапе exportArchive. Поэтому сборочный скрипт теперь создает `ExportOptions.plist` вручную и передает его во Flutter через `--export-options-plist`.

## Команда для следующей подписанной сборки

На MacInCloud:

```bash
cd ~/ASappslides
MAC_KEYCHAIN_PASSWORD='<MAC_PASSWORD>' \
BUILD_SIGNED_IPA=1 \
BUILD_NUMBER=<NEXT_BUILD_NUMBER> \
./scripts/macos/build_ios_app_store.sh
```

Важно: `BUILD_NUMBER` всегда должен быть больше предыдущего загруженного билда в App Store Connect.

Ожидаемый файл:

```text
app/build/ios/ipa/*.ipa
```

## Проверенные команды

На MacInCloud успешно выполнено:

```bash
flutter build ipa --release \
  --build-number=24 \
  --export-options-plist=build/ios/AppStoreExportOptions.plist \
  --dart-define=APPSLIDES_BACKEND_BASE_URL=http://185.171.83.116:8031 \
  --dart-define=APPSLIDES_BILLING_PROVIDER=app_store \
  --dart-define=APPSLIDES_APP_STORE_WEEK_PRODUCT_ID=slide_ai_week \
  --dart-define=APPSLIDES_APP_STORE_MONTH_PRODUCT_ID=slide_ai_month
```

Также ранее успешно проходили:

```bash
flutter analyze
flutter test
flutter build ios --release --no-codesign
flutter build ios --simulator --debug
```

Локальные проверки Windows-проекта:

```bash
python -m pytest scripts/tests -q
python -m pytest backend/tests -q
python scripts/validate_ios_privacy_manifest.py
```

## Замечания

- Android SDK на Mac не нужен для iOS/App Store сборки.
- `open_filex` пока не поддерживает Swift Package Manager для iOS. Сейчас это предупреждение Flutter, не ошибка.
- Xcode предупреждает, что в будущем часть StoreKit 1 API будет deprecated. Текущая сборка проходит, но позже может потребоваться обновление `in_app_purchase_storekit`.
- Flutter показывает предупреждение, что iOS app icon и launch image похожи на placeholder. Для реальной модерации App Store желательно отдельно проверить иконку и launch screen.
