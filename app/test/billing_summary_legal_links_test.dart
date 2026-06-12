import 'package:appslides/core/config/app_config.dart';
import 'package:appslides/domain/models/billing_summary.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses legal links from backend billing summary', () {
    final summary = BillingSummary.fromJson(_summaryJson(
      privacyPolicyUrl: 'https://example.com/privacy',
      termsOfUseUrl: 'https://example.com/eula',
    ));

    expect(summary.privacyPolicyUrl, 'https://example.com/privacy');
    expect(summary.termsOfUseUrl, 'https://example.com/eula');
  });

  test('falls back to built-in legal links when backend omits them', () {
    final summary = BillingSummary.fromJson(_summaryJson());

    expect(summary.privacyPolicyUrl, AppConfig.privacyPolicyUrl);
    expect(summary.termsOfUseUrl, AppConfig.termsOfUseUrl);
  });
}

Map<String, dynamic> _summaryJson({
  String? privacyPolicyUrl,
  String? termsOfUseUrl,
}) {
  return <String, dynamic>{
    'client_id': 'as_test_client',
    'support_username': '@support',
    'support_max_url': 'https://max.ru/support',
    'offer_url': 'https://example.com/offer',
    if (privacyPolicyUrl != null) 'privacy_policy_url': privacyPolicyUrl,
    if (termsOfUseUrl != null) 'terms_of_use_url': termsOfUseUrl,
    'test_mode': false,
    'plans': const <dynamic>[],
    'active_subscription': null,
    'latest_valid_subscription': null,
  };
}
