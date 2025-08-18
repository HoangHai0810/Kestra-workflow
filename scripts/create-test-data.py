
"""
Test Data Generator for S3 to TimescaleDB Migration
This script creates sample time-series data and uploads it to S3 for testing
"""

import boto3
import pandas as pd
import io
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_sample_data(start_date, end_date, num_devices=5):
    """Generate sample time-series data"""
    
    # Create time range with 1-minute intervals
    date_range = pd.date_range(start=start_date, end=end_date, freq='1min')
    
    data = []
    for timestamp in date_range:
        for device_id in range(1, num_devices + 1):
            # Generate realistic sensor data
            temperature = round(random.uniform(20, 30), 2)  # 20-30°C
            humidity = round(random.uniform(40, 60), 2)     # 40-60%
            pressure = round(random.uniform(1010, 1020), 2) # 1010-1020 hPa
            
            # Add some variation based on time
            if 6 <= timestamp.hour <= 18:  # Daytime
                temperature += random.uniform(2, 5)
                humidity -= random.uniform(5, 15)
            
            # Add some device-specific characteristics
            if device_id == 1:  # Production zone
                location = "zone_a"
                zone = "production"
            elif device_id == 2:  # Testing zone
                location = "zone_b"
                zone = "testing"
            elif device_id == 3:  # Development zone
                location = "zone_c"
                zone = "development"
            elif device_id == 4:  # Storage zone
                location = "zone_d"
                zone = "storage"
            else:  # Monitoring zone
                location = "zone_e"
                zone = "monitoring"
            
            # Create records for each metric
            data.extend([
                {
                    'timestamp': timestamp.isoformat() + 'Z',
                    'device_id': f'device_{device_id:03d}',
                    'metric_name': 'temperature',
                    'metric_value': max(0, temperature),
                    'location': location,
                    'zone': zone
                },
                {
                    'timestamp': timestamp.isoformat() + 'Z',
                    'device_id': f'device_{device_id:03d}',
                    'metric_name': 'humidity',
                    'metric_value': max(0, min(100, humidity)),
                    'location': location,
                    'zone': zone
                },
                {
                    'timestamp': timestamp.isoformat() + 'Z',
                    'device_id': f'device_{device_id:03d}',
                    'metric_name': 'pressure',
                    'metric_value': pressure,
                    'location': location,
                    'zone': zone
                }
            ])
    
    return pd.DataFrame(data)

def upload_to_s3(df, bucket_name, key, aws_access_key_id, aws_secret_access_key, region='us-east-1'):
    """Upload DataFrame to S3 as CSV"""
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
        
        # Convert DataFrame to CSV string
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=csv_content.encode('utf-8'),
            ContentType='text/csv'
        )
        
        print(f"✅ Successfully uploaded {len(df)} records to s3://{bucket_name}/{key}")
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to S3: {str(e)}")
        return False

def main():
    """Main function to generate and upload test data"""
    
    print("🚀 S3 Test Data Generator for TimescaleDB Migration")
    print("=" * 60)
    
    # Get configuration from environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    s3_prefix = os.getenv('S3_PREFIX', 'data/')
    
    
    # Ensure prefix ends with slash
    if not s3_prefix.endswith('/'):
        s3_prefix += '/'
    
    # Generate test data for the last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Generating data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Generate sample data
    print("🔧 Generating sample time-series data...")
    df = generate_sample_data(start_date, end_date, num_devices=5)
    
    print(f"📊 Generated {len(df)} records")
    print(f"📈 Data spans {len(df['timestamp'].unique())} unique timestamps")
    print(f"🏭 Covers {df['device_id'].nunique()} devices")
    print(f"📍 Across {df['location'].nunique()} locations")
    
    # Show sample data
    print("\n📋 Sample data:")
    print(df.head(10).to_string(index=False))
    
    # Create different test files
    test_files = [
        {
            'key': f'{s3_prefix}sample-metrics.csv',
            'description': 'Full dataset for testing'
        },
        {
            'key': f'{s3_prefix}daily-metrics-2024-01-15.csv',
            'description': 'Daily dataset for scheduled workflow testing'
        },
        {
            'key': f'{s3_prefix}hourly-metrics-2024-01-15.csv',
            'description': 'Hourly dataset for smaller batch testing'
        }
    ]
    
    # Upload each test file
    for test_file in test_files:
        print(f"\n📤 Uploading {test_file['description']}...")
        
        if 'daily' in test_file['key']:
            # Daily data (last 24 hours)
            daily_start = end_date - timedelta(days=1)
            daily_df = generate_sample_data(daily_start, end_date, num_devices=3)
            success = upload_to_s3(daily_df, s3_bucket, test_file['key'], 
                                 aws_access_key_id, aws_secret_access_key, aws_region)
        elif 'hourly' in test_file['key']:
            # Hourly data (last 1 hour)
            hourly_start = end_date - timedelta(hours=1)
            hourly_df = generate_sample_data(hourly_start, end_date, num_devices=2)
            success = upload_to_s3(hourly_df, s3_bucket, test_file['key'], 
                                 aws_access_key_id, aws_secret_access_key, aws_region)
        else:
            # Full dataset
            success = upload_to_s3(df, s3_bucket, test_file['key'], 
                                 aws_access_key_id, aws_secret_access_key, aws_region)
        
        if success:
            print(f"   📁 File: s3://{s3_bucket}/{test_file['key']}")
    
    print("\n🎉 Test data generation complete!")
    print("\n📋 Next steps:")
    print("1. Go to Kestra UI: http://localhost:8080")
    print("2. Execute the 's3-to-timescaledb-migration' workflow")
    print("3. Use these test files:")
    for test_file in test_files:
        print(f"   - {test_file['key']} ({test_file['description']})")
    
    print("\n🔧 Workflow inputs:")
    print(f"   - s3_bucket: {s3_bucket}")
    print(f"   - s3_key: {s3_prefix}sample-metrics.csv")
    print("   - table_name: test_metrics")

if __name__ == "__main__":
    main()
