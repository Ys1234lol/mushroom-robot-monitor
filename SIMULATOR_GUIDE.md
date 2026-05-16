# 🧪 Simulator Guide

Monitor your Mushroom Robot without real hardware! Use these simulators for testing.

## 📋 What's Included

### 1. **mqtt_simulator.py** - MQTT Broker Simulator
- Simulates MQTT clients publishing robot status
- Generates realistic robot behavior patterns
- Publishes to `AgaricusBisporusHarvesting/TR2001`
- Responds to commands on `PR0001` and `EL0001` topics

### 2. **modbus_simulator.py** - Modbus TCP Simulator (Advanced)
- Simulates Modbus TCP PLC server
- Realistic behavior patterns (moving, docking, collecting)
- Occasionally triggers errors for testing
- Requires: `pip install pymodbus`

### 3. **test_with_simulator.py** - Integrated Test Runner
- Starts simulators automatically
- Runs monitoring system
- All-in-one testing solution

---

## 🚀 Quick Start (MQTT Simulator Only)

### Terminal 1: Start MQTT Simulator
```bash
python mqtt_simulator.py
```

Expected output:
```
✓ MQTT Simulator connected to broker at localhost:1885
🤖 Starting MQTT behavior simulation...
📤 Published to TR2001: {"DeviceID": 2001, ...}
```

### Terminal 2: Start Monitoring System
```bash
python mushroom_robot_monitor.py
```

Expected output:
```
✓ Connected to Modbus TCP: 192.168.2.88:502
✓ Connected to MQTT broker: 192.168.1.107:1885
🚀 Mushroom Robot Monitoring System Started
📨 MQTT [AgaricusBisporusHarvesting/TR2001]: {"DeviceID": 2001, ...}
```

### Terminal 3: Monitor the Database
```bash
python query_database.py
```

---

## 🔧 Configuration

### For MQTT Simulator

Edit `mqtt_simulator.py` to change:
- Broker address: `broker='localhost'`
- Broker port: `port=1885`
- Simulation speed: Change `time.sleep(2)` in `simulate_behavior()`

### For Modbus Simulator

Edit `modbus_simulator.py` to change:
- Listen address: `host='0.0.0.0'`
- Listen port: `port=502` (requires admin on Windows)

### For Monitoring System

Edit `mushroom_robot_monitor.py` lines 23-28:
```python
MODBUS_HOST = "localhost"   # Connect to simulator
MODBUS_PORT = 502
MQTT_BROKER = "localhost"   # Connect to simulator
MQTT_PORT = 1885
```

---

## 📊 What Gets Simulated

### Robot Behavior
```
Home Position (1000mm)
   ↓
Moving Forward → Approaching → Docking → Docked
   ↓
Collecting Mushrooms (every ~10 cycles)
   ↓
Extending Basket → Returning Home
   ↓
Loop back to Home Position
```

### Data Variations
- **Position**: Changes from 1000mm to 100mm then back
- **Mushroom Count**: Increments during docked state
- **Status**: Cycles through all states
- **Errors**: Random errors (2% chance per cycle)
- **Error Codes**: 101-199 range

---

## 🎯 Testing Scenarios

### Scenario 1: Basic Functionality
```bash
# Terminal 1
python mqtt_simulator.py

# Terminal 2
python mushroom_robot_monitor.py

# Terminal 3
python query_database.py
```

### Scenario 2: Long-Running Stability Test
```bash
# Run for 1 hour
python mqtt_simulator.py &
python mushroom_robot_monitor.py  # Edit to: monitor.start(duration=3600)
```

### Scenario 3: Error Handling
```bash
# Simulator will trigger random errors
# Monitor will detect and log them
python mqtt_simulator.py
python mushroom_robot_monitor.py

# Check alerts
sqlite3 logs/monitoring_data.db "SELECT * FROM alerts;"
```

