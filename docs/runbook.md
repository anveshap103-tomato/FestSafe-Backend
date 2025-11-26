# FestSafe AI Runbook

## Incident Response Procedures

### Model Drift

**Symptoms:**
- Forecast accuracy metrics degrading
- High prediction errors
- Alert from monitoring system

**Steps:**
1. Check MLflow for recent model performance metrics
2. Compare current model performance to baseline
3. If drift detected:
   - Trigger model retraining pipeline
   - Validate new model on test set
   - Deploy new model to staging
   - A/B test if needed
   - Roll out to production

**Rollback:**
```bash
kubectl set image deployment/ml-service ml-service=festsafe/ml-service:previous-version -n festsafe
```

### Data Pipeline Failure

**Symptoms:**
- No new observations in database
- Alerts from data ingestion workers
- Missing external API data

**Steps:**
1. Check worker logs:
   ```bash
   kubectl logs -f deployment/workers -n festsafe
   ```
2. Verify external API connectivity
3. Check RabbitMQ queue status
4. Restart workers if needed:
   ```bash
   kubectl rollout restart deployment/workers -n festsafe
   ```
5. Replay failed messages from dead letter queue

**Prevention:**
- Monitor queue depth
- Set up alerts for queue backlog
- Implement circuit breakers for external APIs

### High Latency

**Symptoms:**
- API response times > 500ms
- Dashboard loading slowly
- User complaints

**Steps:**
1. Check Prometheus metrics for latency
2. Identify bottleneck:
   - Database queries: Check slow query log
   - ML inference: Check model service metrics
   - External APIs: Check response times
3. Scale up services if needed:
   ```bash
   kubectl scale deployment/backend --replicas=5 -n festsafe
   ```
4. Check database connection pool
5. Review Redis cache hit rate

**Optimization:**
- Add database indexes
- Increase cache TTL
- Optimize model inference
- Use read replicas for database

### Database Issues

**Symptoms:**
- Connection errors
- Slow queries
- High CPU/memory usage

**Steps:**
1. Check database status:
   ```bash
   kubectl exec -it postgres-pod -n festsafe -- psql -U festsafe -c "SELECT * FROM pg_stat_activity;"
   ```
2. Check for long-running queries
3. Review connection pool settings
4. Scale database if needed
5. Check disk space

**Backup & Recovery:**
- Daily automated backups
- Point-in-time recovery available
- Test restore procedures monthly

### Security Incident

**Symptoms:**
- Unauthorized access attempts
- Unusual API activity
- Data breach alerts

**Steps:**
1. Immediately revoke affected tokens
2. Review audit logs
3. Check for data exfiltration
4. Notify security team
5. Rotate secrets:
   ```bash
   kubectl create secret generic festsafe-secrets --from-literal=secret-key=new-key -n festsafe --dry-run=client -o yaml | kubectl apply -f -
   ```
6. Review access logs
7. Update security policies if needed

## Monitoring & Alerts

### Key Metrics

- **API Latency**: P95 < 500ms
- **Error Rate**: < 1%
- **Database Connections**: < 80% of max
- **Model Accuracy**: MAE < 2.0
- **Queue Depth**: < 1000 messages

### Alert Channels

- **Critical**: PagerDuty / On-call rotation
- **Warning**: Slack #alerts channel
- **Info**: Email digest

## Deployment Procedures

### Rolling Update

```bash
# Update backend
kubectl set image deployment/backend backend=festsafe/backend:v1.1.0 -n festsafe
kubectl rollout status deployment/backend -n festsafe

# Update frontend
kubectl set image deployment/frontend frontend=festsafe/frontend:v1.1.0 -n festsafe
kubectl rollout status deployment/frontend -n festsafe
```

### Rollback

```bash
kubectl rollout undo deployment/backend -n festsafe
kubectl rollout undo deployment/frontend -n festsafe
```

## Maintenance Windows

- **Weekly**: Database maintenance (Sundays 2-4 AM UTC)
- **Monthly**: Security updates
- **Quarterly**: Model retraining

## Contact Information

- **On-Call**: See PagerDuty
- **Engineering Lead**: engineering@festsafe.ai
- **Security**: security@festsafe.ai


