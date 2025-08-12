import base64
import os
from pathlib import Path

def encode_secret(secret):
    """Encode secret to Base64"""
    return base64.b64encode(secret.encode('utf-8')).decode('utf-8')

def load_env_file():
    """Load .env file and parse to dictionary"""
    env_file = Path('.env')
    if not env_file.exists():
        print("File .env not found!")
        return None
    
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    return env_vars

def main():
    env_vars = load_env_file()
    if not env_vars:
        return
    
    secrets_to_encode = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_REGION',
        'CLICKHOUSE_USER',
        'CLICKHOUSE_PASSWORD',
        'ES_USER',
        'ES_PASSWORD'
    ]
    
    for secret_name in secrets_to_encode:
        if secret_name in env_vars:
            original_value = env_vars[secret_name]
            encoded_value = encode_secret(original_value)
            print(f"{secret_name}_B64={encoded_value}")
            with open('.env', 'a', encoding='utf-8') as f:
                f.write(f"{secret_name}_B64='{encoded_value}'\n")
        else:
            print(f"{secret_name} not found in .env file")

if __name__ == "__main__":
    main()
