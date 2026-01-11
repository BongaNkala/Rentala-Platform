import os
import sys

def configure_environment(platform='web'):
    """Configure environment for different platforms"""
    
    env_vars = {
        'web': {
            'PLATFORM': 'web',
            'CORS_ALLOWED_ORIGINS': 'http://localhost:8000,http://127.0.0.1:8000',
        },
        'desktop': {
            'PLATFORM': 'desktop',
            'CORS_ALLOWED_ORIGINS': 'http://localhost:3000,http://127.0.0.1:3000,app://localhost',
            'ENABLE_DESKTOP_FEATURES': 'True',
        },
        'mobile': {
            'PLATFORM': 'mobile',
            'CORS_ALLOWED_ORIGINS': 'http://localhost:19006,exp://localhost:19000',
            'ENABLE_MOBILE_FEATURES': 'True',
        }
    }
    
    config = env_vars.get(platform, env_vars['web'])
    
    for key, value in config.items():
        os.environ[key] = value
    
    print(f"Configured for {platform.upper()} platform")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        configure_environment(sys.argv[1])
    else:
        configure_environment('web')
