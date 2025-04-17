# Troubleshooting Guide

## Common Issues and Solutions

### Model Loading Issues

#### Error: CUDA out of memory
**Symptom:** Model fails to load with CUDA memory error
**Solution:**
```bash
# Try 4-bit quantization
tursi up your-model --bits 4

# Or use CPU-only mode (automatically used when CUDA is unavailable)
```

#### Error: Model not found
**Symptom:** "Model 'xyz' not found in cache or Hugging Face"
**Solution:**
- Check model name spelling
- Verify model exists on Hugging Face
- Check internet connection
- Try specifying full model path

### API Issues

#### Rate Limiting
**Symptom:** Getting 429 Too Many Requests
**Solution:**
```bash
# Increase rate limit
tursi up your-model --rate-limit "200/minute"
```

#### Connection Refused
**Symptom:** Cannot connect to API endpoint
**Solution:**
- Verify correct port number
- Check if server is running (`tursi ps`)
- Ensure host is set correctly for remote access
```bash
# For remote access, use
tursi up your-model --host 0.0.0.0
```

### Performance Issues

#### High Memory Usage
**Solutions:**
1. Use 4-bit quantization:
```bash
tursi up your-model --bits 4
```
2. Choose a smaller model variant
3. Adjust rate limiting to prevent overload
4. Monitor with `tursi stats`

#### Slow Inference
**Solutions:**
1. Try static quantization:
```bash
tursi up your-model --quantization static
```
2. Use a lighter model
3. Monitor system resources
4. Check for other processes using CPU/GPU

### System Issues

#### Cache Directory Problems
**Symptom:** Permission denied or disk space issues
**Solution:**
```bash
# Specify alternative cache directory
tursi up your-model --cache-dir /path/to/cache
```

#### Process Management
**Symptom:** Cannot stop server or zombie processes
**Solution:**
```bash
# Graceful shutdown
tursi down

# If still running, find and kill process
ps aux | grep tursi
kill -9 <PID>
```

## Best Practices for Avoiding Issues

1. **Regular Monitoring**
   ```bash
   # Monitor logs
   tursi logs --follow

   # Check resource usage
   tursi stats
   ```

2. **Proper Shutdown**
   - Always use `tursi down` for graceful shutdown
   - Verify with `tursi ps` that all processes are stopped

3. **Resource Planning**
   - Start with default settings
   - Monitor resource usage
   - Adjust quantization and rate limits as needed
   - Use appropriate model size for your use case

4. **Testing**
   - Test API endpoints before production
   - Verify model outputs
   - Check resource usage under load
   - Test error handling

## Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/BlueTursi/tursi-ai/issues)
2. Run with debug logging:
   ```bash
   TURSI_DEBUG=1 tursi up your-model
   ```
3. Include in bug reports:
   - Full command used
   - Error message
   - System information
   - Logs (`tursi logs`)
   - Resource stats (`tursi stats`)
