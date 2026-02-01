# AGES Quick Start Guide

Welcome to **AetherGuard Edge Sentinel (AGES)** - your autopoietic digital guardian. This guide will help you get AGES up and running in minutes.

---

## Installation

### Step 1: Install Dependencies

First, ensure you have Python 3.8 or higher installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `psutil` - For system monitoring
- `numpy` - For statistical computations
- `pyyaml` - For configuration management

### Step 2: Verify Installation

Check that the main script is executable:

```bash
chmod +x ages.py
```

---

## Running AGES

### Start Protection

To start AGES and begin protecting your system:

```bash
./ages.py start
```

You should see the AGES banner and a message confirming that the system is operational. AGES will now run in the foreground, monitoring your system for threats.

### Check Status

To view the current status of AGES and all its modules:

```bash
./ages.py status
```

This will display detailed information about:
- Engine status (running, generation count, threats blocked)
- Module status (SBAD, TNFA, APG, RGG, TSHL, MBC)
- Resource usage and performance metrics

### Stop Protection

To stop AGES gracefully, press `Ctrl+C` in the terminal where it's running.

---

## Understanding the Output

When AGES starts, it enters a **learning mode** for the first 5 minutes. During this time, it builds statistical profiles of your system's normal behavior. You'll see messages like:

```
SBAD learning period complete - active monitoring engaged
```

After the learning period, AGES will begin actively detecting anomalies. If a threat is detected, you'll see alerts like:

```
[AGES ALERT] Threat Quarantined: suspicious_process.exe - Attempted unauthorized system modification.
```

---

## Configuration

The default configuration is located at `config/default.yaml`. You can customize AGES by editing this file or creating your own configuration.

### Common Configuration Changes

**Adjust Sensitivity:** Lower the `z_score_threshold` in SBAD to make anomaly detection more sensitive:

```yaml
modules:
  sbad:
    z_score_threshold: 2.5  # Default is 3.0
```

**Reduce Resource Usage:** Increase the scan intervals to reduce CPU usage:

```yaml
modules:
  sbad:
    scan_interval: 5.0  # Default is 2.0
  tnfa:
    monitor_interval: 10.0  # Default is 5.0
```

**Adjust Resource Limits:** Change the MBC thresholds to give AGES more or less CPU:

```yaml
modules:
  mbc:
    cpu_threshold: 50.0  # Default is 70.0 (more conservative)
```

### Using a Custom Configuration

To run AGES with a custom configuration file:

```bash
./ages.py start --config /path/to/your/config.yaml
```

---

## Monitoring AGES

### Log Files

AGES writes detailed logs to `logs/ages.log`. You can monitor this file in real-time:

```bash
tail -f logs/ages.log
```

### Generated Rules

As AGES learns, it generates defensive rules stored in `data/rules.json`. You can inspect this file to see what patterns AGES has learned:

```bash
cat data/rules.json | python -m json.tool
```

### Rule Genealogy

The complete genealogy of all rules is stored in `data/genealogy.json`. This file shows the parent-child relationships and performance of each rule.

---

## Testing AGES

### Simulate CPU Anomaly

To test SBAD's CPU monitoring, create an artificial CPU spike:

```bash
# Run a CPU-intensive task
yes > /dev/null &
# Note the process ID
PID=$!
# Let it run for 30 seconds
sleep 30
# Kill the process
kill $PID
```

AGES should detect this as an anomaly after the learning period.

### Simulate Network Anomaly

To test TNFA's network monitoring, perform a port scan (only on systems you own):

```bash
# Scan a range of ports on localhost
for port in {1..100}; do
  nc -zv localhost $port 2>&1 | grep succeeded
done
```

AGES should detect this as potential port scanning behavior.

---

## Troubleshooting

### AGES Won't Start

**Problem:** Error about missing `psutil` module.

**Solution:** Install dependencies:
```bash
pip install psutil numpy pyyaml
```

### High CPU Usage

**Problem:** AGES is using too much CPU.

**Solution:** Increase scan intervals in the configuration file (see Configuration section above).

### No Threats Detected

**Problem:** AGES isn't detecting any anomalies.

**Solution:** 
1. Ensure the learning period has completed (wait 5 minutes after starting).
2. Check that modules are enabled in the configuration.
3. Lower the detection thresholds to increase sensitivity.

### Permission Errors

**Problem:** AGES can't access certain system information.

**Solution:** Run AGES with elevated privileges (use with caution):
```bash
sudo ./ages.py start
```

---

## Next Steps

Now that you have AGES running, consider:

1. **Customizing the configuration** to match your security needs and hardware capabilities.
2. **Monitoring the logs** to understand what AGES is learning about your system.
3. **Reviewing generated rules** to see how AGES is evolving its defenses.
4. **Reading the full README** for detailed information about each module and the autopoietic architecture.

---

**Welcome to the future of adaptive cybersecurity. AGES is now learning, evolving, and protecting your system.**
