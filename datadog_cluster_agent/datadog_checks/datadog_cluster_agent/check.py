# (C) Datadog, Inc. 2021-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

from datadog_checks.base import OpenMetricsBaseCheck

DEFAULT_METRICS = {
    'admission_webhooks_certificate_expiry': 'admission_webhooks.certificate_expiry',
    'admission_webhooks_mutation_attempts': 'admission_webhooks.mutation_attempts',
    'admission_webhooks_mutation_errors': 'admission_webhooks.mutation_errors',
    'admission_webhooks_reconcile_errors': 'admission_webhooks.reconcile_errors',
    'admission_webhooks_reconcile_success': 'admission_webhooks.reconcile_success',
    'admission_webhooks_webhooks_received': 'admission_webhooks.webhooks_received',
    'admission_webhooks_library_injection_attempts': 'admission_webhooks.library_injection_attempts',
    'admission_webhooks_library_injection_errors': 'admission_webhooks.library_injection_errors',
    'aggregator__flush': 'aggregator.flush',
    'aggregator__processed': 'aggregator.processed',
    'api_requests': 'api_requests',
    'cluster_checks_busyness': 'cluster_checks.busyness',
    'cluster_checks_configs_dangling': 'cluster_checks.configs_dangling',
    'cluster_checks_configs_dispatched': 'cluster_checks.configs_dispatched',
    'cluster_checks_configs_info': 'cluster_checks.configs_info',
    'cluster_checks_failed_stats_collection': 'cluster_checks.failed_stats_collection',
    'cluster_checks_nodes_reporting': 'cluster_checks.nodes_reporting',
    'cluster_checks_rebalancing_decisions': 'cluster_checks.rebalancing_decisions',
    'cluster_checks_rebalancing_duration_seconds': 'cluster_checks.rebalancing_duration_seconds',
    'cluster_checks_successful_rebalancing_moves': 'cluster_checks.successful_rebalancing_moves',
    'cluster_checks_updating_stats_duration_seconds': 'cluster_checks.updating_stats_duration_seconds',
    'datadog_requests': 'datadog.requests',
    'external_metrics': 'external_metrics',
    'external_metrics_datadog_metrics': 'external_metrics.datadog_metrics',
    'external_metrics_delay_seconds': 'external_metrics.delay_seconds',
    'external_metrics_processed_value': 'external_metrics.processed_value',
    'go_goroutines': 'go.goroutines',
    'go_memstats_alloc_bytes': 'go.memstats.alloc_bytes',
    'go_threads': 'go.threads',
    'rate_limit_queries_limit': 'datadog.rate_limit_queries.limit',
    'rate_limit_queries_period': 'datadog.rate_limit_queries.period',
    'rate_limit_queries_remaining': 'datadog.rate_limit_queries.remaining',
    'rate_limit_queries_reset': 'datadog.rate_limit_queries.reset',
    'secret_backend__elapsed_ms': 'secret_backend.elapsed',
    'endpoint_checks_configs_dispatched': 'endpoint_checks.configs_dispatched',
    'autodiscovery_poll_duration': 'autodiscovery.poll_duration',
    'autodiscovery_watched_resources': 'autodiscovery.watched_resources',
    'autodiscovery_errors': 'autodiscovery.errors',
}


class DatadogClusterAgentCheck(OpenMetricsBaseCheck):
    def __init__(self, name, init_config, instances):
        super(DatadogClusterAgentCheck, self).__init__(
            name,
            init_config,
            instances,
            default_instances={
                'datadog.cluster_agent': {
                    'prometheus_url': 'http://localhost:5000/metrics',
                    'namespace': 'datadog.cluster_agent',
                    'metrics': [DEFAULT_METRICS],
                    'label_joins': {
                        'leader_election_is_leader': {
                            'labels_to_match': ['*'],
                            'labels_to_get': ['is_leader'],
                        }
                    },
                    'send_histograms_buckets': True,
                    'send_distribution_counts_as_monotonic': True,
                    'send_distribution_sums_as_monotonic': True,
                }
            },
            default_namespace='datadog.cluster_agent',
        )
