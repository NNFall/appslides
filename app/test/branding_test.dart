import 'package:appslides/core/config/app_config.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('uses App Store product title as app name', () {
    expect(AppConfig.appName, 'Slide AI: PPTX & PDF Maker');
  });
}
