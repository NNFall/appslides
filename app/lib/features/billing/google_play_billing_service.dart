import 'dart:async';

import 'package:in_app_purchase/in_app_purchase.dart';

import '../../core/config/app_config.dart';

class GooglePlayPurchaseResult {
  const GooglePlayPurchaseResult({
    required this.packageName,
    required this.productId,
    required this.purchaseToken,
    required this.purchaseDetails,
    this.restored = false,
  });

  final String packageName;
  final String productId;
  final String purchaseToken;
  final PurchaseDetails purchaseDetails;
  final bool restored;
}

class GooglePlayBillingException implements Exception {
  const GooglePlayBillingException(this.message);

  final String message;

  @override
  String toString() => message;
}

class GooglePlayBillingService {
  GooglePlayBillingService({
    InAppPurchase? inAppPurchase,
    Duration restoreSettleDelay = const Duration(seconds: 3),
  })  : _inAppPurchase = inAppPurchase ?? InAppPurchase.instance,
        _restoreSettleDelay = restoreSettleDelay;

  static const Duration _purchaseTimeout = Duration(minutes: 10);

  final InAppPurchase _inAppPurchase;
  final Duration _restoreSettleDelay;
  final Map<String, ProductDetails> _products = <String, ProductDetails>{};
  final Map<String, Completer<PurchaseDetails>> _pendingPurchases =
      <String, Completer<PurchaseDetails>>{};
  final Map<String, PurchaseDetails> _latestPurchases =
      <String, PurchaseDetails>{};

  StreamSubscription<List<PurchaseDetails>>? _purchaseSubscription;
  bool _available = false;
  bool _initialized = false;

  bool get available => _available;

  Future<void> initialize() async {
    if (_initialized) {
      return;
    }
    _initialized = true;
    _purchaseSubscription =
        _inAppPurchase.purchaseStream.listen(_handlePurchaseUpdates);
    await refreshProducts();
  }

  Future<void> refreshProducts() async {
    _available = await _inAppPurchase.isAvailable();
    if (!_available) {
      _products.clear();
      return;
    }

    final productIds = <String>{
      AppConfig.googlePlayWeekProductId,
      AppConfig.googlePlayMonthProductId,
    };
    final response = await _inAppPurchase.queryProductDetails(productIds);
    if (response.error != null) {
      throw GooglePlayBillingException(response.error!.message);
    }
    _products
      ..clear()
      ..addEntries(
        response.productDetails.map(
          (product) => MapEntry(product.id, product),
        ),
      );
  }

  String? productIdForPlan(String planKey) {
    return AppConfig.googlePlayProductIdForPlan(planKey);
  }

  String? priceForPlan(String planKey) {
    final productId = productIdForPlan(planKey);
    if (productId == null) {
      return null;
    }
    return _products[productId]?.price;
  }

  Future<GooglePlayPurchaseResult> buyPlan(String planKey) async {
    await initialize();
    if (!_available) {
      throw const GooglePlayBillingException(
        'Google Play Billing is not available on this device.',
      );
    }

    final productId = productIdForPlan(planKey);
    if (productId == null) {
      throw const GooglePlayBillingException(
        'This plan is not configured for Google Play.',
      );
    }

    var product = _products[productId];
    if (product == null) {
      await refreshProducts();
      product = _products[productId];
    }
    if (product == null) {
      throw GooglePlayBillingException(
        'Google Play product "$productId" is not available. Check Play Console products and tester access.',
      );
    }

    final completer = Completer<PurchaseDetails>();
    _pendingPurchases[productId] = completer;

    final launched = await _inAppPurchase.buyNonConsumable(
      purchaseParam: PurchaseParam(productDetails: product),
    );
    if (!launched) {
      _pendingPurchases.remove(productId);
      final restoredPurchase = await _restoredPurchaseForProduct(productId);
      if (restoredPurchase != null) {
        return restoredPurchase;
      }
      throw const GooglePlayBillingException(
        'Google Play purchase flow was not opened.',
      );
    }

    final purchase = await completer.future.timeout(
      _purchaseTimeout,
      onTimeout: () {
        _pendingPurchases.remove(productId);
        throw const GooglePlayBillingException(
          'Google Play purchase confirmation timed out.',
        );
      },
    );
    final purchaseToken = purchase.verificationData.serverVerificationData;
    if (purchaseToken.isEmpty) {
      throw const GooglePlayBillingException(
        'Google Play did not return a purchase token.',
      );
    }

    return GooglePlayPurchaseResult(
      packageName: AppConfig.googlePlayPackageName,
      productId: purchase.productID,
      purchaseToken: purchaseToken,
      purchaseDetails: purchase,
      restored: purchase.status == PurchaseStatus.restored,
    );
  }

