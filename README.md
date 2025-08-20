# Kestra Workflow - S3 JSON Ingestion Pipeline

A production-ready data pipeline built with Kestra that automatically processes JSON files uploaded to S3 and ingests extracted data into multiple specialized databases in parallel.

## Overview

This project implements an intelligent data pipeline that monitors an S3 bucket for new JSON files containing Google Lens API results, then automatically processes and distributes the data across multiple database technologies optimized for different use cases:

- **TimescaleDB**: Time-series analytics and historical data storage with hypertables
- **ClickHouse**: High-performance analytical queries and real-time aggregations
- **Elasticsearch**: Full-text search and complex aggregations
- **Qdrant**: Vector similarity search and machine learning workloads

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌──────────────────────────────────┐
│     S3      │───▶│   Kestra    │───▶│        Data Storage Layer        │
│             │    │  Workflow   │    │                                  │
│ JSON Files  │    │  Engine     │    │  ┌─────────────┐ ┌─────────────┐ │
│ (Auto-trigger)│  └─────────────┘    │  │TimescaleDB  │ │ ClickHouse  │ │
└─────────────┘                       │  │(Time-Series)│ │(Analytics)  │ │
                                      │  └─────────────┘ └─────────────┘ │
                                      │  ┌─────────────┐ ┌─────────────┐ │
                                      │  │Elasticsearch│ │   Qdrant    │ │
                                      │  │  (Search)   │ │  (Vectors)  │ │
                                      └──────────────────────────────────┘
```

### Data Flow

1. **Trigger**: S3 trigger monitors bucket every minute for new JSON files
2. **Ingestion**: JSON files are automatically detected and processed
3. **Parsing**: Google Lens API response data is extracted and validated
4. **Transformation**: Data is structured for each target database
5. **Parallel Distribution**: Data is simultaneously written to all databases
6. **File Management**: Processed files are moved to `processed/` folder
7. **Monitoring**: Success/failure metrics are logged and tracked

## Prerequisites

### System Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: Minimum 10GB available disk space
- **Network**: Internet access for Docker image downloads

### External Services
- **AWS S3**: For source data storage
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

The main workflow (`flows/s3-json-ingestion.yaml`) is configured with:

| Parameter   |             Value           |            Description          |
|-------------|-----------------------------|---------------------------------|
| `s3_bucket` | `static-staging.flowio.app` | S3 bucket containing JSON files |
| `s3_prefix` | `resources/kestra_test/`    | S3 prefix for monitoring        |
| `table_name`|  Configurable via inputs    | Target table/collection name    |

### S3 Trigger Configuration

```yaml
triggers:
  - id: s3_trigger
    type: io.kestra.plugin.aws.s3.Trigger
    bucket: "static-staging.flowio.app"
    prefix: "resources/kestra_test/"
    interval: PT1M                    # Check every minute
    action: MOVE                      # Move files after processing
    moveTo:
        key: "resources/kestra_test/processed/{{ trigger.objects[0].key | replace('resources/kestra_test/', '') }}"
    filter: FILES                     # Only process files (not folders)
    maxKeys: 1                        # Process one file at a time
```

### Database Schemas

#### TimescaleDB Schema
```sql
CREATE TABLE IF NOT EXISTS {{ inputs.table_name }} (
    id SERIAL,                        -- Auto-incrementing primary key
    timestamp TIMESTAMPTZ NOT NULL,   -- Measurement timestamp
    source_image_url TEXT,            -- Source image URL
    search_type VARCHAR(100),         -- Search type (visual, exact, etc.)
    search_query TEXT,                -- Search query text
    result_position INTEGER,          -- Result position in API response
    title TEXT,                       -- Product/result title
    link TEXT,                        -- Product/result link
    source TEXT,                      -- Source website
    price TEXT,                       -- Price as text
    extracted_price DECIMAL(10,2),    -- Numeric price value
    currency VARCHAR(10),             -- Currency code
    stock_information TEXT,           -- Stock availability info
    thumbnail TEXT,                   -- Thumbnail image URL
    image_link TEXT,                  -- Main image URL
    image_width INTEGER,              -- Image width in pixels
    image_height INTEGER,             -- Image height in pixels
    extensions TEXT[],                -- File extensions
    image_url TEXT,                   -- Alternative image URL
    image_size_bytes BIGINT,          -- Image file size
    feature_type VARCHAR(100),        -- Feature type
    url TEXT,                         -- Alternative URL
    score DECIMAL(3,2),               -- Confidence score
    full_matches INTEGER,             -- Number of full matches
    partial_matches INTEGER,          -- Number of partial matches
    similar_images INTEGER,            -- Number of similar images
    web_entities TEXT,                -- Web entities found
    best_guess_labels TEXT,           -- Best guess labels
    PRIMARY KEY (timestamp, id)
);
```

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
4. The `s3-json-ingestion` workflow will be automatically available