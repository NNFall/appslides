class BillingPlan {
  const BillingPlan({
    required this.key,
    required this.title,
    required this.priceRub,
    required this.limit,
    required this.days,
    required this.recurring,
    this.googlePlayProductId,
    this.appStoreProductId,
  });

  final String key;
  final String title;
  final int priceRub;
  final int limit;
  final int days;
  final bool recurring;
  final String? googlePlayProductId;
  final String? appStoreProductId;

  factory BillingPlan.fromJson(Map<String, dynamic> json) {
    return BillingPlan(
      key: json['key'] as String,
      title: json['title'] as String,
      priceRub: json['price_rub'] as int,
      limit: json['limit'] as int,
      days: json['days'] as int,
      recurring: json['recurring'] as bool,
      googlePlayProductId: json['google_play_product_id'] as String?,
      appStoreProductId: json['app_store_product_id'] as String?,
    );
  }
}
