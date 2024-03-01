
entry for prometheus.yml for locust exporter


  - job_name: 'locust'
    static_configs:
      - targets: ['10.1.1.55:9646']


