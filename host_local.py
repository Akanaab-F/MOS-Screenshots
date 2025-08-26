#!/usr/bin/env python3
"""
Production-ready local hosting for Route Screenshot Generator
"""

import os
import sys
from waitress import serve
from app_with_redis_alt import app, start_worker

def main():
    print("🚀 Starting Route Screenshot Generator (Production Mode)")
    print("📝 This version is optimized for local/network hosting")
    print()
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Start background worker
    start_worker()
    
    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')  # 0.0.0.0 allows external connections
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Server will be available at:")
    print(f"   Local: http://localhost:{port}")
    print(f"   Network: http://[YOUR_IP]:{port}")
    print()
    print("📊 To find your IP address, run: ipconfig")
    print("🔒 Make sure your firewall allows connections on port", port)
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    # Start production server
    serve(app, host=host, port=port, threads=4)

if __name__ == '__main__':
    main()
