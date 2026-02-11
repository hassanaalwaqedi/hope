# HOPE - Quick Azure Deployment (Student Account)

## Issue Identified
Your Azure student subscription has regional/policy restrictions that prevent deploying Azure Container Registry (ACR) in `eastus` region with the Bicep template.

## Recommended Solution: Use Azure Web App with GitHub Integration

This approach works better with student subscriptions and is simpler:

### Step 1: Create PostgreSQL Database Manually

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource" → Search "Azure Database for PostgreSQL Flexible Server"
3. Configure:
   - **Resource Group**: `hope-prod-rg` (already created)
   - **Server name**: `hope-api-db`
   - **Region**: Choose one allowed by your subscription (try `westeurope` or `westus`)
   - **Workload type**: Development
   - **Compute + storage**: Burstable, B1ms (1 vCore, 2 GiB RAM) - **~$15/month**
   - **Admin username**: `hopeadmin`
   - **Password**: `7X3$r*Vo4Yavq#ynuU5sbhk1` (from script)
4. Networking → Check "Allow public access from any Azure service"
5. Click "Review + create"

### Step 2: Create Web App with Container

1. Azure Portal → "Create a resource" → "Web App"
2. Configure:
   - **Resource Group**: `hope-prod-rg`
   - **Name**: `hope-api` (will be `hope-api.azurewebsites.net`)
   - **Publish**: **Docker Container**
   - **Operating System**: Linux
   - **Region**: Same as PostgreSQL
   - **Pricing plan**: B1 (Basic) - **~$13/month**
3. Docker tab:
   - **Options**: Single Container
   - **Image Source**: Docker  Hub
   - **Image**: `python:3.11-slim` (temporary, we'll update later)
4. Click "Review + create"

### Step 3: Configure Environment Variables

1. Go to your Web App → Configuration → Application settings
2. Add these settings:

| Name | Value |
|------|-------|
| `HOPE_ENV` | `production` |
| `HOPE_DB_HOST` | `hope-api-db.postgres.database.azure.com` |
| `HOPE_DB_PORT` | `5432` |
| `HOPE_DB_NAME` | `postgres` |
| `HOPE_DB_USER` | `hopeadmin` |
| `HOPE_DB_PASSWORD` | `7X3$r*Vo4Yavq#ynuU5sbhk1` |
| `HOPE_DB_SSL_MODE` | `require` |
| `HOPE_JWT_SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `HOPE_ENCRYPTION_KEY` | Generate with: `python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"` |
| `HOPE_GEMINI_API_KEY` | Your Google AI Studio API key |

3. Save

### Step 4: Deploy Code via GitHub (Easiest)

1. Push your code to GitHub
2. In Azure Web App → Deployment Center
3. Choose "GitHub" → Authorize → Select your `hope` repository
4. Branch: `main`
5. Click "Save"

Azure will:
- Build your Docker image automatically
- Deploy it to the Web App
- Rebuild on every push to `main`

### Step 5: Run Database Migrations

```powershell
# SSH into the Web App
az webapp ssh --name hope-api --resource-group hope-prod-rg

# Inside SSH session:
alembic upgrade head
exit
```

### Step 6: Test

```powershell
Invoke-WebRequest https://hope-api.azurewebsites.net/health
```

---

## Alternative: Deploy via Docker Hub

If you don't want to use GitHub:

1. Build and push to Docker Hub:
```powershell
docker build -t yourusername/hope-api:latest .
docker push yourusername/hope-api:latest
```

2. Update Web App → Configuration → Container settings:
   - Image: `yourusername/hope-api:latest`

---

## Total Cost: ~$28/month

With $100 student credit = **~3.5 months free**
