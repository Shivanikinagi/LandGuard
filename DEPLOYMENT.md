# Deployment Guide

## Render Deployment

### Prerequisites

1. Create a [Pinata](https://pinata.cloud) account to get your IPFS JWT token
2. Sign up for [Render](https://render.com)

### Steps

1. **Fork/Push this repository to GitHub**

2. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Use the following settings:
     - **Environment**: Python
     - **Build Command**: (Automatically detected from render.yaml)
     - **Start Command**: (Automatically detected from render.yaml)

3. **Set Environment Variables in Render Dashboard**
   
   Go to your service's **Environment** tab and add:
   
   ```
   PINATA_JWT=your_actual_pinata_jwt_token_here
   ```
   
   To get your Pinata JWT:
   - Go to https://app.pinata.cloud/developers/api-keys
   - Click "New Key"
   - Give it Admin permissions
   - Copy the JWT token
   
   Optional environment variables:
   ```
   MAX_FILE_SIZE=100000000
   COMPRESSION_LEVEL=9
   ENABLE_IPFS=true
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Click "Manual Deploy" > "Deploy latest commit"
   - Wait for the build to complete
   - Your service will be available at `https://your-service.onrender.com`

### Troubleshooting

#### "PINATA_JWT not found" Error
- Make sure you've set the `PINATA_JWT` environment variable in the Render Dashboard
- Redeploy after setting the variable

#### "python-magic-bin" Install Error
- This has been fixed in the latest version
- The project now uses platform-specific dependencies

#### Build Timeout
- Render free tier has build time limits
- Consider upgrading to a paid plan if builds consistently timeout

### Testing Your Deployment

```bash
# Test the API
curl https://your-service.onrender.com/

# Upload a file for compression
curl -X POST https://your-service.onrender.com/compress \
  -F "file=@test.txt" \
  -F "compression_level=9"
```

## Railway Deployment

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Set environment variables:
   ```bash
   railway variables set PINATA_JWT=your_jwt_here
   ```
5. Deploy: `railway up`

## Docker Deployment

```bash
# Build the image
docker build -f Dockerfile.pcc -t landguard .

# Run with environment variables
docker run -p 8000:8000 \
  -e PINATA_JWT=your_jwt_here \
  landguard
```

## Heroku Deployment

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set buildpacks:
   ```bash
   heroku buildpacks:add heroku/python
   ```
5. Set environment variables:
   ```bash
   heroku config:set PINATA_JWT=your_jwt_here
   ```
6. Deploy:
   ```bash
   git push heroku main
   ```
