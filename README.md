# Kestra Workflow - Multi-Database Data Pipeline

A production-ready data pipeline built with Kestra that demonstrates enterprise-grade data ingestion, transformation, and storage across multiple database technologies.

## Overview

This project implements a robust data pipeline that processes CSV data from S3 and distributes it across multiple specialized databases, each optimized for different use cases:

- **TimescaleDB**: Time-series analytics and historical data storage
- **ClickHouse**: High-performance analytical queries and real-time aggregations
- **Elasticsearch**: Full-text search and complex aggregations
- **Qdrant**: Vector similarity search and machine learning workloads

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌──────────────────────────────────┐
│     S3      │───▶│   Kestra    │───▶│        Data Storage Layer        │
│             │    │  Workflow   │    │                                  │
└─────────────┘    │  Engine     │    │  ┌─────────────┐ ┌─────────────┐ │
                   └─────────────┘    │  │TimescaleDB  │ │ ClickHouse  │ │
                                      │  │(Time-Series)│ │(Analytics)  │ │
                                      │  └─────────────┘ └─────────────┘ │
                                      │  ┌─────────────┐ ┌─────────────┐ │
                                      │  │Elasticsearch│ │   Qdrant    │ │
                                      │  │  (Search)   │ │  (Vectors)  │ │
                                      │  └─────────────┘ └─────────────┘ │
                                      └──────────────────────────────────┘
```

### Data Flow

1. **Ingestion**: CSV files are downloaded from S3
2. **Processing**: Data is parsed and validated with header handling
3. **Transformation**: Metrics are converted to appropriate formats for each database
4. **Distribution**: Data is simultaneously written to all target databases
5. **Verification**: Success/failure metrics are logged and monitored

## Features

### Core Capabilities
- **Multi-format Support**: CSV ingestion with configurable delimiters and automatic header handling
- **Parallel Processing**: Simultaneous writes to all databases using parallel task execution
- **Error Handling**: Comprehensive error handling with detailed logging and status reporting
- **Scheduling**: Configurable cron-based execution (default: every 6 hours)
- **Monitoring**: Built-in health checks and performance metrics for each database

### Database Optimizations
- **TimescaleDB**: Hypertables for time-series data with automatic partitioning and TTL
- **ClickHouse**: MergeTree engine with optimized partitioning and batch processing
- **Elasticsearch**: Optimized mappings for search and analytics with bulk indexing
- **Qdrant**: 6-dimensional vectors for similarity search and ML workloads

### Enterprise Features
- **Security**: Environment-based secret management for all database credentials
- **Scalability**: Docker-based deployment with health monitoring and proper networking
- **Observability**: Structured logging and metrics collection for all operations
- **Maintenance**: Automated cleanup and data lifecycle management

## Prerequisites

### System Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: Minimum 10GB available disk space
- **Network**: Internet access for Docker image downloads

### Software Dependencies
- **Python**: 3.8+ (for local development)
- **curl**: For health checks and API testing
- **Git**: For version control

### External Services
- **AWS S3**: For source data (configured via environment variables)
- **Network Access**: To required AWS endpoints

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd kestra-workflow
```

### 2. Environment Setup
Create a `.env` file in the project root:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Database Credentials
CLICKHOUSE_USER=admin
CLICKHOUSE_PASSWORD=admin123
ES_USER=elastic
ES_PASSWORD=elastic123

# PostgreSQL/TimescaleDB
POSTGRES_DB=kestra_data
POSTGRES_USER=kestra_user
POSTGRES_PASSWORD=kestra_password
POSTGRES_PORT=5432

# Kestra Configuration
KESTRA_USERNAME=admin
KESTRA_PASSWORD=admin
KESTRA_PORT=8080

# Service Ports
CLICKHOUSE_PORT=8123
ELASTICSEARCH_PORT=9200
QDRANT_HTTP_PORT=6333
```

### 3. Start Services
```bash
# Start all services
docker compose up -d

# Verify services are running
docker compose ps
```

## Configuration

### Workflow Parameters

The main workflow (`flows/s3-csv-ingestion.yaml`) accepts the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `s3_bucket` | String | `static-staging.flowio.app` | S3 bucket containing source data |
| `s3_key` | String | `resources/kestra-test/sample-metrics.csv` | S3 object key for CSV file |
| `table_name` | String | `test_metrics_data` | Target table/collection name |
| `delimiter` | String | `,` | CSV delimiter character |

### Database Schemas

All databases use a consistent schema:

```sql
CREATE TABLE metrics (
    timestamp TIMESTAMPTZ,      -- Measurement timestamp
    device_id TEXT,             -- Device identifier
    metric_name TEXT,           -- Metric name/type
    metric_value DOUBLE PRECISION, -- Numeric value
    location TEXT,              -- Geographic location
    zone TEXT                   -- Zone/region
);
```

### Vector Configuration (Qdrant)

Qdrant collections are configured with:
- **Vector Size**: 6 dimensions for comprehensive metric representation
- **Distance Metric**: Cosine similarity for optimal similarity search
- **Storage**: On-disk payloads for large datasets
- **Indexing**: Optimized for similarity search and ML workloads

## Usage

### Starting the Pipeline

```bash
# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f kestra
```

### Accessing Kestra UI

1. Open browser to: http://localhost:8080
2. Login with credentials from `.env` file
3. Navigate to Flows section
4. The `s3-csv-ingestion` workflow will be automatically available

### Manual Execution

```bash
# Execute workflow manually via API
curl -X POST \
  -H "Content-Type: application/json" \
  -u "admin:admin" \
  -d '{"inputs": {"table_name": "my_metrics"}}' \
  http://localhost:8080/api/v1/executions/trigger/com.flowio/s3-csv-ingestion
