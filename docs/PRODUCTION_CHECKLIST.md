# InsightStream AI - Production Deployment Checklist

## Pre-Deployment

### Code Review & Testing
- [ ] All unit tests pass: `pytest backend/tests/`
- [ ] Integration tests pass: `pytest backend/tests/integration/`
- [ ] Load testing completed on critical endpoints
- [ ] Security audit completed (OWASP Top 10)
- [ ] Code review completed by team lead
- [ ] Linting passes: `flake8 backend/`
- [ ] Type checking passes: `mypy backend/`

### Documentation
- [ ] API documentation updated in Swagger/OpenAPI
- [ ] Environment variables documented in `.env.example`
- [ ] Deployment guide completed
- [ ] Monitoring setup documented
- [ ] Runbook created for common incidents
- [ ] Architecture diagrams updated

### Configuration
- [ ] All secrets stored in environment variables (no hardcoded values)
- [ ] Database migrations tested on staging
- [ ] Backup strategy verified
- [ ] SSL/TLS certificates valid
- [ ] CORS origins configured correctly for production
- [ ] Rate limiting configured
- [ ] API keys rotated (new keys for production)

### External Services
- [ ] Groq API account verified with production quota
- [ ] Google Gemini API enabled and quota verified
- [ ] Qdrant instance provisioned (or self-hosted ready)
- [ ] Supabase project created with backups enabled
- [ ] RabbitMQ cluster configured and tested
- [ ] Ollama deployment plan finalized
- [ ] Monitoring/alerting tools configured

## Infrastructure Setup

### Docker & Containerization
- [ ] Dockerfiles optimized for production (multi-stage builds)
- [ ] Docker images built and tested
- [ ] Docker registry configured (ECR, Docker Hub, etc.)
- [ ] Docker images tagged with version
- [ ] Docker images scanned for vulnerabilities
- [ ] docker-compose.prod.yml validated

### Kubernetes (if applicable)
- [ ] Kubernetes manifests created and validated
- [ ] Helm charts created (if using Helm)
- [ ] Resource limits and requests set
- [ ] Pod security policies configured
- [ ] Network policies configured
- [ ] Ingress controller configured
- [ ] Storage classes configured for persistence

### Database
- [ ] Supabase backups enabled and tested
- [ ] PostgreSQL connection pool configured
- [ ] Database indexing optimized
- [ ] Query performance profiled
- [ ] Migration scripts tested
- [ ] Rollback procedures documented

### Monitoring & Logging
- [ ] Prometheus scrape configs ready
- [ ] Grafana dashboards created
- [ ] Log aggregation (ELK, Datadog, etc.) configured
- [ ] Alert thresholds defined and tested
- [ ] Error tracking (Sentry, etc.) configured
- [ ] Uptime monitoring configured
- [ ] Performance monitoring baseline established

## Deployment Day

### Pre-Deployment Checks
- [ ] Staging environment matches production setup exactly
- [ ] All deployment scripts tested on staging
- [ ] Database backups created
- [ ] Current version tagged in Git: `git tag v0.2.0`
- [ ] Deployment plan reviewed with team
- [ ] Rollback plan reviewed and tested
- [ ] Stakeholders notified of deployment window
- [ ] On-call team assigned and briefed

### Deployment Steps
- [ ] Stop old application instances gracefully
- [ ] Run database migrations (if any)
- [ ] Deploy new application version
- [ ] Verify health check endpoints respond
- [ ] Run smoke tests:
  - [ ] `/health` endpoint returns 200
  - [ ] `/health/services` shows all services healthy
  - [ ] API can process a test request
  - [ ] Database queries work
  - [ ] External API calls work
- [ ] Monitor error rates and latency
- [ ] Verify logs show no critical errors
- [ ] Check CPU/memory usage is normal

### Post-Deployment Checks
- [ ] All health endpoints passing
- [ ] No spike in error rates
- [ ] No spike in latency
- [ ] Database connections healthy
- [ ] Cache working correctly
- [ ] Message queue processing messages
- [ ] Background jobs running
- [ ] User-facing features tested manually

## Post-Deployment

### Monitoring (First 24 hours)
- [ ] Alert system functional
- [ ] Error rates remain normal
- [ ] No unusual traffic patterns
- [ ] Database performance acceptable
- [ ] External API quotas within limits
- [ ] Logs reviewed for warnings
- [ ] User reports reviewed

### Monitoring (First Week)
- [ ] Weekly performance metrics reviewed
- [ ] Database growth monitored
- [ ] Cost monitoring (cloud spend)
- [ ] Security scanning scheduled
- [ ] Backup integrity verified
- [ ] Disaster recovery plan reviewed

### Ongoing
- [ ] Performance metrics collected
- [ ] User feedback collected
- [ ] Security updates monitored and applied
- [ ] Dependency updates planned
- [ ] Capacity planning ongoing
- [ ] Documentation kept up to date

## Rollback Procedure (if issues occur)

1. Alert team and stop traffic (if possible)
2. Review error logs and metrics
3. Decide: continue troubleshooting OR rollback
4. If rollback:
   ```bash
   # Revert to previous version
   git checkout <previous-tag>
   docker build -t insightstream:v0.1.0 .
   # Redeploy with previous version
   ```
5. Run full health check suite
6. Verify system stability for 30 minutes
7. Post-mortem meeting to discuss root cause

## Production Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-Call | [TBD] | [TBD] | [TBD] |
| Database Admin | [TBD] | [TBD] | [TBD] |
| API Owner | [TBD] | [TBD] | [TBD] |
| Infrastructure | [TBD] | [TBD] | [TBD] |

## Sign-Off

- [ ] Tech Lead: _________________ Date: _______
- [ ] DevOps Lead: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______
