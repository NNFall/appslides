from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.integrations.admin_notifier import AdminNotifier  # noqa: E402


class CapturingNotifier(AdminNotifier):
    def __init__(self) -> None:
        super().__init__(bot_token="", admin_ids=[])
        self.messages: list[str] = []

    async def notify(self, text: str) -> None:
        self.messages.append(text)


class AdminNotifierFormattingTests(unittest.IsolatedAsyncioTestCase):
    async def test_new_client_message_uses_short_id_and_html_markup(self) -> None:
        notifier = CapturingNotifier()
        await notifier.notify_new_client("appslides_monhlids_f677777d2d08d0e059", "tag")
        message = notifier.messages[-1]
        self.assertIn("<b>", message)
        self.assertIn("User ID:", message)
        self.assertIn("appslides_m", message)
        self.assertIn("d0e059", message)
        self.assertIn("tag", message)

    async def test_outline_created_message_contains_short_id_and_slide_count(self) -> None:
        notifier = CapturingNotifier()
        await notifier.notify_outline_created(
            "appslides_monhlids_f677777d2d08d0e059",
            "topic text for outline",
            9,
        )
        message = notifier.messages[-1]
        self.assertIn("User ID:", message)
        self.assertIn("appslides_m", message)
        self.assertIn("d0e059", message)
        self.assertIn("9", message)

    async def test_promo_redeemed_message_contains_code_and_usage(self) -> None:
        notifier = CapturingNotifier()
        await notifier.notify_promo_redeemed(
            client_id="appslides_monhlids_f677777d2d08d0e059",
            code="c7206288",
            tokens=10,
            used=1,
            max_uses=1,
        )
        message = notifier.messages[-1]
        self.assertIn("User ID:", message)
        self.assertIn("c7206288", message)
        self.assertIn("10", message)
        self.assertIn("1/1", message)

    async def test_auto_renew_success_format(self) -> None:
        notifier = CapturingNotifier()
        await notifier.notify_auto_renew_success(
            client_id="client-1234567890abcdef",
            plan_key="week",
            plan_title="plan",
            tokens=10,
            amount_rub=199,
            status="succeeded",
            payment_id="payment-1",
        )
        message = notifier.messages[-1]
        self.assertIn("User ID:", message)
        self.assertIn("client-1234", message)
        self.assertIn("abcdef", message)
        self.assertIn("payment-1", message)
        self.assertIn("199", message)

    async def test_auto_renew_error_format(self) -> None:
        notifier = CapturingNotifier()
        await notifier.notify_auto_renew_error(
            client_id="client-123",
            plan_key="week",
            plan_title="plan",
            tokens=10,
            amount_rub=199,
            status="error",
            payment_id="-",
            reason="payment_method_id missing",
            expires_subscription=True,
        )
        message = notifier.messages[-1]
        self.assertIn("client-123", message)
        self.assertIn("payment_method_id missing", message)
        self.assertIn("expired", message)

    async def test_manual_renew_success_format(self) -> None:
        notifier = CapturingNotifier()
        await notifier.notify_renewal_success(
            client_id="client-123",
            plan_key="month",
            plan_title="plan",
            tokens=50,
            amount_rub=499,
            status="succeeded",
            payment_id="payment-2",
        )
        message = notifier.messages[-1]
        self.assertIn("client-123", message)
        self.assertIn("payment-2", message)
        self.assertIn("499", message)


if __name__ == "__main__":
    unittest.main()
