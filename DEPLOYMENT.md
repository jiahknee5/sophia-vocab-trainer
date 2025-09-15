# 🚀 Deployment Instructions

## Deploying to Vercel

### Step 1: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with your GitHub account
2. Click "New Project"
3. Import the `sophia-vocab-trainer` repository
4. Vercel will automatically detect the configuration
5. Click "Deploy"

### Step 2: Set Up Database (Optional)

For persistent data storage, you can use Vercel Postgres:

1. In your Vercel project dashboard, go to the "Storage" tab
2. Click "Create Database" → "Postgres"
3. Follow the setup instructions
4. The DATABASE_URL will be automatically added to your environment variables

Alternatively, you can use any PostgreSQL provider:
- [Supabase](https://supabase.com) (free tier available)
- [Neon](https://neon.tech) (generous free tier)
- [Railway](https://railway.app)

### Step 3: Configure Custom Domain

To connect `home.johnnycchung.com`:

1. In your Vercel project, go to "Settings" → "Domains"
2. Add `home.johnnycchung.com`
3. You'll see DNS records to add to your domain provider

#### DNS Configuration

Add these records to your domain's DNS settings:

**Option A: CNAME Record (Recommended)**
```
Type: CNAME
Name: home
Value: cname.vercel-dns.com
TTL: 3600
```

**Option B: A Record**
```
Type: A
Name: home
Value: 76.76.21.21
TTL: 3600
```

### Step 4: Environment Variables (Optional)

If you want to customize settings:

1. Go to "Settings" → "Environment Variables"
2. Add:
   - `SECRET_KEY`: A secure random string
   - `DATABASE_URL`: Your PostgreSQL connection string (if using external DB)

### Step 5: Verify Deployment

1. Visit your Vercel URL: `https://sophia-vocab-trainer.vercel.app`
2. Once DNS propagates (5-30 minutes), visit: `https://home.johnnycchung.com`

## 🔧 Troubleshooting

### Database Issues
- If using SQLite, note that data won't persist between deployments
- Consider using Vercel Postgres or external database for production

### Domain Not Working
- DNS changes can take up to 48 hours to propagate
- Check DNS propagation at [whatsmydns.net](https://www.whatsmydns.net)
- Ensure SSL certificate is provisioned in Vercel dashboard

### Function Timeouts
- Vercel has a 10-second timeout for serverless functions
- Consider optimizing database queries if needed

## 📱 Mobile Access

Once deployed, Sophia can:
1. Visit `home.johnnycchung.com` on her iPhone
2. Tap Share → "Add to Home Screen"
3. Access the app like a native application!

## 🔄 Updates

To deploy updates:
1. Push changes to GitHub
2. Vercel will automatically redeploy

Or manually:
```bash
npm i -g vercel
vercel --prod
```