import 'package:appslides/core/config/app_config.dart';
import 'package:appslides/data/repositories/legal_links_repository.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('uses built-in legal links before any server data is cached', () async {
    final repository = LegalLinksRepository(
      storage: _MemoryLegalLinksStorage(),
    );

    await repository.restore();

    expect(repository.privacyPolicyUrl, AppConfig.privacyPolicyUrl);
    expect(repository.termsOfUseUrl, AppConfig.termsOfUseUrl);
  });

  test('saves server legal links and restores them later', () async {
    final storage = _MemoryLegalLinksStorage();
    final repository = LegalLinksRepository(storage: storage);

    await repository.save(
      privacyPolicyUrl: 'https://example.com/privacy',
      termsOfUseUrl: 'https://example.com/eula',
    );

    final restored = LegalLinksRepository(storage: storage);
    await restored.restore();

    expect(restored.privacyPolicyUrl, 'https://example.com/privacy');
    expect(restored.termsOfUseUrl, 'https://example.com/eula');
  });

  test('ignores invalid cached links and keeps safe fallbacks', () async {
    final storage = _MemoryLegalLinksStorage(
      initialPrivacyPolicyUrl: 'not a url',
      initialTermsOfUseUrl: 'ftp://example.com/eula',
    );
    final repository = LegalLinksRepository(storage: storage);

    await repository.restore();

    expect(repository.privacyPolicyUrl, AppConfig.privacyPolicyUrl);
    expect(repository.termsOfUseUrl, AppConfig.termsOfUseUrl);
  });
}

class _MemoryLegalLinksStorage implements LegalLinksStorage {
  _MemoryLegalLinksStorage({
    String? initialPrivacyPolicyUrl,
    String? initialTermsOfUseUrl,
  })  : _privacyPolicyUrl = initialPrivacyPolicyUrl,
        _termsOfUseUrl = initialTermsOfUseUrl;

  String? _privacyPolicyUrl;
  String? _termsOfUseUrl;

  @override
  Future<String?> readPrivacyPolicyUrl() async => _privacyPolicyUrl;

  @override
  Future<String?> readTermsOfUseUrl() async => _termsOfUseUrl;

  @override
  Future<void> write({
    required String privacyPolicyUrl,
    required String termsOfUseUrl,
  }) async {
    _privacyPolicyUrl = privacyPolicyUrl;
    _termsOfUseUrl = termsOfUseUrl;
  }
}
