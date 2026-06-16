import 'dart:async';

import 'package:flutter/foundation.dart';

import '../../core/config/app_config.dart';
import '../../data/api/appslides_api_client.dart';
import '../../data/repositories/appslides_repository.dart';
import '../../domain/models/billing_payment.dart';
import '../../domain/models/billing_summary.dart';
import 'google_play_billing_service.dart';

class BillingController extends ChangeNotifier {
  BillingController({
    required AppSlidesRepository repository,
    GooglePlayBillingService? googlePlayBilling,
  })  : _repository = repository,
        _googlePlayBilling = googlePlayBilling ??
            (AppConfig.useGooglePlayBilling
                ? GooglePlayBillingService()
                : null);

  static const Duration _paymentPollInterval = Duration(seconds: 20);
  static const Duration _paymentPollTimeout = Duration(minutes: 30);

  final AppSlidesRepository _repository;
  final GooglePlayBillingService? _googlePlayBilling;

  BillingSummary? _summary;
  BillingPayment? _payment;
  bool _loadingSummary = false;
  bool _creatingPayment = false;
  bool _canceling = false;
  String? _error;
  Timer? _pollTimer;
  DateTime? _pollingStartedAt;
  bool _pollingInFlight = false;
  bool _paymentPollingTimedOut = false;

  BillingSummary? get summary => _summary;
  BillingPayment? get payment => _payment;
  bool get loadingSummary => _loadingSummary;
  bool get creatingPayment => _creatingPayment;
  bool get canceling => _canceling;
  String? get error => _error;
  bool get paymentPollingTimedOut => _paymentPollingTimedOut;

  Future<void> initialize() async {
    if (_summary != null || _loadingSummary) {
      return;
    }
    if (AppConfig.useGooglePlayBilling) {
      try {
        await _googlePlayBilling?.initialize();
      } catch (error) {
        _error = _describeError(error);
      }
    }
    await refreshSummary();
  }

  Future<void> refreshSummary() async {
    _loadingSummary = true;
    _error = null;
    notifyListeners();

    try {
      _summary = await _repository.fetchBillingSummary();
    } catch (error) {
      _error = _describeError(error);
    } finally {
      _loadingSummary = false;
      notifyListeners();
    }
  }

  Future<void> startCheckout({
    required String planKey,
    bool renew = false,
  }) async {
    _creatingPayment = true;
    _error = null;
    notifyListeners();

    try {
      final payment = AppConfig.useGooglePlayBilling
          ? await _startGooglePlayCheckout(planKey)
          : await _repository.createBillingPayment(
              planKey: planKey,
              renew: renew,
            );
      _payment = payment;
      _summary = payment.summary;
      if (!payment.isFinished) {
        _startPolling(payment.paymentId);
      }
    } catch (error) {
      _error = _describeError(error);
    } finally {
      _creatingPayment = false;
      notifyListeners();
    }
  }

  Future<bool> restoreGooglePlayPurchases() async {
    final billing = _googlePlayBilling;
    if (billing == null) {
      _error = 'Google Play Billing is not configured in this build.';
      notifyListeners();
      return false;
    }

    _creatingPayment = true;
    _error = null;
    notifyListeners();

    try {
      final purchases = await billing.restoreKnownPurchases();
      Object? lastError;
      for (final purchase in purchases) {
        try {
          final payment = await _repository.verifyGooglePlayPurchase(
            packageName: purchase.packageName,
            productId: purchase.productId,
            purchaseToken: purchase.purchaseToken,
          );
          if (payment.isSuccessful) {
            await billing.completePurchase(purchase.purchaseDetails);
            _payment = payment;
            _summary = payment.summary;
            notifyListeners();
            return true;
          }
        } catch (error) {
          lastError = error;
        }
      }
      if (lastError != null) {
        _error = _describeError(lastError);
      } else {
        _error = 'No active Google Play purchases were found for this account.';
      }
      return false;
    } catch (error) {
      _error = _describeError(error);
      return false;
    } finally {
      _creatingPayment = false;
      notifyListeners();
    }
  }

  Future<void> pollPayment(String paymentId) async {
    if (_pollingInFlight) {
      return;
    }

    _pollingInFlight = true;
    try {
      final payment = await _repository.getBillingPayment(paymentId);
      _payment = payment;
      _summary = payment.summary;
      if (payment.isFinished) {
        _stopPolling();
      } else if (_pollingStartedAt != null) {
        _paymentPollingTimedOut = false;
      }
      notifyListeners();
    } catch (error) {
      _error = _describeError(error);
      notifyListeners();
    } finally {
      _pollingInFlight = false;
    }
  }

  Future<void> cancelSubscription() async {
    _canceling = true;
    _error = null;
    notifyListeners();

    try {
      _summary = await _repository.cancelBillingSubscription();
    } catch (error) {
      _error = _describeError(error);
    } finally {
      _canceling = false;
      notifyListeners();
    }
  }

  void clearPayment() {
    _stopPolling();
    _payment = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _stopPolling();
    unawaited(_googlePlayBilling?.dispose() ?? Future<void>.value());
    super.dispose();
  }

  String? storePriceForPlan(String planKey) {
    return _googlePlayBilling?.priceForPlan(planKey);
  }

  Future<BillingPayment> _startGooglePlayCheckout(String planKey) async {
    final billing = _googlePlayBilling;
    if (billing == null) {
      throw const GooglePlayBillingException(
        'Google Play Billing is not configured in this build.',
      );
    }

    final purchase = await billing.buyPlan(planKey);
    final payment = await _repository.verifyGooglePlayPurchase(
      packageName: purchase.packageName,
      productId: purchase.productId,
      purchaseToken: purchase.purchaseToken,
    );
    if (payment.isSuccessful) {
      await billing.completePurchase(purchase.purchaseDetails);
    }
    return payment;
  }

  void _startPolling(String paymentId) {
    _stopPolling();
    _pollingStartedAt = DateTime.now();
    _paymentPollingTimedOut = false;
    _pollTimer = Timer.periodic(_paymentPollInterval, (_) async {
      if (_pollingStartedAt == null ||
          DateTime.now().difference(_pollingStartedAt!) >=
              _paymentPollTimeout) {
        _paymentPollingTimedOut = true;
        _stopPolling(resetTimeout: false);
        notifyListeners();
        return;
      }
      await pollPayment(paymentId);
    });
    unawaited(pollPayment(paymentId));
  }

  void _stopPolling({bool resetTimeout = true}) {
    _pollTimer?.cancel();
    _pollTimer = null;
    _pollingStartedAt = null;
    _pollingInFlight = false;
    if (resetTimeout) {
      _paymentPollingTimedOut = false;
    }
  }

  String _describeError(Object error) {
    if (error is AppSlidesApiException) {
      return error.message;
    }
    return error.toString();
  }
}
