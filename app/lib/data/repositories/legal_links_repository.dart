import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/config/app_config.dart';
import '../../domain/models/billing_summary.dart';

class LegalLinksRepository extends ChangeNotifier {
  LegalLinksRepository({
    LegalLinksStorage? storage,
  }) : _storage = storage ?? SharedPreferencesLegalLinksStorage();

  final LegalLinksStorage _storage;

  String _privacyPolicyUrl = AppConfig.privacyPolicyUrl;
  String _termsOfUseUrl = AppConfig.termsOfUseUrl;
  bool _isLoaded = false;
  bool _isRestoring = false;

  String get privacyPolicyUrl => _privacyPolicyUrl;
  String get termsOfUseUrl => _termsOfUseUrl;
  bool get isLoaded => _isLoaded;

  Future<void> restore() async {
    if (_isLoaded || _isRestoring) {
      return;
    }

    _isRestoring = true;
    notifyListeners();
    try {
      _privacyPolicyUrl = _legalUrlOrFallback(
        await _storage.readPrivacyPolicyUrl(),
        AppConfig.privacyPolicyUrl,
      );
      _termsOfUseUrl = _legalUrlOrFallback(
        await _storage.readTermsOfUseUrl(),
        AppConfig.termsOfUseUrl,
      );
    } finally {
      _isLoaded = true;
      _isRestoring = false;
      notifyListeners();
    }
  }

  Future<void> save({
    required String privacyPolicyUrl,
    required String termsOfUseUrl,
  }) async {
    final normalizedPrivacy = _legalUrlOrFallback(
      privacyPolicyUrl,
      AppConfig.privacyPolicyUrl,
    );
    final normalizedTerms = _legalUrlOrFallback(
      termsOfUseUrl,
      AppConfig.termsOfUseUrl,
    );

    final changed = normalizedPrivacy != _privacyPolicyUrl ||
        normalizedTerms != _termsOfUseUrl;
    _privacyPolicyUrl = normalizedPrivacy;
    _termsOfUseUrl = normalizedTerms;
    await _storage.write(
      privacyPolicyUrl: _privacyPolicyUrl,
      termsOfUseUrl: _termsOfUseUrl,
    );
    if (changed) {
      notifyListeners();
    }
  }

  Future<void> saveFromSummary(BillingSummary summary) {
    return save(
      privacyPolicyUrl: summary.privacyPolicyUrl,
      termsOfUseUrl: summary.termsOfUseUrl,
    );
  }

  static String _legalUrlOrFallback(String? value, String fallback) {
    final raw = value?.trim() ?? '';
    final uri = Uri.tryParse(raw);
    if (uri == null || !uri.hasScheme || uri.host.isEmpty) {
      return fallback;
    }
    if (uri.scheme != 'https') {
      return fallback;
    }
    return uri.toString();
  }
}

abstract class LegalLinksStorage {
  Future<String?> readPrivacyPolicyUrl();

  Future<String?> readTermsOfUseUrl();

  Future<void> write({
    required String privacyPolicyUrl,
    required String termsOfUseUrl,
  });
}

class SharedPreferencesLegalLinksStorage implements LegalLinksStorage {
  static const String _privacyPolicyKey = 'appslides.legal.privacy_url.v1';
  static const String _termsOfUseKey = 'appslides.legal.terms_url.v1';

  final SharedPreferencesAsync _storage = SharedPreferencesAsync();

  @override
  Future<String?> readPrivacyPolicyUrl() {
    return _storage.getString(_privacyPolicyKey);
  }

  @override
  Future<String?> readTermsOfUseUrl() {
    return _storage.getString(_termsOfUseKey);
  }

  @override
  Future<void> write({
    required String privacyPolicyUrl,
    required String termsOfUseUrl,
  }) async {
    await _storage.setString(_privacyPolicyKey, privacyPolicyUrl);
    await _storage.setString(_termsOfUseKey, termsOfUseUrl);
  }
}
