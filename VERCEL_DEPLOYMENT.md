# Deploying PeopleConnects to Vercel

## Prerequisites
1. Install Vercel CLI: `npm install -g vercel`
2. Create a Vercel account at https://vercel.com
3. Have your MongoDB connection string ready

## Step-by-Step Deployment Guide

### 1. Prepare Your Project

The necessary configuration files have been created:
- `vercel.json` - Vercel configuration
- `.vercelignore` - Files to exclude from deployment
- `api/index.py` - Vercel entry point

### 2. Install Vercel CLI (if not already installed)

```bash
npm install -g vercel
```

### 3. Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate with your Vercel account.

### 4. Configure Environment Variables

Before deploying, you need to set up environment variables in Vercel:

```bash
vercel env add MONGO_URL
vercel env add DATABASE_NAME
vercel env add SECRET_KEY
vercel env add ADMIN_USERNAME
vercel env add ADMIN_PASSWORD
```

When prompted, enter the values for each variable and select:
- Production: Yes
- Preview: Yes
- Development: Yes

**Important Environment Variables:**
- `MONGO_URL`: Your MongoDB connection string (e.g., mongodb+srv://user:pass@cluster.mongodb.net/)
- `DATABASE_NAME`: peopleconnects
- `SECRET_KEY`: A strong random secret key for JWT tokens
- `ADMIN_USERNAME`: Your admin username
- `ADMIN_PASSWORD`: Your admin password

### 5. Deploy to Vercel

Run the deployment command:

```bash
vercel
```

Or for production deployment:

```bash
vercel --prod
```

Follow the prompts:
- Set up and deploy? `Y`
- Which scope? Select your account
- Link to existing project? `N` (first time) or `Y` (if exists)
- What's your project's name? `peoplesconnect` (or your preferred name)
- In which directory is your code located? `./`

### 6. Alternative: Deploy via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import your Git repository (GitHub/GitLab/Bitbucket)
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
5. Add Environment Variables in the dashboard:
   - MONGO_URL
   - DATABASE_NAME
   - SECRET_KEY
   - ADMIN_USERNAME
   - ADMIN_PASSWORD
6. Click "Deploy"

## Important Notes for Vercel Deployment

### 1. File Upload Limitations
Vercel has a 4.5MB request body limit. For file uploads (profile pictures, post images):
- Consider using external storage (AWS S3, Cloudinary, etc.)
- Or reduce image sizes before upload

### 2. Serverless Function Limitations
- Maximum execution time: 10 seconds (Hobby), 60 seconds (Pro)
- Cold starts may occur
- Stateless execution (no persistent local storage)

### 3. Static Files
Your static files will be served from the `/static` directory as configured in `vercel.json`.

### 4. Database Connection
- Use MongoDB Atlas or another cloud-hosted MongoDB
- Ensure your database allows connections from Vercel IPs (0.0.0.0/0 or specific IPs)

### 5. Environment Variables via CLI

You can also set environment variables during deployment:

```bash
vercel --prod \
  -e MONGO_URL="your_mongo_url" \
  -e DATABASE_NAME="peopleconnects" \
  -e SECRET_KEY="your_secret_key" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD="your_password"
```

## Post-Deployment

1. **Verify Deployment**: Visit the URL provided by Vercel
2. **Check Logs**: Use `vercel logs` to view application logs
3. **Monitor**: Use Vercel dashboard to monitor performance and errors

## Troubleshooting

### Static Files Not Loading
- Ensure the `static` directory is included in your deployment
- Check browser console for 404 errors
- Verify paths in templates use `/static/...` not relative paths

### Database Connection Errors
- Verify MongoDB connection string is correct
- Check if your MongoDB allows connections from all IPs
- Test connection string locally first

### Module Import Errors
- Ensure all dependencies are in `requirements.txt`
- Check that file paths use absolute imports

### Environment Variables Not Working
```bash
# List all environment variables
vercel env ls

# Pull environment variables to local .env file
vercel env pull
```

## Updating Your Deployment

To update your deployed application:

```bash
# For preview deployment
vercel

# For production deployment
vercel --prod
```

Or simply push to your Git repository if you connected via GitHub/GitLab.

## Custom Domain (Optional)

1. Go to your project in Vercel Dashboard
2. Settings → Domains
3. Add your custom domain
4. Follow DNS configuration instructions

## Rollback (if needed)

```bash
# List deployments
vercel ls

# Promote a previous deployment to production
vercel promote <deployment-url>
```

## Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI on Vercel Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
