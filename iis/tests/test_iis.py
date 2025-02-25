# (C) Datadog, Inc. 2010-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import copy
import logging
import re

import pytest
from datadog_test_libs.win.pdh_mocks import initialize_pdh_tests, pdh_mocks_fixture  # noqa: F401

from datadog_checks.base.constants import ServiceCheck
from datadog_checks.dev.testing import requires_py2
from datadog_checks.iis import IIS

from .common import (
    APP_POOL_METRICS,
    CHECK_NAME,
    DEFAULT_APP_POOLS,
    DEFAULT_SITES,
    INSTANCE,
    INVALID_HOST_INSTANCE,
    MINIMAL_INSTANCE,
    SITE_METRICS,
    WIN_SERVICES_CONFIG,
    WIN_SERVICES_LEGACY_CONFIG,
    WIN_SERVICES_MINIMAL_CONFIG,
)

pytestmark = [requires_py2, pytest.mark.usefixtures('pdh_mocks_fixture')]


@pytest.fixture(autouse=True)
def setup_check():
    initialize_pdh_tests()


def test_additional_metrics(aggregator, caplog, dd_run_check):
    instance = copy.deepcopy(MINIMAL_INSTANCE)
    instance['additional_metrics'] = [
        [
            'HTTP Service Request Queues',
            'none',
            'RejectedRequests',
            'iis.httpd_service_request_queues.rejectedrequests',
            'gauge',
        ]
    ]

    c = IIS(CHECK_NAME, {}, [instance])

    with caplog.at_level(logging.DEBUG):
        dd_run_check(c)

        aggregator.assert_metric('iis.httpd_service_request_queues.rejectedrequests')
        assert 'Unknown IIS counter: HTTP Service Request Queues. Falling back to default submission' in caplog.text


def test_basic_check(aggregator, dd_run_check):
    instance = MINIMAL_INSTANCE
    c = IIS(CHECK_NAME, {}, [instance])
    dd_run_check(c)
    iis_host = c.get_iishost()

    namespace_data = ((SITE_METRICS, IIS.SITE, DEFAULT_SITES), (APP_POOL_METRICS, IIS.APP_POOL, DEFAULT_APP_POOLS))
    for metrics, namespace, values in namespace_data:
        for metric in metrics:
            for value in values:
                aggregator.assert_metric(metric, tags=['{}:{}'.format(namespace, value), iis_host], count=1)

    for _, namespace, values in namespace_data:
        for value in values:
            aggregator.assert_service_check(
                'iis.{}_up'.format(namespace), IIS.OK, tags=['{}:{}'.format(namespace, value), iis_host], count=1
            )

    aggregator.assert_all_metrics_covered()


def test_check_on_specific_websites_and_app_pools(aggregator, dd_run_check):
    instance = INSTANCE
    c = IIS(CHECK_NAME, {}, [instance])
    dd_run_check(c)
    iis_host = c.get_iishost()

    namespace_data = (
        (SITE_METRICS, IIS.SITE, ['Default_Web_Site', 'Exchange_Back_End', 'Total']),
        (APP_POOL_METRICS, IIS.APP_POOL, ['DefaultAppPool', 'MSExchangeServicesAppPool', 'Total']),
    )
    for metrics, namespace, values in namespace_data:
        for metric in metrics:
            for value in values:
                aggregator.assert_metric(metric, tags=['{}:{}'.format(namespace, value), iis_host], count=1)

    for _, namespace, values in namespace_data:
        for value in values:
            aggregator.assert_service_check(
                'iis.{}_up'.format(namespace), IIS.OK, tags=['{}:{}'.format(namespace, value), iis_host], count=1
            )

    aggregator.assert_service_check('iis.site_up', IIS.CRITICAL, tags=['site:Non_Existing_Website', iis_host], count=1)
    aggregator.assert_service_check(
        'iis.app_pool_up', IIS.CRITICAL, tags=['app_pool:Non_Existing_App_Pool', iis_host], count=1
    )

    aggregator.assert_all_metrics_covered()


def test_service_check_with_invalid_host(aggregator, dd_run_check):
    instance = INVALID_HOST_INSTANCE
    c = IIS(CHECK_NAME, {}, [instance])
    dd_run_check(c)
    iis_host = c.get_iishost()

    aggregator.assert_service_check('iis.site_up', IIS.CRITICAL, tags=['site:Total', iis_host])
    aggregator.assert_service_check('iis.app_pool_up', IIS.CRITICAL, tags=['app_pool:Total', iis_host])


