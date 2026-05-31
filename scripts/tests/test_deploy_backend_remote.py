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
        ),
    )

    assert local_env['BACKEND_CONTAINER_NAME'] == 'asappslides_backend'
    assert local_env['ADMIN_BOT_CONTAINER_NAME'] == 'asappslides_admin_bot'
    assert 'PM_ADMIN_BOT_TOKEN' not in local_env
