import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:in_app_purchase_platform_interface/in_app_purchase_platform_interface.dart';

import 'package:appslides/features/billing/google_play_billing_service.dart';

void main() {
  test('restores a previous Google Play subscription purchase', () async {
    final fakeStore = _FakeInAppPurchase(
      restoredPurchases: <PurchaseDetails>[
        _purchase('slide_ai_week', 'restored-token-week'),
      ],
    );
    final service = GooglePlayBillingService(
      inAppPurchase: fakeStore,
      restoreSettleDelay: Duration.zero,
    );

    final restored = await service.restoreKnownPurchases();

    expect(fakeStore.restoreCalled, isTrue);
    expect(restored, hasLength(1));
    expect(restored.single.productId, 'slide_ai_week');
    expect(restored.single.purchaseToken, 'restored-token-week');
    await service.dispose();
  });
}

PurchaseDetails _purchase(String productId, String token) {
  final purchase = PurchaseDetails(
    purchaseID: 'purchase-$productId',
    productID: productId,
    verificationData: PurchaseVerificationData(
      localVerificationData: 'local-$token',
      serverVerificationData: token,
      source: 'google_play',
    ),
    transactionDate: '1710000000000',
    status: PurchaseStatus.restored,
  );
  purchase.pendingCompletePurchase = true;
  return purchase;
}

class _FakeInAppPurchase implements InAppPurchase {
  _FakeInAppPurchase({required this.restoredPurchases});

  final List<PurchaseDetails> restoredPurchases;
  final StreamController<List<PurchaseDetails>> _purchaseController =
      StreamController<List<PurchaseDetails>>.broadcast();

  bool restoreCalled = false;

  @override
  Stream<List<PurchaseDetails>> get purchaseStream =>
      _purchaseController.stream;

  @override
  Future<bool> isAvailable() async => true;

  @override
  Future<ProductDetailsResponse> queryProductDetails(
    Set<String> identifiers,
  ) async {
    final products = identifiers
        .map(
          (id) => ProductDetails(
            id: id,
            title: id,
            description: id,
            price: r'$1.00',
            rawPrice: 1,
            currencyCode: 'USD',
          ),
        )
        .toList();
    return ProductDetailsResponse(
      productDetails: products,
      notFoundIDs: const <String>[],
    );
  }

  @override
  Future<bool> buyConsumable({
    required PurchaseParam purchaseParam,
    bool autoConsume = true,
  }) async {
    return true;
  }

  @override
  Future<bool> buyNonConsumable({required PurchaseParam purchaseParam}) async {
    return true;
  }

  @override
  Future<void> completePurchase(PurchaseDetails purchase) async {}

  @override
  Future<void> restorePurchases({String? applicationUserName}) async {
    restoreCalled = true;
    _purchaseController.add(restoredPurchases);
    await Future<void>.delayed(Duration.zero);
  }

  @override
  Future<String> countryCode() async => 'US';

  @override
  T getPlatformAddition<T extends InAppPurchasePlatformAddition?>() {
    throw UnimplementedError();
  }

  Future<void> dispose() => _purchaseController.close();
}
