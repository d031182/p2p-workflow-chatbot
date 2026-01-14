# SAP BTP Cloud Foundry Deployment Guide

## Prerequisites

### 1. Install Cloud Foundry CLI

**Windows:**
Download from: https://github.com/cloudfoundry/cli/releases

Or use Chocolatey:
```powershell
choco install cloudfoundry-cli
```

Or download the installer:
```
https://packages.cloudfoundry.org/stable?release=windows64&version=v8&source=github
```

**Verify Installation:**
```bash
cf --version
```

### 2. SAP BTP Account Requirements
- Active SAP BTP account
- Cloud Foundry environment enabled
- Org and Space created
- API Endpoint: https://api.cf.eu10.hana.ondemand.com

## Quick Deployment

### Option 1: Manual CF CLI Deployment

1. **Install CF CLI** (see above)

2. **Login to Cloud Foundry:**
```bash
cf login -a https://api.cf.eu10.hana.ondemand.com
```
Enter your SAP credentials when prompted.

3. **Target Your Space:**
```bash
cf target -o <your-org> -s <your-space>
```

4. **Deploy:**
```bash
cf push
```

5. **Access Your App:**
The deployment will output a URL like:
```
https://p2p-workflow.cfapps.eu10.hana.ondemand.com
```

### Option 2: Using SAP BTP Cockpit (Web UI)

1. Go to SAP BTP Cockpit: https://cockpit.eu10.hana.ondemand.com
2. Navigate to your Cloud Foundry Space
3. Click "Deploy" → "Upload Application"
4. Create a zip file of this directory (excluding files in .cfignore)
5. Upload and configure:
   - Name: p2p-workflow
   - Memory: 512MB (or 1GB for better AI performance)
   - Instances: 1

### Option 3: CI/CD Pipeline

Use `.github/workflows` or Jenkins with CF CLI:
```yaml
- name: Deploy to CF
  run: |
    cf login -a https://api.cf.eu10.hana.ondemand.com -u ${{ secrets.CF_USER }} -p ${{ secrets.CF_PASSWORD }}
    cf push
```

## Configuration Files

### manifest.yml
Defines:
- App name: `p2p-workflow`
- Memory: 512MB
- Disk: 1GB
- Python buildpack
- Health check endpoint

### runtime.txt
Specifies Python 3.10.x

### .cfignore
Excludes test files, docs, and cache from deployment

## Post-Deployment

### Check Status
```bash
cf apps
cf app p2p-workflow
```

### View Logs
```bash
cf logs p2p-workflow --recent
```

### Scale if Needed
```bash
# Increase memory for AI models
cf scale p2p-workflow -m 1G

# Add more instances
cf scale p2p-workflow -i 2

cf restart p2p-workflow
```

### Set Environment Variables
```bash
cf set-env p2p-workflow FLASK_ENV production
cf set-env p2p-workflow SECRET_KEY "your-secret-key-here"
cf restage p2p-workflow
```

## Memory Requirements

### Minimum Configuration (No AI)
- **512MB** - Basic workflow functionality only
- Disable AI chatbot in settings

### Recommended Configuration (With AI)
- **1GB** - Full functionality including Flan-T5 model
- All features enabled

### High Performance
- **2GB** - Multiple instances, faster responses
- Use for production with multiple users

## Application Features

Once deployed, users can access:

1. **Dashboard** - `/` - Overview of workflow status
2. **Purchase Orders** - `/purchase-orders` - Manage POs
3. **Goods Receipts** - `/goods-receipts` - Track deliveries
4. **Invoices** - `/invoices` - Invoice processing
5. **Approvals** - `/pending-approvals` - Review pending items
6. **AI Assistant** - `/chatbot` - Intelligent chatbot with visual analytics
7. **Statistics** - `/statistics` - Workflow metrics

## Troubleshooting

### App Crashes on Start
**Cause**: Not enough memory for AI model
**Solution**: 
```bash
cf scale p2p-workflow -m 1G
cf restart p2p-workflow
```

### Slow First Request
**Cause**: AI model loading on first request
**Solution**: This is normal. Subsequent requests will be faster.

### Port Binding Error
**Cause**: App not using $PORT environment variable
**Solution**: Already configured in web_app.py to use `os.environ.get('PORT', 5000)`

## Security for Production

Before production deployment:

1. **Change Secret Key:**
   ```bash
   cf set-env p2p-workflow SECRET_KEY "$(python -c 'import secrets; print(secrets.token_hex(32))')"
   ```

2. **Add Authentication:**
   - Integrate with SAP IAS/IPS
   - Use OAuth2/SAML

3. **Use Database:**
   - Bind PostgreSQL or HANA service
   - Persist data instead of in-memory storage

4. **Enable HTTPS Only:**
   - Already handled by Cloud Foundry

## Monitoring

View app metrics:
```bash
cf app p2p-workflow
```

Check events:
```bash
cf events p2p-workflow
```

## Cleanup

Remove the app:
```bash
cf delete p2p-workflow
```

## Next Steps

After deployment:
1. Test all features in cloud environment
2. Configure AI chatbot settings
3. Enable tools for advanced analytics
4. Monitor performance and scale as needed
5. Add database for production data persistence
