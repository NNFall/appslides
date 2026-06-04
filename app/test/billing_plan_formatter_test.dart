import 'package:appslides/domain/models/billing_plan.dart';
import 'package:appslides/features/billing/billing_plan_formatter.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('formats App Store fallback prices in USD', () {
    const formatter = BillingPlanFormatter(
      storeBillingEnabled: true,
      appStoreBillingEnabled: true,
    );

    expect(formatter.tariffLine(_weekPlan()), r'$1.99 / week — 10 generations');
    expect(
      formatter.tariffLine(_monthPlan()),
      r'$4.99 / month — 50 generations',
    );
  });

  test('uses native store price when StoreKit metadata is available', () {
    const formatter = BillingPlanFormatter(
      storeBillingEnabled: true,
      appStoreBillingEnabled: true,
      storePriceForPlan: {'week': r'$0.99'},
    );

    expect(formatter.tariffLine(_weekPlan()), r'$0.99 / week — 10 generations');
  });
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

BillingPlan _monthPlan() {
  return const BillingPlan(
    key: 'month',
    title: 'Monthly',
    priceRub: 499,
    limit: 50,
    days: 30,
    recurring: true,
    appStoreProductId: 'slide_ai_month',
  );
}
