import 'billing_summary.dart';

class PromoRedeemResult {
  const PromoRedeemResult({
    required this.code,
    required this.tokensAdded,
    required this.used,
    required this.maxUses,
    required this.summary,
  });

  final String code;
  final int tokensAdded;
  final int used;
  final int maxUses;
  final BillingSummary summary;

  factory PromoRedeemResult.fromJson(Map<String, dynamic> json) {
    return PromoRedeemResult(
      code: json['code'] as String,
      tokensAdded: json['tokens_added'] as int? ?? 0,
      used: json['used'] as int? ?? 0,
      maxUses: json['max_uses'] as int? ?? 1,
      summary: BillingSummary.fromJson(
        (json['summary'] as Map).cast<String, dynamic>(),
      ),
    );
  }
}
