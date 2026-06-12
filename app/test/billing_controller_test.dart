import 'package:appslides/data/repositories/appslides_repository.dart';
import 'package:appslides/core/config/app_config.dart';
import 'package:appslides/domain/models/billing_payment.dart';
import 'package:appslides/domain/models/billing_plan.dart';
import 'package:appslides/domain/models/billing_subscription.dart';
import 'package:appslides/domain/models/billing_summary.dart';
import 'package:appslides/features/billing/billing_controller.dart';
import 'package:appslides/features/billing/store_billing_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('restores App Store purchase through backend verification', () async {
    SharedPreferencesAsyncPlatform.instance =
        InMemorySharedPreferencesAsync.empty();
    final purchaseDetails = PurchaseDetails(
      purchaseID: '200000000000777',
      productID: 'slide_ai_week',
      verificationData: PurchaseVerificationData(
        localVerificationData: 'local-app-store-receipt',
        serverVerificationData: 'server-app-store-receipt',
        source: 'app_store',
      ),
      transactionDate: '1760000000000',
      status: PurchaseStatus.restored,
    )..pendingCompletePurchase = true;
    final storeBilling = FakeStoreBilling(
      StorePurchaseResult(
        provider: StoreBillingProvider.appStore,
        productId: 'slide_ai_week',
        verificationData: 'server-app-store-receipt',
        verificationSource: 'app_store',
        localVerificationData: 'local-app-store-receipt',
        transactionId: '200000000000777',
        purchaseDetails: purchaseDetails,
      ),
    );
    final repository = FakeRepository();
    final controller = BillingController(
      repository: repository,
      storeBilling: storeBilling,
    );

    await controller.restoreAppStorePurchase();

    expect(repository.verifiedProductId, 'slide_ai_week');
    expect(repository.verifiedTransactionId, '200000000000777');
    expect(repository.verifiedData, 'server-app-store-receipt');
    expect(repository.verifiedSource, 'app_store');
    expect(repository.localVerifiedData, 'local-app-store-receipt');
    expect(storeBilling.completedPurchase, same(purchaseDetails));
    expect(controller.payment?.paymentId, '200000000000777');
    expect(controller.summary?.remainingGenerations, 10);
    expect(controller.restoringPurchase, isFalse);
    expect(controller.error, isNull);
  });
}

class FakeStoreBilling implements StoreBillingClient {
  FakeStoreBilling(this.purchase);

  final StorePurchaseResult purchase;
  PurchaseDetails? completedPurchase;

  @override
  bool get available => true;

  @override
  StoreBillingProvider get provider => StoreBillingProvider.appStore;

  @override
  Future<void> initialize() async {}

  @override
  Future<void> refreshProducts() async {}

  @override
  String? productIdForPlan(String planKey) {
    return planKey == 'week' ? 'slide_ai_week' : null;
  }

  @override
  String? priceForPlan(String planKey) {
    return planKey == 'week' ? r'$1.99' : null;
  }

  @override
  Future<StorePurchaseResult> buyPlan(String planKey) async {
    throw UnimplementedError();
  }

  @override
  Future<StorePurchaseResult> restoreLatestPurchase() async => purchase;

  @override
  Future<void> completePurchase(PurchaseDetails purchase) async {
    completedPurchase = purchase;
  }

  @override
  Future<void> dispose() async {}
}

class FakeRepository extends AppSlidesRepository {
  String? verifiedProductId;
  String? verifiedTransactionId;
  String? verifiedData;
  String? verifiedSource;
  String? localVerifiedData;

  @override
  Future<BillingPayment> verifyAppStorePurchase({
    required String productId,
    required String verificationData,
    required String verificationSource,
    String? transactionId,
    String? localVerificationData,
  }) async {
    verifiedProductId = productId;
    verifiedTransactionId = transactionId;
    verifiedData = verificationData;
    verifiedSource = verificationSource;
    localVerifiedData = localVerificationData;
    return BillingPayment(
      paymentId: transactionId ?? 'restored-app-store-payment',
      status: 'paid',
      confirmationUrl: null,
      testMode: false,
      summary: _summary(),
      plan: _weekPlan(),
    );
  }
}

BillingSummary _summary() {
  final now = DateTime.utc(2026, 5, 31);
  return BillingSummary(
    clientId: 'as_test_client',
    supportUsername: '@support',
    supportMaxUrl: 'https://max.ru/support',
    offerUrl: 'https://example.com/offer',
    privacyPolicyUrl: AppConfig.privacyPolicyUrl,
    termsOfUseUrl: AppConfig.termsOfUseUrl,
    testMode: false,
    plans: [_weekPlan()],
    activeSubscription: BillingSubscription(
      planKey: 'week',
      status: 'active',
      remaining: 10,
      startsAt: now.toIso8601String(),
      endsAt: now.add(const Duration(days: 7)).toIso8601String(),
      autoRenew: true,
      provider: 'app_store',
    ),
    latestValidSubscription: null,
  );
}

BillingPlan _weekPlan() {
  return const BillingPlan(
    key: 'week',
    title: 'Weekly',
    priceRub: 199,
    limit: 10,
    days: 7,
    recurring: true,
    appStoreProductId: 'slide_ai_week',
  );
}