```

### Monitoring Execution

```bash
# View execution logs
docker compose logs -f kestra

# Check database connections
docker compose exec kestra curl -f http://host.docker.internal:6333/collections
```

## API Reference

### Kestra API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/flows` | GET | List all available workflows |
| `/api/v1/executions` | GET | List workflow executions |
| `/api/v1/executions/{id}` | GET | Get execution details |
| `/api/v1/executions/trigger/{namespace}/{id}` | POST | Trigger workflow execution |

### Database Health Checks

| Service | Endpoint | Description |
|---------|----------|-------------|
| TimescaleDB | `postgres:5432` | PostgreSQL health check |
| ClickHouse | `host.docker.internal:8123/ping` | HTTP ping endpoint |
| Elasticsearch | `host.docker.internal:9200/_cluster/health` | Cluster health status |
| Qdrant | `host.docker.internal:6333/collections` | Collections endpoint |

## Monitoring & Logging

### Health Monitoring
```bash
# Check all services
docker compose ps

# Monitor specific service
docker compose logs -f qdrant

# Health check endpoints
curl http://localhost:8080/health
curl http://localhost:6333/collections
```

### Log Analysis
```bash
# View all logs
docker compose logs

# Filter by service
docker compose logs kestra | grep "ERROR"

# Real-time monitoring
docker compose logs -f --tail=100
```

### Performance Metrics
- **Execution Time**: Tracked per task and overall workflow
- **Success Rate**: Monitored across all database operations
- **Resource Usage**: Docker container metrics
- **Database Performance**: Connection pool and query metrics

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check Docker resources
docker system df
docker stats

# Verify port availability
netstat -tulpn | grep :8080
```

#### Database Connection Errors
```bash
# Test network connectivity (using host.docker.internal)
docker compose exec kestra ping host.docker.internal
docker compose exec kestra curl -f http://host.docker.internal:6333/collections

# Check service logs
docker compose logs qdrant
```

#### Workflow Execution Failures
```bash
# Check Kestra logs
docker compose logs -f kestra

# Verify environment variables
docker compose exec kestra env | grep AWS
```

### Debug Commands

```bash
# Enter service container
docker compose exec kestra bash

# Check file permissions
docker compose exec kestra ls -la /app/flows

# Test database connections
docker compose exec kestra python3 -c "
import urllib.request
response = urllib.request.urlopen('http://host.docker.internal:6333/collections')
print(response.read().decode())
"
```

## Development

### Local Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd kestra-workflow

# Create development environment
cp .env.example .env
# Edit .env with your credentials

# Start development services
docker compose -f docker-compose.dev.yml up -d
```

### Adding New Workflows

1. Create new YAML file in `flows/` directory
2. Follow Kestra workflow syntax
3. Restart Kestra service: `docker compose restart kestra`
4. Verify workflow appears in UI

### Testing

```bash
# Run workflow tests
docker compose exec kestra python3 -m pytest tests/

# Validate YAML syntax
docker compose exec kestra python3 -c "
import yaml
with open('/app/flows/s3-csv-ingestion.yaml') as f:
    yaml.safe_load(f)
print('YAML syntax is valid')
"
```

## Contributing

### Development Guidelines

1. **Code Style**: Follow existing YAML and Python conventions
2. **Testing**: Test workflows locally before committing
3. **Documentation**: Update README for new features
4. **Commits**: Use descriptive commit messages

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-workflow`
3. Make changes and test locally
4. Commit changes: `git commit -m "Add new workflow feature"`
5. Push to branch: `git push origin feature/new-workflow`
6. Submit pull request with detailed description

### Issue Reporting

When reporting issues, please include:
- **Environment**: Docker version, OS, etc.
- **Steps**: Detailed reproduction steps
- **Logs**: Relevant error logs and stack traces
- **Expected vs Actual**: Clear description of expected behavior

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- **Issues**: Create GitHub issue
- **Documentation**: Check Kestra docs at https://kestra.io/docs/
- **Community**: Join Kestra community discussions

---

**Note**: This is a production-ready template. Customize configurations, security settings, and monitoring based on your specific deployment requirements.