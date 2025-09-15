# 🌐 Accessing Sophia's Vocabulary Trainer via Tailscale

## Quick Start

1. **Start the server**:
   ```bash
   cd /Volumes/project_chimera/projects/sophia-vocab-trainer
   ./run.sh
   ```

2. **Find your Tailscale IP**:
   ```bash
   tailscale ip -4
   ```

3. **Access from any device on your Tailscale network**:
   - Open a browser to: `http://[YOUR_TAILSCALE_IP]:5005`
   - Example: `http://100.64.0.1:5005`

## Troubleshooting

### Check if everything is set up correctly:
```bash
python check_setup.py
```

### Server not starting?
1. Check Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure Tailscale is running:
   ```bash
   tailscale status
   ```

3. Check if port 5005 is free:
   ```bash
   lsof -i :5005
   ```

### Can't access from another device?
1. Make sure both devices are on the same Tailscale network
2. Check firewall settings - port 5005 should be accessible
3. Try accessing with the machine name instead of IP:
   ```
   http://[MACHINE_NAME]:5005
   ```

## Security Note
The application is configured to run in debug mode for development. For production use:
1. Set `FLASK_ENV=production` in the .env file
2. Change `debug=True` to `debug=False` in app.py
3. Use a proper WSGI server like Gunicorn

## For Sophia
Once the server is running, you can access your vocabulary trainer from:
- Your computer
- Your iPad
- Your phone
- Any device connected to the family Tailscale network!

Just bookmark the Tailscale URL and you're ready to learn! 📚✨