### Scenario 4: Data Export
```bash
python mqtt_simulator.py &
python mushroom_robot_monitor.py &

# Wait 5 minutes
sleep 300

# Export data
python export_to_csv.py

# View CSV files
ls -la *.csv
```

---

## 📈 Generated Outputs

After running with simulators, you'll get:

```
logs/
├── mushroom_robot_monitor.log    # Detailed log with simulator data
├── monitoring_data.db            # Full database with simulated data
├── waveforms/
│   ├── CurrentPosition_waveform.png       # Position changes over time
│   ├── DistanceToPickingRobot_waveform.png
│   ├── RunningMode_waveform.png
│   ├── MovingStatus_waveform.png
│   ├── BehaviorStatus_waveform.png
│   └── CollectedMushroomCount_waveform.png # Count increasing
└── reports/
    └── report_20260512_103045.html        # HTML summary

alerts_export.csv                # All alerts (including simulated errors)
state_transitions_export.csv      # All state changes
modbus_registers_export.csv       # All register values
```

---

## 🔍 Viewing Simulated Data

### View Log File
```bash
tail -f logs/mushroom_robot_monitor.log
```

### View Recent Alerts
```bash
sqlite3 logs/monitoring_data.db "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10;"
```

### View State Transitions
```bash
sqlite3 logs/monitoring_data.db "SELECT * FROM state_transitions ORDER BY timestamp DESC LIMIT 10;"
```

### Open HTML Report
```bash
open logs/reports/report_*.html          # macOS
start logs/reports/report_*.html         # Windows
firefox logs/reports/report_*.html       # Linux
```

---

## 🐛 Troubleshooting

### Error: "Address already in use"
```bash
# Port is in use, try different port
# Edit mqtt_simulator.py, change port to 1886
```

### Error: "Connection refused"
```bash
# Make sure simulator is running in another terminal
# Check firewall settings
```

### No data in database
```bash
# Wait a few seconds for simulator to start
# Check if MQTT is running on correct port
# Verify network connectivity
```

### MQTT connection timeout
```bash
# Install MQTT broker (Mosquitto)
# Or use online test broker: test.mosquitto.org
```

---

## 💡 Advanced: Using Real MQTT Broker

If you have a real MQTT broker:

### Option 1: Local Mosquitto
```bash
# Install Mosquitto
brew install mosquitto              # macOS
sudo apt-get install mosquitto     # Ubuntu
choco install mosquitto            # Windows

# Start broker
mosquitto -p 1885

# In another terminal
python mqtt_simulator.py
python mushroom_robot_monitor.py
```

### Option 2: Online Test Broker
```python
# Edit mqtt_simulator.py
broker='test.mosquitto.org'
port=1883

# Edit mushroom_robot_monitor.py
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
```

---

## 📝 Modifying Simulator Behavior

### Increase Simulation Speed
In `mqtt_simulator.py`, change:
```python
time.sleep(2)  # Change from 2 to 0.5 for 4x speed
```

### Change Robot Behavior
In `mqtt_simulator.py`, modify `simulate_behavior()` method:
```python
# Example: Increase error frequency
if random.random() < 0.20:  # Changed from 0.05 to 0.20
    self.robot_state['Error'] = 1
```

### Add Custom Events
Add to `simulate_behavior()` loop:
```python
if cycle == 50:  # At cycle 50
    logger.info("🚨 Triggering custom event")
    self.robot_state['ESTOP'] = 1
```

---

## ✅ Next Steps

1. ✅ Start MQTT simulator
2. ✅ Start monitoring system
3. ✅ View real-time logs
4. ✅ Check database
5. ✅ Generate waveforms
6. ✅ Export data
7. ✅ Validate everything works
8. ✅ Connect to real hardware

---

## 📚 Related Files

- `README.md` - Main documentation
- `PROTOCOL.md` - Technical specifications
- `mushroom_robot_monitor.py` - Main monitoring system
- `query_database.py` - Database query tool
- `export_to_csv.py` - Data export tool

---

**Happy Testing! 🎉**
