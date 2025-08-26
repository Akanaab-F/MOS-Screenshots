# 🚀 Hosting Guide for Route Screenshot Generator

## 📋 **Hosting Options Overview**

| Option | Difficulty | Cost | Best For |
|--------|------------|------|----------|
| **Local/Network** | ⭐ Easy | Free | Testing, Internal use |
| **Heroku** | ⭐⭐ Medium | Free-$7/month | Small teams, prototypes |
| **Railway** | ⭐⭐ Medium | Free-$5/month | Quick deployment |
| **DigitalOcean** | ⭐⭐⭐ Hard | $5/month | Production, full control |
| **AWS/GCP** | ⭐⭐⭐⭐ Expert | Variable | Enterprise, scaling |

---

## 🏠 **Option 1: Local/Network Hosting**

### **Quick Start (Development)**
```bash
# Install production dependencies
pip install waitress

# Run production server
python host_local.py
```

### **Network Access Setup**
1. **Find your IP address:**
   ```bash
   # Windows
   ipconfig
   
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   ```

2. **Configure firewall:**
   - Allow port 5000 in Windows Firewall
   - Or change port: `set PORT=8080 && python host_local.py`

3. **Access from other devices:**
   - `http://192.168.1.100:5000` (replace with your IP)

### **Production Setup**
```bash
# Install as Windows Service
pip install pywin32
python -m pip install waitress

# Create service script
python create_service.py
```

---

## ☁️ **Option 2: Heroku Hosting (Recommended)**

### **Step 1: Prepare for Deployment**
```bash
# Create deployment files
python deploy_heroku.py

# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

### **Step 2: Deploy**
```bash
# Login to Heroku
heroku login

# Deploy
python deploy_heroku.py deploy

# Or manual deployment:
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
git push heroku main
```

### **Step 3: Configure**
```bash
# Set environment variables
heroku config:set SECRET_KEY=your-super-secret-key
heroku config:set FLASK_ENV=production

# Open the app
heroku open
```

### **Cost:**
- **Free tier:** 550-1000 dyno hours/month
- **Paid:** $7/month for unlimited usage

---

## 🚂 **Option 3: Railway Hosting**

### **Step 1: Setup**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect and deploy

### **Step 2: Configure**
```bash
# Add environment variables in Railway dashboard:
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### **Cost:**
- **Free:** $5 credit/month
- **Paid:** Pay-as-you-use

---

## 🐳 **Option 4: Docker Deployment**

### **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app_with_redis_alt:app"]
```

### **Deploy with Docker**
```bash
# Build image
docker build -t route-screenshot-generator .

# Run container
docker run -p 5000:5000 route-screenshot-generator

# Or with docker-compose
docker-compose up -d
```

---

## ☁️ **Option 5: Cloud Platforms**

### **DigitalOcean App Platform**
1. Create account at [digitalocean.com](https://digitalocean.com)
2. Connect GitHub repository
3. Choose Python environment
4. Set environment variables
5. Deploy

### **AWS Elastic Beanstalk**
1. Install AWS CLI
2. Create `Dockerfile` or `requirements.txt`
3. Deploy:
```bash
eb init
eb create
eb deploy
```

### **Google Cloud Run**
1. Install Google Cloud CLI
2. Deploy:
```bash
gcloud run deploy --source .
```

---

## 🔧 **Production Configuration**

### **Environment Variables**
```bash
# Required
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0

# Optional
FLASK_ENV=production
PORT=5000
HOST=0.0.0.0
```

### **Database Setup**
```bash
# For PostgreSQL (recommended for production)
pip install psycopg2-binary

# Update app configuration
DATABASE_URL=postgresql://username:password@localhost/route_screenshots
```

### **Security Considerations**
1. **Change default secret key**
2. **Use HTTPS in production**
3. **Set up proper user authentication**
4. **Configure rate limiting**
5. **Set up monitoring and logging**

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**
```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow()})
```

### **Logging**
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### **Backup Strategy**
```bash
# Database backup
pg_dump $DATABASE_URL > backup.sql

# File backup
tar -czf screenshots_backup.tar.gz screenshots/
```

---

## 🚀 **Quick Deployment Checklist**

- [ ] Choose hosting platform
- [ ] Set up environment variables
- [ ] Configure database
- [ ] Set up Redis/Celery (if needed)
- [ ] Test deployment
- [ ] Configure domain (optional)
- [ ] Set up monitoring
- [ ] Create backup strategy

---

## 💡 **Recommendations**

### **For Testing/Development:**
- **Local hosting** with `python host_local.py`

### **For Small Teams:**
- **Heroku** or **Railway** (easiest setup)

### **For Production:**
- **DigitalOcean** or **AWS** (more control)

### **For Enterprise:**
- **AWS/GCP** with proper infrastructure

---

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **Port already in use:**
   ```bash
   # Change port
   set PORT=8080 && python host_local.py
   ```

2. **Database connection errors:**
   - Check `DATABASE_URL` format
   - Ensure database is running

3. **Chrome/Selenium issues:**
   - Install Chrome dependencies
   - Use headless mode in production

4. **Memory issues:**
   - Increase server memory
   - Optimize image processing

### **Support:**
- Check application logs
- Monitor system resources
- Test with smaller datasets first

---

## 📞 **Need Help?**

1. Check the application logs
2. Verify environment variables
3. Test locally first
4. Start with simple hosting option
5. Scale up as needed

**Remember:** Start simple, then scale up as your needs grow! 🚀
