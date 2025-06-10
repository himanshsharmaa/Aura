# Aura Troubleshooting Guide

## Common Issues and Solutions

### 1. Audio Device Issues

#### Problem: No Microphone Detected
**Symptoms:**
- Error: "No input devices found"
- Application fails to start
- No audio input visualization

**Solutions:**
1. Check if microphone is properly connected
2. Verify system settings:
   - Windows: Settings > System > Sound > Input
   - Linux: `pavucontrol` or `alsamixer`
   - macOS: System Preferences > Sound > Input
3. Try reinstalling PyAudio:
   ```bash
   pip uninstall pyaudio
   pip install pyaudio
   ```

#### Problem: Poor Audio Quality
**Symptoms:**
- Low detection accuracy
- Frequent false positives/negatives
- Distorted audio

**Solutions:**
1. Check microphone settings:
   - Set sample rate to 16000 Hz
   - Use mono channel
   - Adjust input volume
2. Reduce background noise
3. Use a better quality microphone

### 2. Model Issues

#### Problem: Model Download Fails
**Symptoms:**
- Error: "Failed to download model"
- Application crashes on startup
- Missing model files

**Solutions:**
1. Check internet connection
2. Clear model cache:
   ```bash
   rm -rf models/*
   ```
3. Manual download:
   - Download YAMNet model from TensorFlow Hub
   - Place in `models/yamnet_model/`

#### Problem: High Memory Usage
**Symptoms:**
- Slow performance
- Application freezes
- System becomes unresponsive

**Solutions:**
1. Close other applications
2. Reduce batch size in config.json
3. Use CPU-only mode:
   ```python
   os.environ['CUDA_VISIBLE_DEVICES'] = ''
   ```

### 3. Hotword Detection Issues

#### Problem: Low Detection Accuracy
**Symptoms:**
- Misses wake word
- False triggers
- Inconsistent behavior

**Solutions:**
1. Collect more training samples:
   ```python
   detector.start_collecting_samples('positive')
   # Say "Aura" clearly
   detector.stop_collecting_samples()
   ```
2. Adjust threshold in config.json
3. Retrain model with new samples

#### Problem: Training Fails
**Symptoms:**
- Error during training
- Model not improving
- High loss values

**Solutions:**
1. Check sample quality:
   - Clear audio
   - Proper duration
   - Good signal-to-noise ratio
2. Increase number of samples
3. Adjust learning rate in config.json

### 4. Sound Event Detection Issues

#### Problem: False Event Detection
**Symptoms:**
- Triggers on wrong sounds
- Misses actual events
- Inconsistent detection

**Solutions:**
1. Adjust threshold in config.json
2. Collect more training data
3. Fine-tune model parameters

### 5. Application Crashes

#### Problem: Random Crashes
**Symptoms:**
- Application closes unexpectedly
- Error messages in logs
- System becomes unresponsive

**Solutions:**
1. Check logs in `logs/` directory
2. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
3. Clear cache:
   ```bash
   rm -rf data/cache/*
   ```

### 6. Performance Issues

#### Problem: High CPU Usage
**Symptoms:**
- Slow response
- High system load
- Battery drain

**Solutions:**
1. Reduce processing frequency
2. Use lighter models
3. Optimize configuration:
   ```json
   {
     "processing": {
       "batch_size": 1,
       "use_gpu": false,
       "thread_count": 1
     }
   }
   ```

## Running Tests

To verify all components:

```bash
python tests/test_components.py
```

This will:
1. Test all major components
2. Generate a test report
3. Create necessary directories
4. Validate configuration

## Getting Help

If issues persist:
1. Check the logs in `logs/` directory
2. Run the test suite
3. Create an issue on GitHub with:
   - Error messages
   - System information
   - Steps to reproduce
   - Log files

## System Requirements

- Python 3.8+
- 4GB RAM minimum
- Working microphone
- Internet connection (first run)
- 1GB free disk space 