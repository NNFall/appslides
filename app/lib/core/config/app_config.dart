class AppConfig {
  static const String appName = 'Slide AI: PPTX & PDF Maker';
  static const String billingProvider = String.fromEnvironment(
    'APPSLIDES_BILLING_PROVIDER',
    defaultValue: 'google_play',
  );
  static const String googlePlayPackageName = String.fromEnvironment(
    'APPSLIDES_GOOGLE_PLAY_PACKAGE_NAME',
    defaultValue: 'com.appslides.slideai',
  );
  static const String googlePlayWeekProductId = String.fromEnvironment(
    'APPSLIDES_GOOGLE_PLAY_WEEK_PRODUCT_ID',
    defaultValue: 'slide_ai_week',
  );
  static const String googlePlayMonthProductId = String.fromEnvironment(
    'APPSLIDES_GOOGLE_PLAY_MONTH_PRODUCT_ID',
    defaultValue: 'slide_ai_month',
  );
  static const String fixedBackendBaseUrl = 'http://185.171.83.116:8021';
  static const String healthPath = '/v1/health';
  static const String templatesPath = '/v1/templates/presentation';
  static const String outlinePath = '/v1/presentations/outline';
  static const String outlineRevisePath = '/v1/presentations/outline/revise';
  static const String renderPath = '/v1/presentations/render';
  static const String presentationJobsPath = '/v1/presentations/jobs';
  static const String conversionJobsPath = '/v1/conversions/jobs';
  static const String billingSummaryPath = '/v1/billing/summary';
  static const String billingPaymentsPath = '/v1/billing/payments';
  static const String googlePlayVerifyPath = '/v1/billing/google-play/verify';
  static const String billingCancelSubscriptionPath =
      '/v1/billing/subscription/cancel';
  static const String promoRedeemPath = '/v1/promo/redeem';

  static String presentationJobPath(String jobId) =>
      '$presentationJobsPath/$jobId';

  static String presentationDownloadPath(String jobId, String format) =>
      '${presentationJobPath(jobId)}/download/$format';

  static String conversionJobPath(String jobId) => '$conversionJobsPath/$jobId';

  static String conversionDownloadPath(String jobId) =>
      '${conversionJobPath(jobId)}/download';

  static String billingPaymentPath(String paymentId) =>
      '$billingPaymentsPath/$paymentId';

  static String get defaultBackendBaseUrl => fixedBackendBaseUrl;

  static bool get useGooglePlayBilling => billingProvider == 'google_play';

  static String? googlePlayProductIdForPlan(String planKey) {
    return switch (planKey) {
      'week' => googlePlayWeekProductId,
      'month' => googlePlayMonthProductId,
      _ => null,
    };
  }

  const AppConfig._();
}
