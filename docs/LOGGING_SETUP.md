# InsightStream AI - Logging & Monitoring Setup Guide

## Overview

This guide covers setting up comprehensive logging and monitoring for InsightStream AI in production. The system uses:

- **Application Logging**: Python logging framework → JSON format → Centralized aggregation
- **Metrics Collection**: Prometheus for time-series metrics
- **Visualization**: Grafana dashboards for real-time monitoring
- **Error Tracking**: Sentry for exception monitoring (optional)
- **Health Checks**: Built-in FastAPI health endpoints

## 1. Application Logging

### 1.1 Python Logging Configuration

Create `backend/app/core/logging_config.py`:

```python
import logging
import json
from datetime import datetime
import os

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging():
    """Configure application-wide logging"""
    
    # Get log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # File handler (JSON format)
    log_file = os.getenv("LOG_FILE", "/var/log/insightstream/app.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Console handler (plain text for development)
    if os.getenv("ENVIRONMENT") == "development":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    return root_logger

# Usage in main.py:
# from .core.logging_config import setup_logging
# logger = setup_logging()
```

### 1.2 Integration in FastAPI

Add to `backend/app/main.py` startup:

```python
from .core.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger.info("🚀 InsightStream AI API starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT')}")
    logger.info(f"Version: 0.2.0")
```

## 2. Log Aggregation

### 2.1 ELK Stack (Elasticsearch, Logstash, Kibana)

Setup with Docker:

```yaml
# docker-compose.yml additions
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
  environment:
    - discovery.type=single-node
    - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
  ports:
    - "9200:9200"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data

logstash:
  image: docker.elastic.co/logstash/logstash:7.14.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  ports:
    - "5000:5000"
  depends_on:
    - elasticsearch

kibana:
  image: docker.elastic.co/kibana/kibana:7.14.0
  ports:
    - "5601:5601"
  depends_on:
    - elasticsearch
```

### 2.2 Logstash Configuration

Create `logstash.conf`:

```conf
input {
  file {
    path => "/var/log/insightstream/app.log"
    codec => json
    start_position => "beginning"
  }
}

filter {
  mutate {
    rename => { "level" => "severity" }
    remove_field => [ "path", "host" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "insightstream-%{+YYYY.MM.dd}"
  }
  stdout {
    codec => rubydebug
  }
}
```

### 2.3 Alternative: Datadog

If using Datadog instead of ELK:

```python
# Install: pip install ddtrace

from ddtrace import tracer
from ddtrace.ext import SpanTypes

@app.middleware("http")
async def datadog_middleware(request, call_next):
    with tracer.trace("http.request", span_type=SpanTypes.WEB) as span:
        span.set_tag("http.method", request.method)
        span.set_tag("http.url", request.url.path)
        response = await call_next(request)
        span.set_tag("http.status_code", response.status_code)
        return response
```

## 3. Metrics Collection (Prometheus)

### 3.1 Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'insightstream-api'
    static_configs:
      - targets: ['localhost:8000']

  - job_name: 'insightstream-worker'
    static_configs:
      - targets: ['localhost:8001']

  - job_name: 'qdrant'
    static_configs:
      - targets: ['localhost:6333']

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['localhost:15692']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### 3.2 Add Prometheus Metrics to FastAPI

```python
# Install: pip install prometheus-client

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response
import time

# Define metrics
request_count = Counter(
    'insightstream_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'insightstream_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'insightstream_active_connections',
    'Number of active connections'
)

# Middleware to collect metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    active_connections.inc()
    
    try:
        response = await call_next(request)
        status = response.status_code
    finally:
        active_connections.dec()
    
    duration = time.time() - start_time
    
    # Record metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=status
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Expose metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 4. Grafana Dashboards

### 4.1 Create Dashboard via UI

1. Open Grafana: `http://localhost:3001`
2. Login with default credentials (admin/admin)
3. Add Prometheus data source:
   - URL: `http://prometheus:9090`
4. Create new dashboard with panels for:
   - Request rate (requests/sec)
   - Request latency (p95, p99)
   - Error rate
   - Active connections
   - Database query time
   - API integration health

### 4.2 Dashboard as Code (JSON)

