import '../../domain/models/billing_plan.dart';

class BillingPlanFormatter {
  const BillingPlanFormatter({
    required this.storeBillingEnabled,
    required this.appStoreBillingEnabled,
    this.storePriceForPlan = const <String, String>{},
  });

  final bool storeBillingEnabled;
  final bool appStoreBillingEnabled;
  final Map<String, String> storePriceForPlan;

  String optionLabel(BillingPlan plan) {
    return switch (plan.key) {
      'week' => '🔥 ${tariffLine(plan)}',
      'month' => '⭐ ${tariffLine(plan)}',
      'one10' => '⭐ ${tariffLine(plan)}',
      'one40' => '⭐ ${tariffLine(plan)}',
      _ => '${priceLabel(plan)} — ${plan.limit} generations',
    };
  }

  String tariffLine(BillingPlan plan) {
    final price = priceLabel(plan);
    if (storeBillingEnabled) {
      return switch (plan.key) {
        'week' => '$price / week — ${plan.limit} generations',
        'month' => '$price / month — ${plan.limit} generations',
        _ => '$price — ${plan.limit} generations',
      };
    }
    return switch (plan.key) {
      'week' => '$price / week — ${plan.limit} generations',
      'month' => '$price / month — ${plan.limit} generations',
      'one10' => '$price — ${plan.limit} generations',
      'one40' => '$price — ${plan.limit} generations',
      _ => '$price — ${plan.limit} generations',
    };
  }

  String priceLabel(BillingPlan plan) {
    final storePrice = storePriceForPlan[plan.key]?.trim();
    if (storeBillingEnabled && storePrice != null && storePrice.isNotEmpty) {
      return storePrice;
    }
    if (appStoreBillingEnabled) {
      return switch (plan.key) {
        'week' => r'$1.99',
        'month' => r'$4.99',
        _ => '\$${(plan.priceRub / 100).toStringAsFixed(2)}',
      };
    }
    return '${plan.priceRub} ₽';
  }
}
