import 'package:appslides/core/config/app_config.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('backend base URL can be overridden at build time', () {
    const expectedBackendBaseUrl = String.fromEnvironment(
      'EXPECTED_BACKEND_BASE_URL',
      defaultValue: 'http://185.171.83.116:8021',
    );

    expect(AppConfig.defaultBackendBaseUrl, expectedBackendBaseUrl);
  });

  test('App Store product ids mirror subscription plan keys', () {
    expect(AppConfig.appStoreProductIdForPlan('week'), 'slide_ai_week');
    expect(AppConfig.appStoreProductIdForPlan('month'), 'slide_ai_month');
    expect(AppConfig.appStoreProductIdForPlan('one10'), isNull);
  });

  test('default build still uses native Google Play billing provider', () {
    expect(AppConfig.useGooglePlayBilling, isTrue);
    expect(AppConfig.useAppStoreBilling, isFalse);
    expect(AppConfig.useNativeStoreBilling, isTrue);
  });
}
