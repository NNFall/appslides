from __future__ import annotations

from argparse import Namespace

from scripts.deploy import deploy_backend_remote as deploy


def test_build_remote_env_passes_app_store_settings() -> None:
    remote_env = deploy.build_remote_env(
        {
            'APP_STORE_BUNDLE_ID': 'com.appslides.slideai',
            'APP_STORE_APP_APPLE_ID': '1234567890',
            'APP_STORE_ISSUER_ID': 'issuer-id',
            'APP_STORE_KEY_ID': 'key-id',
            'APP_STORE_PRIVATE_KEY_FILE': '/data/appstore/AuthKey_TEST.p8',
            'APP_STORE_ENVIRONMENT': 'sandbox',
            'APP_STORE_TEST_MODE': '1',
        },
        host_port=8031,
    )

    assert 'HOST_PORT=8031' in remote_env
    assert 'APP_STORE_BUNDLE_ID=com.appslides.slideai' in remote_env
    assert 'APP_STORE_APP_APPLE_ID=1234567890' in remote_env
    assert 'APP_STORE_ISSUER_ID=issuer-id' in remote_env
    assert 'APP_STORE_KEY_ID=key-id' in remote_env
    assert 'APP_STORE_PRIVATE_KEY_FILE=/data/appstore/AuthKey_TEST.p8' in remote_env
    assert 'APP_STORE_ENVIRONMENT=sandbox' in remote_env
    assert 'APP_STORE_TEST_MODE=1' in remote_env


def test_apply_cli_overrides_sets_isolated_container_names() -> None:
    local_env = {
        'BACKEND_CONTAINER_NAME': 'pmappslides_backend',
        'ADMIN_BOT_CONTAINER_NAME': 'pmappslides_admin_bot',
        'PM_ADMIN_BOT_TOKEN': 'token',
    }

    deploy.apply_cli_overrides(
        local_env,
        Namespace(
            backend_container_name='asappslides_backend',
            admin_bot_container_name='asappslides_admin_bot',
            disable_admin_bot=True,
            billing_profile='default',
        ),
    )

    assert local_env['BACKEND_CONTAINER_NAME'] == 'asappslides_backend'
    assert local_env['ADMIN_BOT_CONTAINER_NAME'] == 'asappslides_admin_bot'
    assert 'PM_ADMIN_BOT_TOKEN' not in local_env


def test_app_store_billing_profile_removes_non_apple_billing_settings() -> None:
    local_env = {
        'KIE_API_KEY': 'keep-ai-key',
        'YOOKASSA_SHOP_ID': 'shop-id',
        'YOOKASSA_SECRET_KEY': 'secret',
        'YOOKASSA_RETURN_URL': 'https://example.com/yookassa',
        'GOOGLE_PLAY_PACKAGE_NAME': 'com.appslides.slideai',
        'GOOGLE_PLAY_SERVICE_ACCOUNT_JSON': '{"type":"service_account"}',
        'GOOGLE_PLAY_TEST_MODE': '1',
        'APP_STORE_BUNDLE_ID': 'com.appslides.slideai',
        'APP_STORE_ENVIRONMENT': 'sandbox',
    }

    deploy.apply_cli_overrides(
        local_env,
        Namespace(
            backend_container_name='asappslides_backend',
            admin_bot_container_name='asappslides_admin_bot',
            disable_admin_bot=True,
            billing_profile='app-store',
        ),
    )
    remote_env = deploy.build_remote_env(local_env, host_port=8031)

    assert 'KIE_API_KEY=keep-ai-key' in remote_env
    assert 'APP_STORE_BUNDLE_ID=com.appslides.slideai' in remote_env
    assert 'APP_STORE_ENVIRONMENT=sandbox' in remote_env
    assert 'YOOKASSA_' not in remote_env
    assert 'GOOGLE_PLAY_' not in remote_env


def test_app_store_billing_profile_writes_safe_app_store_defaults() -> None:
    local_env: dict[str, str] = {}

    deploy.apply_cli_overrides(
        local_env,
        Namespace(
            backend_container_name='asappslides_backend',
            admin_bot_container_name='asappslides_admin_bot',
            disable_admin_bot=True,
            billing_profile='app-store',
        ),
    )
    remote_env = deploy.build_remote_env(local_env, host_port=8031)

    assert 'APP_STORE_BUNDLE_ID=com.appslides.slideai' in remote_env
    assert 'APP_STORE_ENVIRONMENT=sandbox' in remote_env
    assert 'APP_STORE_TEST_MODE=0' in remote_env