def test_check(aggregator, dd_run_check):
    """
    Returns the right metrics and service checks
    """
    instance = WIN_SERVICES_CONFIG
    c = IIS(CHECK_NAME, {}, [instance])
    dd_run_check(c)
    iis_host = c.get_iishost()

    # Test tag name normalization
    sites = ['Total']
    for site in instance['sites']:
        sites.append(re.sub(r'[,+*\-/()\[\]{}\s]', '_', site))
    app_pools = ['Total']
    for app_pool in instance['app_pools']:
        app_pools.append(re.sub(r'[,+*\-/()\[\]{}\s]', '_', app_pool))

    # Exclude `Failing site` and `Failing app pool`
    namespace_data_ok = ((SITE_METRICS, IIS.SITE, sites[:-1]), (APP_POOL_METRICS, IIS.APP_POOL, app_pools[:-1]))
    for metrics, namespace, values in namespace_data_ok:
        for metric in metrics:
            for value in values:
                aggregator.assert_metric(
                    metric, tags=['mytag1', 'mytag2', '{}:{}'.format(namespace, value), iis_host], count=1
                )

    for _, namespace, values in namespace_data_ok:
        # Exclude `Total`
        for value in values[1:]:
            aggregator.assert_service_check(
                'iis.{}_up'.format(namespace),
                IIS.OK,
                tags=['mytag1', 'mytag2', '{}:{}'.format(namespace, value), iis_host],
                count=1,
            )

    # Only `Failing site` and `Failing app pool`
    namespace_data_failed = ((SITE_METRICS, IIS.SITE, sites[-1:]), (APP_POOL_METRICS, IIS.APP_POOL, app_pools[-1:]))
    for _, namespace, values in namespace_data_failed:
        for value in values:
            aggregator.assert_service_check(
                'iis.{}_up'.format(namespace),
                IIS.CRITICAL,
                tags=['mytag1', 'mytag2', '{}:{}'.format(namespace, value), iis_host],
                count=1,
            )

    aggregator.assert_all_metrics_covered()


def test_check_without_sites_specified(aggregator, dd_run_check):
    """
    Returns the right metrics and service checks for the `_Total` site
    """
    # Run check
    instance = WIN_SERVICES_MINIMAL_CONFIG
    c = IIS(CHECK_NAME, {}, [instance])
    dd_run_check(c)
    iis_host = c.get_iishost()

    namespace_data = ((SITE_METRICS, IIS.SITE, DEFAULT_SITES), (APP_POOL_METRICS, IIS.APP_POOL, DEFAULT_APP_POOLS))
    for metrics, namespace, values in namespace_data:
        for metric in metrics:
            for value in values:
                aggregator.assert_metric(
                    metric, tags=['mytag1', 'mytag2', '{}:{}'.format(namespace, value), iis_host], count=1
                )

    for _, namespace, values in namespace_data:
        for value in values:
            aggregator.assert_service_check(
                'iis.{}_up'.format(namespace),
                IIS.OK,
                tags=['mytag1', 'mytag2', '{}:{}'.format(namespace, value), iis_host],
                count=1,
            )

    aggregator.assert_all_metrics_covered()


def test_legacy_check_version(aggregator, dd_run_check):
    instance = WIN_SERVICES_LEGACY_CONFIG
    c = IIS(CHECK_NAME, {}, [instance])
    dd_run_check(c)
    iis_host = c.get_iishost()

    aggregator.assert_service_check('iis.windows.perf.health', ServiceCheck.OK, count=0)
    namespace_data = ((SITE_METRICS, IIS.SITE, DEFAULT_SITES), (APP_POOL_METRICS, IIS.APP_POOL, DEFAULT_APP_POOLS))
    for metrics, namespace, values in namespace_data:
        for metric in metrics:
            for value in values:
                aggregator.assert_metric(metric, tags=['{}:{}'.format(namespace, value), iis_host], count=1)

    for _, namespace, values in namespace_data:
        for value in values:
            aggregator.assert_service_check(
                'iis.{}_up'.format(namespace),
                IIS.OK,
                tags=['{}:{}'.format(namespace, value), iis_host],
                count=1,
            )

    aggregator.assert_all_metrics_covered()
