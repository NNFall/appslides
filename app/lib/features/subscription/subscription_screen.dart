import 'package:flutter/material.dart';

import '../../shared/widgets/section_card.dart';

class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      children: [
        const SectionCard(
          title: 'Billing',
          subtitle:
              'The mobile version uses native store billing for subscriptions.',
        ),
        const SizedBox(height: 16),
        SectionCard(
          title: 'What must not break',
          subtitle:
              'Entitlements, purchase restoration, receipt/purchase token verification and limit sync with the backend.',
          child: Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              FilledButton(
                onPressed: () {},
                child: const Text('Open plans'),
              ),
              OutlinedButton(
                onPressed: () {},
                child: const Text('Restore'),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
