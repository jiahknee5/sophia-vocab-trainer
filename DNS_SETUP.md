# 🌐 DNS Configuration for home.johnnycchung.com

## Current Status

✅ GitHub Repository: https://github.com/jiahknee5/sophia-vocab-trainer
✅ Vercel Deployment: https://sophia-vocab-trainer.vercel.app
✅ Domain Added to Vercel: home.johnnycchung.com

## Required DNS Configuration

You need to add ONE of the following to your DNS provider (where johnnycchung.com is registered):

### Option 1: CNAME Record (Recommended)
```
Type: CNAME
Name: home
Value: cname.vercel-dns.com
TTL: 3600 (or Auto)
```

### Option 2: A Record
```
Type: A  
Name: home
Value: 76.76.21.21
TTL: 3600 (or Auto)
```

## Steps to Configure

1. **Log in to your domain registrar** (GoDaddy, Namecheap, etc.)
2. **Find DNS Management** or "DNS Records"
3. **Add a new record** with the values above
4. **Save the changes**

## Verification

After adding the DNS record:

1. Wait 5-30 minutes for DNS propagation
2. Visit https://home.johnnycchung.com
3. You should see Sophia's Vocabulary Trainer!

You can check DNS propagation status at:
- https://www.whatsmydns.net/#CNAME/home.johnnycchung.com

## SSL Certificate

Vercel will automatically provision an SSL certificate once DNS is configured correctly.

## Troubleshooting

If the domain doesn't work after 1 hour:
1. Double-check the DNS record values
2. Ensure there are no conflicting records for "home"
3. Clear your browser cache
4. Try from a different device/network

## Current Vercel URLs

- Production: https://sophia-vocab-trainer.vercel.app
- Domain (pending DNS): https://home.johnnycchung.com