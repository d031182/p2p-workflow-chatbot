# SAP BTP Login Troubleshooting

## Error: PASSWORD_LOCKED

```
{"error":"invalid_grant","error_description":"User authentication failed: PASSWORD_LOCKED"}
```

### What This Means
Your SAP BTP account password has been locked, typically due to:
- Multiple failed login attempts
- Security policy enforcement
- Password expiration

## Solutions

### Option 1: Use SSO (Recommended)

Cloud Foundry supports Single Sign-On, which bypasses password authentication:

```bash
cf login -a https://api.cf.eu10.hana.ondemand.com --sso
```

This will:
1. Provide you with a URL
2. Open it in your browser
3. Authenticate via SAP SSO
4. Get a temporary passcode
5. Paste the passcode back in the CLI

### Option 2: Reset Your Password

1. Go to SAP Accounts: https://accounts.sap.com
2. Click "Forgot Password"
3. Follow the reset process
4. Wait for password unlock (may take a few minutes)
5. Try login again

### Option 3: Contact SAP Support

If the account remains locked:
1. Contact your SAP BTP administrator
2. Or open a ticket at https://launchpad.support.sap.com
3. Request password unlock

### Option 4: Use Service Key Authentication

For CI/CD or automated deployments:

1. **Create a Service Key in BTP Cockpit:**
   - Go to your Cloud Foundry Space
   - Create a service key with appropriate permissions

2. **Use API Token:**
```bash
cf auth <username> <api-token> --origin <identity-provider>
```

## Recommended: SSO Login

The easiest and most secure method:

```bash
# Step 1: Start SSO login
cf login -a https://api.cf.eu10.hana.ondemand.com --sso

# Step 2: You'll see output like:
# Temporary Authentication Code ( Get one at https://login.cf.eu10.hana.ondemand.com/passcode ):

# Step 3: Click the URL or copy it to your browser

# Step 4: Login with your SAP credentials in the browser

# Step 5: Copy the temporary passcode shown

# Step 6: Paste it back in the CLI

# Step 7: Select your org and space
```

## After Successful Login

Once logged in, proceed with deployment:

```bash
# Verify login
cf target

# Deploy
cf push

# Check status
cf apps
```

## Alternative: Deploy Without CLI

If you can't resolve the login issue, you can deploy via:

### SAP BTP Cockpit (Web UI)

1. **Go to:** https://cockpit.eu10.hana.ondemand.com
2. **Navigate to:** Cloud Foundry → Your Org → Your Space
3. **Click:** "Deploy Application" or "Upload"
4. **Create a ZIP file** of this directory:
   - Include: All .py files, templates/, static/, requirements.txt, manifest.yml, runtime.txt
   - Exclude: Test files, .md documentation, __pycache__
5. **Upload and configure**
6. **Start the application**

### Create Deployment ZIP

On Windows PowerShell:
```powershell
# Navigate to project directory
cd "c:\Users\D031182\OneDrive - SAP SE\Documents\Cline\steel_thread"

# Create zip excluding test files
Compress-Archive -Path *.py,templates,static,requirements.txt,manifest.yml,runtime.txt,.cfignore -DestinationPath p2p-workflow.zip
```

Then upload `p2p-workflow.zip` via BTP Cockpit.

## Prevention

To avoid future lockouts:
- ✅ Use SSO authentication (`--sso` flag)
- ✅ Store credentials securely
- ✅ Don't retry failed logins multiple times
- ✅ Use service keys for automation

## Quick Reference

```bash
# SSO Login (Recommended)
cf login -a https://api.cf.eu10.hana.ondemand.com --sso

# Regular Login (if password unlocked)
cf login -a https://api.cf.eu10.hana.ondemand.com

# Check Current Target
cf target

# Deploy
cf push

# View Logs
cf logs p2p-workflow --recent
```

## Need Help?

- **SAP BTP Documentation:** https://help.sap.com/docs/btp
- **Cloud Foundry Docs:** https://docs.cloudfoundry.org
- **SAP Support:** https://launchpad.support.sap.com
