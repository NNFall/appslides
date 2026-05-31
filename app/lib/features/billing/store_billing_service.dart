import 'dart:async';

import 'package:in_app_purchase/in_app_purchase.dart';

import '../../core/config/app_config.dart';

enum StoreBillingProvider {
  googlePlay,
  appStore,
}

class StorePurchaseResult {
  const StorePurchaseResult({
    required this.provider,
    required this.productId,
    required this.verificationData,
    required this.verificationSource,
    required this.purchaseDetails,
    this.packageName,
    this.transactionId,
    this.localVerificationData,
  });

  final StoreBillingProvider provider;
  final String? packageName;
  final String productId;
  final String verificationData;
  final String verificationSource;
  final String? localVerificationData;
  final String? transactionId;
  final PurchaseDetails purchaseDetails;
}

class StoreBillingException implements Exception {
  const StoreBillingException(this.message);

  final String message;

  @override
  String toString() => message;
}

class StoreBillingService {
  StoreBillingService({
    InAppPurchase? inAppPurchase,
    StoreBillingProvider? provider,
  })  : _inAppPurchase = inAppPurchase ?? InAppPurchase.instance,
        _provider = provider ??
            (AppConfig.useAppStoreBilling
                ? StoreBillingProvider.appStore
                : StoreBillingProvider.googlePlay);

  static const Duration _purchaseTimeout = Duration(minutes: 10);

  final InAppPurchase _inAppPurchase;
  final StoreBillingProvider _provider;
  final Map<String, ProductDetails> _products = <String, ProductDetails>{};
  final Map<String, Completer<PurchaseDetails>> _pendingPurchases =
      <String, Completer<PurchaseDetails>>{};

  StreamSubscription<List<PurchaseDetails>>? _purchaseSubscription;
  bool _available = false;
  bool _initialized = false;

  bool get available => _available;
  StoreBillingProvider get provider => _provider;

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

    final productIds = <String>{};
    switch (_provider) {
      case StoreBillingProvider.appStore:
        productIds
          ..add(AppConfig.appStoreWeekProductId)
          ..add(AppConfig.appStoreMonthProductId);
        break;
      case StoreBillingProvider.googlePlay:
        productIds
          ..add(AppConfig.googlePlayWeekProductId)
          ..add(AppConfig.googlePlayMonthProductId);
        break;
    }
    final response = await _inAppPurchase.queryProductDetails(productIds);
    if (response.error != null) {
      throw StoreBillingException(response.error!.message);
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
    return switch (_provider) {
      StoreBillingProvider.appStore =>
        AppConfig.appStoreProductIdForPlan(planKey),
      StoreBillingProvider.googlePlay =>
        AppConfig.googlePlayProductIdForPlan(planKey),
    };
  }

  String? priceForPlan(String planKey) {
    final productId = productIdForPlan(planKey);
    if (productId == null) {
      return null;
    }
    return _products[productId]?.price;
  }

  Future<StorePurchaseResult> buyPlan(String planKey) async {
    await initialize();
    if (!_available) {
      throw StoreBillingException(
        _provider == StoreBillingProvider.appStore
            ? 'App Store purchases are not available on this device.'
            : 'Google Play Billing is not available on this device.',
      );
    }

    final productId = productIdForPlan(planKey);
    if (productId == null) {
      throw StoreBillingException(
        _provider == StoreBillingProvider.appStore
            ? 'This plan is not configured for App Store.'
            : 'This plan is not configured for Google Play.',
      );
    }

    var product = _products[productId];
    if (product == null) {
      await refreshProducts();
      product = _products[productId];
    }
    if (product == null) {
      throw StoreBillingException(
        'Store product "$productId" is not available. Check store products and tester access.',
      );
    }

    final completer = Completer<PurchaseDetails>();
    _pendingPurchases[productId] = completer;

    final launched = await _inAppPurchase.buyNonConsumable(
      purchaseParam: PurchaseParam(productDetails: product),
    );
    if (!launched) {
      _pendingPurchases.remove(productId);
      throw const StoreBillingException('Store purchase flow was not opened.');
    }

    final purchase = await completer.future.timeout(
      _purchaseTimeout,
      onTimeout: () {
        _pendingPurchases.remove(productId);
        throw const StoreBillingException(
          'Store purchase confirmation timed out.',
        );
      },
    );
    final serverVerificationData =
        purchase.verificationData.serverVerificationData;
    if (serverVerificationData.isEmpty) {
      throw const StoreBillingException(
        'Store did not return verification data.',
      );
    }

    return StorePurchaseResult(
      provider: _provider,
      packageName: _provider == StoreBillingProvider.googlePlay
          ? AppConfig.googlePlayPackageName
          : null,
      productId: purchase.productID,
      verificationData: serverVerificationData,
      verificationSource: purchase.verificationData.source,
      localVerificationData: purchase.verificationData.localVerificationData,
      transactionId: purchase.purchaseID,
      purchaseDetails: purchase,
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

  Future<void> dispose() async {
    await _purchaseSubscription?.cancel();
    _purchaseSubscription = null;
    for (final completer in _pendingPurchases.values) {
      if (!completer.isCompleted) {
        completer.completeError(
          const StoreBillingException('Store purchase was canceled.'),
        );
      }
    }
    _pendingPurchases.clear();
  }

  void _handlePurchaseUpdates(List<PurchaseDetails> purchases) {
    for (final purchase in purchases) {
      final completer = _pendingPurchases[purchase.productID];
      if (completer == null || completer.isCompleted) {
        continue;
      }

      switch (purchase.status) {
        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          _pendingPurchases.remove(purchase.productID);
          completer.complete(purchase);
          break;
        case PurchaseStatus.error:
          _pendingPurchases.remove(purchase.productID);
          completer.completeError(
            StoreBillingException(
              purchase.error?.message ?? 'Store purchase failed.',
            ),
          );
          break;
        case PurchaseStatus.canceled:
          _pendingPurchases.remove(purchase.productID);
          completer.completeError(
            const StoreBillingException('Store purchase was canceled.'),
          );
          break;
        case PurchaseStatus.pending:
          break;
      }
    }
  }
}