Export dashboards as JSON for version control:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  http://localhost:3001/api/dashboards/uid/dashboard-uid > dashboard.json
```

Store in `monitoring/grafana/dashboards/insightstream.json` for auto-provisioning.

## 5. Error Tracking (Sentry)

### 5.1 Setup Sentry

```bash
# Install
pip install sentry-sdk

# In main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
    ],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "production")
)
```

### 5.2 Sentry Alert Configuration

- Set up alerts for:
  - Error rate > 5% in 5 minutes
  - New errors in last 24 hours
  - High-frequency errors

## 6. Health Checks & Alerting

### 6.1 Health Check Endpoints

The FastAPI app includes built-in health endpoints:

```
GET /health                    # Quick status check
GET /health/services           # Full service health report
GET /health/groq               # Check Groq API
GET /health/gemini             # Check Google Gemini
GET /health/qdrant             # Check Qdrant
GET /health/supabase           # Check Supabase
GET /health/rabbitmq           # Check RabbitMQ
GET /health/ollama             # Check Ollama
```

### 6.2 Prometheus Alerting Rules

Create `monitoring/prometheus/rules.yml`:

```yaml
groups:
  - name: insightstream_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(insightstream_http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, insightstream_http_request_duration_seconds) > 2
        for: 5m
        annotations:
          summary: "High request latency (p95 > 2s)"

      - alert: ServiceDown
        expr: up{job="insightstream-api"} == 0
        for: 1m
        annotations:
          summary: "InsightStream API is down"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        annotations:
          summary: "Database is down"

      - alert: QueueBacklog
        expr: rabbitmq_queue_messages{queue="ingestion_tasks"} > 1000
        for: 10m
        annotations:
          summary: "Large RabbitMQ queue backlog"
```

### 6.3 Alert Routing (AlertManager)

Setup notification channels:
- Email alerts for critical issues
- Slack webhooks for team notifications
- PagerDuty for on-call escalation

## 7. Distributed Tracing (Optional)

Using Jaeger for request tracing across services:

```python
# Install: pip install jaeger-client

from jaeger_client import Config

def init_jaeger_tracer(service_name):
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service_name,
    )
    return config.initialize_tracer()

tracer = init_jaeger_tracer('insightstream-api')
```

## 8. Log Retention & Cleanup

### 8.1 Docker Log Rotation

In docker-compose.yml:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 8.2 Elasticsearch Index Cleanup

```bash
# Delete indices older than 30 days
curl -X DELETE 'localhost:9200/insightstream-*' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "range": {
        "timestamp": {
          "lt": "now-30d"
        }
      }
    }
  }'
```

## 9. Monitoring Checklist

Daily checks:
- [ ] All services showing "healthy" in `/health/services`
- [ ] Error rate < 1% in last hour
- [ ] p95 latency < 1 second
- [ ] No critical alerts in Prometheus/AlertManager
- [ ] No new error patterns in Sentry

Weekly checks:
- [ ] Review top errors from past week
- [ ] Check database performance metrics
- [ ] Verify backup completion
- [ ] Review slow queries
- [ ] Check storage usage trends

Monthly review:
- [ ] Capacity planning (growth trends)
- [ ] Cost analysis (cloud spend)
- [ ] Security audit (access logs)
- [ ] Disaster recovery drill

## 10. Useful Commands

```bash
# View logs
tail -f /var/log/insightstream/app.log

# Search logs in Kibana
curl 'http://localhost:9200/insightstream-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match": {"severity": "ERROR"}}}'

# Query Prometheus
curl 'http://localhost:9090/api/v1/query?query=up'

# Check health
curl http://localhost:8000/health

# Full service health
curl http://localhost:8000/health/services | jq
```

## 11. Production Deployment Checklist

- [ ] Log aggregation system running and collecting logs
- [ ] Prometheus scraping all targets successfully
- [ ] Grafana dashboards created and shared
- [ ] Alert rules configured and tested
- [ ] Sentry DSN configured in environment
- [ ] Log retention policies set
- [ ] Health check endpoints verified
- [ ] Backup of monitoring configs in version control
- [ ] Team trained on using monitoring tools
- [ ] On-call runbook created with alert handling
