# Deployment Instructions for cPanel (hvacsolution81.com)

This guide explains how to deploy the Flask application to cPanel using Passenger WSGI.

## Prerequisites

- cPanel access to hvacsolution81.com
- Python 3.x available on the hosting server
- SSH access (optional but recommended)

## Step 1: Prepare Files for Upload

1. **Create a ZIP file** of your project:
   ```bash
   # From your local project directory, exclude unnecessary files
   zip -r app_deploy.zip . -x "*.git*" "*.db" "__pycache__/*" "*.pyc" ".env" "venv/*"
   ```

2. **Alternatively**, create a clean directory with only the necessary files:
   - `app.py`
   - `passenger_wsgi.py`
   - `config.py`
   - `requirements.txt`
   - `forms.py`
   - `models/` directory (with `__init__.py`)
   - `routes/` directory (with all blueprint files)
   - `templates/` directory (all HTML files)
   - `static/` directory (CSS, JS, images)

## Step 2: Upload to cPanel

1. **Log in to cPanel** at your hosting provider
2. **Navigate to File Manager**
3. **Go to your domain directory** (usually `/home/username/hvacsolution81.com` or `/home/username/public_html/hvacsolution81.com`)
4. **Upload the ZIP file** and extract it, OR upload files individually via FTP/SFTP

## Step 3: Set Up Python Environment

1. **Via cPanel's Terminal** (or SSH):
   ```bash
   cd /home/username/hvacsolution81.com
   
   # Create virtual environment (if not already exists)
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Step 4: Configure passenger_wsgi.py

1. **Edit `passenger_wsgi.py`** and update the `project_home` path:
   ```python
   project_home = '/home/your_cpanel_username/hvacsolution81.com'
   ```

2. **Set environment variables** for production:
   - In cPanel, you can set environment variables via the "Setup Python App" interface
   - Or edit `passenger_wsgi.py` directly to set `os.environ['SECRET_KEY']`
   
   **Important**: Generate a strong SECRET_KEY:
   ```python
   import secrets
   print(secrets.token_hex(32))  # Use this output as your SECRET_KEY
   ```

## Step 5: Configure Python App in cPanel

1. **Navigate to "Setup Python App"** in cPanel
2. **Create a new Python application**:
   - Python version: 3.x (check which versions are available)
   - Application root: `/home/username/hvacsolution81.com`
   - Application URL: Your domain or subdomain
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`

3. **Add environment variables** (if available in the interface):
   - `SECRET_KEY`: Your generated secret key
   - `DATABASE_URL`: (optional) If using MySQL/PostgreSQL

4. **Save the configuration**

## Step 6: Initialize the Database

If using SQLite (default), the database will be created automatically on first run.

If you need to manually initialize:
```bash
cd /home/username/hvacsolution81.com
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Step 7: Restart the Application

1. In cPanel's "Setup Python App", click **"Restart"** button
2. Or via command line:
   ```bash
   touch /home/username/hvacsolution81.com/tmp/restart.txt
   ```

## Step 8: Verify Deployment

1. **Visit your domain**: `https://hvacsolution81.com`
2. You should see: "Flask app is running! Visit /login to start."
3. Test the login page: `https://hvacsolution81.com/login`

## Common Issues and Troubleshooting

### Issue: ImportError or Module Not Found
- **Solution**: Ensure all dependencies are installed in the virtual environment
- Check that `passenger_wsgi.py` has the correct `project_home` path
- Verify `sys.path` includes your project directory

### Issue: 500 Internal Server Error
- **Solution**: Check error logs in cPanel (usually in `logs/` directory)
- Enable debug logging in `passenger_wsgi.py`
- Verify file permissions (typically 644 for files, 755 for directories)

### Issue: Database Errors
- **Solution**: Ensure `app.db` file exists and has write permissions
- For SQLite, the directory containing the DB must be writable
- Consider using MySQL/PostgreSQL for production

### Issue: Static Files Not Loading
- **Solution**: Check that `static/` directory is uploaded
- Verify paths in templates are correct
- Check .htaccess rules if any

## Environment Variables (Production)

**Never commit sensitive data to Git!** Use environment variables:

```python
# In passenger_wsgi.py or via cPanel environment settings
os.environ['SECRET_KEY'] = 'your-very-long-random-secret-key'
os.environ['DATABASE_URL'] = 'mysql://user:pass@localhost/dbname'  # if using MySQL
```

## Updates and Maintenance

To update your application:

1. Upload new/modified files via File Manager or FTP
2. If dependencies changed, reinstall:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Restart the application:
   ```bash
   touch /home/username/hvacsolution81.com/tmp/restart.txt
   ```

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Do not commit `.db` files or secrets to Git
- [ ] Use HTTPS (enable SSL certificate in cPanel)
- [ ] Set proper file permissions (644 for files, 755 for directories)
- [ ] Disable Flask debug mode in production (`app.run(debug=False)`)
- [ ] Review CSRF protection settings
- [ ] Configure session cookie settings for HTTPS

## Support

For cPanel-specific issues, contact your hosting provider's support team.
For application issues, review Flask documentation at https://flask.palletsprojects.com/