  Future<void> completePurchase(PurchaseDetails purchase) async {
    if (purchase.pendingCompletePurchase) {
      await _inAppPurchase.completePurchase(purchase);
    }
  }

  Future<void> restorePurchases() async {
    await initialize();
    await _inAppPurchase.restorePurchases();
  }

  Future<List<GooglePlayPurchaseResult>> restoreKnownPurchases() async {
    await initialize();
    if (!_available) {
      throw const GooglePlayBillingException(
        'Google Play Billing is not available on this device.',
      );
    }

    await _inAppPurchase.restorePurchases();
    await Future<void>.delayed(_restoreSettleDelay);

    final productIds = <String>{
      AppConfig.googlePlayWeekProductId,
      AppConfig.googlePlayMonthProductId,
    };
    final purchases = <GooglePlayPurchaseResult>[];
    for (final productId in productIds) {
      final purchase = _latestPurchases[productId];
      if (purchase == null) {
        continue;
      }
      final purchaseToken = purchase.verificationData.serverVerificationData;
      if (purchaseToken.isEmpty) {
        continue;
      }
      purchases.add(
        GooglePlayPurchaseResult(
          packageName: AppConfig.googlePlayPackageName,
          productId: purchase.productID,
          purchaseToken: purchaseToken,
          purchaseDetails: purchase,
          restored: true,
        ),
      );
    }

    if (purchases.isEmpty) {
      throw const GooglePlayBillingException(
        'No active Google Play purchases were found for this account.',
      );
    }
    return purchases;
  }

  Future<void> dispose() async {
    await _purchaseSubscription?.cancel();
    _purchaseSubscription = null;
    for (final completer in _pendingPurchases.values) {
      if (!completer.isCompleted) {
        completer.completeError(
          const GooglePlayBillingException(
              'Google Play purchase was canceled.'),
        );
      }
    }
    _pendingPurchases.clear();
  }

  void _handlePurchaseUpdates(List<PurchaseDetails> purchases) {
    for (final purchase in purchases) {
      final completer = _pendingPurchases[purchase.productID];

      switch (purchase.status) {
        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          _latestPurchases[purchase.productID] = purchase;
          if (completer != null && !completer.isCompleted) {
            _pendingPurchases.remove(purchase.productID);
            completer.complete(purchase);
          }
          break;
        case PurchaseStatus.error:
          if (completer != null && !completer.isCompleted) {
            _pendingPurchases.remove(purchase.productID);
            completer.completeError(
              GooglePlayBillingException(
                purchase.error?.message ?? 'Google Play purchase failed.',
              ),
            );
          }
          break;
        case PurchaseStatus.canceled:
          if (completer != null && !completer.isCompleted) {
            _pendingPurchases.remove(purchase.productID);
            completer.completeError(
              const GooglePlayBillingException(
                'Google Play purchase was canceled.',
              ),
            );
          }
          break;
        case PurchaseStatus.pending:
          break;
      }
    }
  }

  Future<GooglePlayPurchaseResult?> _restoredPurchaseForProduct(
    String productId,
  ) async {
    try {
      final restored = await restoreKnownPurchases();
      for (final purchase in restored) {
        if (purchase.productId == productId) {
          return purchase;
        }
      }
    } on GooglePlayBillingException {
      return null;
    }
    return null;
  }
}
