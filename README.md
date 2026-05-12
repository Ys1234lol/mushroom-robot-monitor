# 🤖 Mushroom Robot Monitor

A comprehensive **Modbus TCP + MQTT** monitoring system for mushroom harvesting robots with real-time signal analysis, state tracking, and automated waveform visualization.

## 📋 Features

- ✅ **Modbus TCP Monitoring** - Read 22 registers from PLC (Transfer Robot 2001)
- ✅ **MQTT Support** - Dual-protocol communication with Picking Robot & Elevator
- ✅ **State Tracking** - Automatic state machine analysis with transitions
- ✅ **Anomaly Detection** - Real-time alerts for errors, emergency stops, invalid states
- ✅ **Database Storage** - SQLite with historical data & state transitions
- ✅ **Waveform Diagrams** - Auto-generated PNG charts for 6 key registers
- ✅ **HTML Reports** - Comprehensive reports with statistics & alerts
- ✅ **Detailed Logging** - File & console logging with DEBUG level

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Ys1234lol/mushroom-robot-monitor.git
cd mushroom-robot-monitor

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `mushroom_robot_monitor.py` (lines 23-28) with your network settings:

```python
MODBUS_HOST = "192.168.2.88"   # Your PLC IP
MODBUS_PORT = 502

MQTT_BROKER = "192.168.1.107"  # Your MQTT broker IP
MQTT_PORT = 1885
```

### Run

```bash
python mushroom_robot_monitor.py
```

Expected output:
```
logs/
├── mushroom_robot_monitor.log      # Detailed log file
├── monitoring_data.db              # SQLite database
├── waveforms/                      # PNG diagrams
│   ├── CurrentPosition_waveform.png
│   ├── DistanceToPickingRobot_waveform.png
│   ├── RunningMode_waveform.png
│   ├── MovingStatus_waveform.png
│   ├── BehaviorStatus_waveform.png
│   └── CollectedMushroomCount_waveform.png
└── reports/
    └── report_20260512_103045.html # HTML report
```

## 📊 Architecture

### Data Flow

```
PLC (Modbus TCP)
    ↓
Modbus Monitor (reads 22 registers every 0.5s)
    ↓
State Analyzer (detects transitions & anomalies)
    ↓
Database (stores all data in SQLite)
    ↓
MQTT Monitor (receives from Picking Robot & Elevator)
    ↓
Waveform Generator & Report Generator
```

### Modbus Registers (Read-Only)

| Register | Address | Type | Description |
|----------|---------|------|-------------|
| DeviceID | 2000 | int16 | Device number (2001 for transfer robot) |
| DeviceType | 2001 | int16 | Device type identifier |
| RunningMode | 2003 | int16 | 1=Stop, 2=Running, 3=Debugging |
| MovingStatus | 2004 | int16 | 1=Forward, 2=Backward, 3=Standby |
| BehaviorStatus | 2006 | int16 | 1=Approaching, 2=Docking, 3=Docked |
| CurrentPosition | 2007 | int32 | Distance to elevator (mm) |
| DistanceToPickingRobot | 2009 | int32 | Distance to picking robot (mm) |
| CollectedMushroomCount | 2013 | int16 | Mushroom count |
| ESTOP | 2014 | int16 | Emergency stop (0/1) |
| Error | 2015 | int16 | Error state (0/1) |
| ErrorCode | 2016 | int16 | Error code value |
| BasketStatus | 2018 | int16 | 0=Waiting, 1=Extended, 2=Full, 3=Retracted |

### MQTT Topics

**Published (Transfer Robot → Others):**
- `AgaricusBisporusHarvesting/TR2001` - Transfer robot status

**Subscribed (Others → Transfer Robot):**
- `AgaricusBisporusHarvesting/PR0001` - Picking robot commands
- `AgaricusBisporusHarvesting/EL0001` - Elevator commands

## 🔔 Alert Types & Severity

| Alert Type | Severity | Trigger |
|-----------|----------|---------|
| ESTOP_TRIGGERED | CRITICAL | Emergency stop activated |
| ERROR_STATE | HIGH | Device error detected |
| INVALID_MOVEMENT_STATUS | HIGH | Invalid movement mode |
| INVALID_BASKET_STATUS | MEDIUM | Invalid basket state |
| MQTT_ERROR | HIGH | MQTT error message received |
| PROXIMITY_WARNING | MEDIUM | Close to target (<100mm) |

## 📈 State Machines

### RunningMode
- **Stop (1)** - Device stopped or in error
- **Running (2)** - Normal operation
- **Debugging (3)** - Debug mode

### BehaviorStatus
- **Approaching (1)** - Moving toward target
- **Docking (2)** - Aligning with target
- **Docked (3)** - Successfully docked

### BasketStatus
- **Waiting (0)** - In home position
- **Extended (1)** - Basket extending
- **Full (2)** - Basket fully extended
- **Retracted (3)** - Basket retracted

## 🗄️ Database Schema

### modbus_registers
Stores all Modbus register readings with timestamps

### mqtt_messages
Archives all MQTT messages for analysis

### state_transitions
Tracks all state machine changes with timestamps

### alerts
Logs all alerts with severity levels

## 📝 Example Output

```
2026-05-12 10:30:45 - [INFO] - ✓ Connected to Modbus TCP: 192.168.2.88:502
2026-05-12 10:30:45 - [INFO] - ✓ Connected to MQTT broker: 192.168.1.107:1885
2026-05-12 10:30:45 - [INFO] - 🚀 Mushroom Robot Monitoring System Started
2026-05-12 10:30:46 - [INFO] - 📊 State Change: RunningMode → Stop → Running
2026-05-12 10:30:47 - [INFO] - 📊 State Change: BehaviorStatus → Approaching → Docking
2026-05-12 10:30:50 - [INFO] - ✓ Docking completed successfully
2026-05-12 10:31:02 - [WARNING] - 🚨 ALERT [CRITICAL] ESTOP_TRIGGERED: Emergency stop activated!
2026-05-12 10:35:00 - [INFO] - ✓ Generated waveform: logs/waveforms/RunningMode_waveform.png
2026-05-12 10:35:01 - [INFO] - ✓ Generated report: logs/reports/report_20260512_103501.html
```

## 🔧 Troubleshooting

### Connection Issues
- Check PLC IP: `ping 192.168.2.88`
- Check MQTT IP: `ping 192.168.1.107`
- Verify ports: 502 (Modbus), 1885 (MQTT)

### No Data Received
- Check Modbus/MQTT broker is running
- Verify firewall allows connections
- Check register addresses match your PLC

### Database Errors
- Delete `logs/monitoring_data.db` and restart
- Check write permissions in `logs/` directory

## 📚 Additional Resources

See `PROTOCOL.md` for detailed technical specifications.

## 📄 License

MIT License - See LICENSE file

## 👨‍💻 Author

Created for mushroom harvesting robot monitoring system
