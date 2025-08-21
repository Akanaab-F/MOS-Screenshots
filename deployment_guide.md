# Deployment Guide for Non-Technical Users

This guide will help you deploy the Route Screenshot Generator system so that multiple users can access it independently through a web browser.

## Option 1: Cloud Deployment (Recommended)

### Using Railway (Easiest)

1. **Create a Railway account**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Deploy the application**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect the Docker setup

3. **Configure environment variables**
   - Go to your project settings
   - Add these environment variables:
     - `SECRET_KEY`: Generate a random string (e.g., "my-super-secret-key-123")
     - `FLASK_ENV`: Set to "production"

4. **Access your application**
   - Railway will provide a URL (e.g., `https://your-app.railway.app`)
   - Share this URL with your users

### Using Heroku

1. **Create a Heroku account**
   - Go to [heroku.com](https://heroku.com)
   - Sign up for a free account

2. **Install Heroku CLI**
   - Download from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

3. **Deploy the application**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

4. **Add Redis add-on**
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```

5. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set FLASK_ENV="production"
   ```

## Option 2: Local Server Deployment

### Requirements
- A computer that can run 24/7
- Windows, macOS, or Linux
- At least 4GB RAM
- Stable internet connection

### Step-by-Step Setup

1. **Install Docker Desktop**
   - Download from [docker.com](https://docker.com)
   - Install and start Docker Desktop

2. **Download the application**
   - Download the ZIP file of this project
   - Extract it to a folder on your computer

3. **Open Command Prompt/Terminal**
   - Navigate to the project folder
   - Run: `docker-compose up -d`

4. **Access the application**
   - Open your web browser
   - Go to `http://localhost:5000`
   - Register the first admin account

5. **Make it accessible to others**
   - Find your computer's IP address
   - Configure your firewall to allow port 5000
   - Share the URL: `http://YOUR_IP_ADDRESS:5000`

## Option 3: VPS Deployment

### Using DigitalOcean

1. **Create a DigitalOcean account**
   - Go to [digitalocean.com](https://digitalocean.com)
   - Sign up and add payment method

2. **Create a Droplet**
   - Click "Create" → "Droplets"
   - Choose Ubuntu 20.04
   - Select Basic plan ($5/month minimum)
   - Choose a datacenter close to your users

3. **Connect to your server**
   - Use the provided IP address
   - Connect via SSH or use the web console

4. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

5. **Deploy the application**
   ```bash
   git clone <your-repository>
   cd route-screenshot-generator
   docker-compose up -d
   ```

6. **Set up domain (optional)**
   - Buy a domain name
   - Point it to your server's IP
   - Configure SSL certificate

## User Management

### Creating User Accounts

1. **Self-registration** (Recommended)
   - Users can register themselves at `/register`
   - No admin intervention needed

2. **Admin creation**
   - Create accounts manually in the database
   - Or add an admin interface

### User Training

Provide users with this simple guide:

1. **Access the system**
   - Go to your application URL
   - Register/login with your credentials

2. **Upload files**
   - Click "Upload File"
   - Drag and drop your Excel file
   - Click "Start Processing"

3. **Monitor progress**
   - Check your dashboard for job status
   - Wait for completion

4. **Download results**
   - Click "Download" when job is complete
   - Extract the ZIP file to access screenshots

## Maintenance

### Regular Tasks

1. **Monitor disk space**
   - Check storage usage monthly
   - Clean up old files if needed

2. **Update the application**
   ```bash
   git pull
   docker-compose down
   docker-compose up -d --build
   ```

3. **Backup data**
   - Backup the database file
   - Backup uploaded files

### Troubleshooting

1. **Application not starting**
   - Check if Docker is running
   - Check logs: `docker-compose logs`

2. **Users can't access**
   - Check firewall settings
   - Verify the URL is correct

3. **Jobs not processing**
   - Restart Celery: `docker-compose restart celery`
   - Check Redis connection

## Security Considerations

1. **Change default passwords**
   - Update the SECRET_KEY environment variable
   - Use strong passwords for admin accounts

2. **Regular updates**
   - Keep the application updated
   - Monitor for security patches

3. **Access control**
   - Consider IP whitelisting if needed
   - Monitor user activity

## Support

For technical support:
- Check the logs for error messages
- Review the troubleshooting section in README.md
- Contact your IT department or system administrator

## Cost Estimation

### Monthly Costs (approximate)

- **Railway**: $5-20/month (depending on usage)
- **Heroku**: $7-25/month (depending on dyno size)
- **DigitalOcean**: $5-20/month (depending on droplet size)
- **Local server**: $0 (electricity costs only)

### Scaling Costs

- Add more workers: +$5-10/month per worker
- Increase storage: +$1-5/month per GB
- Add monitoring: +$5-20/month

## Next Steps

1. **Choose your deployment option**
2. **Set up the application**
3. **Test with a small group**
4. **Train your users**
5. **Monitor and maintain**

The system is designed to be user-friendly and require minimal technical knowledge to operate. Users only need to know how to upload Excel files and download results. 