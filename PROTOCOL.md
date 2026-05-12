# Technical Protocol Specification

## System Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   PLC / HMI     │         │  Picking Robot   │
│  (Modbus TCP)   │         │  (MQTT PR0001)   │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │ Modbus TCP (502)         │ MQTT (1885)
         │                          │
    ┌────▼──────────────────────────▼────┐
    │   Transfer Robot Monitor (2001)     │
    │   ├─ Modbus Monitor                 │
    │   ├─ MQTT Monitor                   │
    │   ├─ State Analyzer                 │
    │   ├─ Waveform Generator             │
    │   └─ Report Generator               │
    └────┬──────────────────────────┬────┘
         │                          │
         └─────────┬────────────────┘
                   │
            ┌──────▼──────┐
            │ SQLite DB   │
            │ & Reports   │
            └─────────────┘
```

## Modbus TCP Registers

### Input Registers (Read-Only, Address 2000-2027)

```
Address | Name                        | Type  | Range     | Unit
--------|-----------------------------|----- -|-----------|------
2000    | DeviceID                    | int16 | 0-9999    | -
2001    | DeviceType                  | int16 | 0-99      | -
2002    | MatchedDeviceID             | int16 | 0-9999    | -
2003    | RunningMode                 | int16 | 1-3       | enum
2004    | MovingStatus                | int16 | 1-3       | enum
2005    | MovingTarget                | int16 | 1-2       | enum
2006    | BehaviorStatus              | int16 | 1-3       | enum
2007-08 | CurrentPosition             | int32 | -999...999| mm
2009-10 | DistanceToPickingRobot      | int32 | -999...999| mm
2011    | PickingRobotDetected        | int16 | 0-1       | bool
2012    | CuttingReady                | int16 | 0-1       | bool
2013    | CollectedMushroomCount      | int16 | 0-9999    | count
2014    | ESTOP                       | int16 | 0-1       | bool
2015    | Error                       | int16 | 0-1       | bool
2016    | ErrorCode                   | int16 | 0-65535   | code
2017    | HorizontalMaxCount          | int16 | 0-9999    | -
2018    | BasketStatus                | int16 | 0-3       | enum
2019    | RoomID                      | int16 | 0-999     | -
2020    | ShelfID                     | int16 | 0-99      | -
2021    | CurrentFloor                | int16 | 0-99      | -
2022    | TaskType                    | int16 | 0-99      | -
```

### MQTT Message Format

**Topic**: `AgaricusBisporusHarvesting/TR2001`

```json
{
  "DeviceID": 2001,
  "RunningMode": 2,
  "MovingStatus": 1,
  "BehaviorStatus": 2,
  "CurrentPosition": 500,
  "DistanceToPickingRobot": 300,
  "CollectedMushroomCount": 45,
  "ESTOP": 0,
  "Error": 0,
  "ErrorCode": 0,
  "BasketStatus": 1,
  "RoomID": 3,
  "ShelfID": 5,
  "CurrentFloor": 2,
  "timestamp": 1715500245.123
}
```

## State Enumerations

### RunningMode (Register 2003)
- 1 = **Stop** - Device stopped or error
- 2 = **Running** - Normal operation
- 3 = **Debugging** - Debug mode

### MovingStatus (Register 2004)
- 1 = **Forward** - Moving toward target
- 2 = **Backward** - Moving away
- 3 = **Standby** - Not moving

### MovingTarget (Register 2005)
- 1 = **PickingRobot** - Moving to picking robot
- 2 = **Lift** - Moving to lift/elevator

### BehaviorStatus (Register 2006)
- 1 = **Approaching** - Approaching target
- 2 = **Docking** - Aligning with target
- 3 = **Docked** - Successfully docked

### BasketStatus (Register 2018)
- 0 = **Waiting** - In home position
- 1 = **Extended** - Basket extending
- 2 = **ExtendedFull** - Fully extended
- 3 = **Retracted** - Retracted position

## Alert Rules

| Trigger | Alert Type | Severity | Action |
|---------|-----------|----------|--------|
| Register 2014 = 1 | ESTOP_TRIGGERED | CRITICAL | Immediate stop |
| Register 2015 = 1 | ERROR_STATE | HIGH | Log error code |
| Position < 100mm | PROXIMITY_WARNING | MEDIUM | Reduce speed |
| Distance < 100mm | PROXIMITY_WARNING | MEDIUM | Alert operator |
| Invalid enum | INVALID_STATE | HIGH | Log and alert |

## Communication Timing

- **Modbus Read Cycle**: 0.5 seconds
- **MQTT Publish Interval**: On data change (delta compression)
- **Keep-Alive**: 60 seconds
- **Timeout**: 5000 ms

## Error Codes (Register 2016)

```
0    = No error
1-99 = Hardware errors
100-199 = Communication errors
200-299 = Sensor errors
300-399 = Movement errors
400-499 = Device-specific errors
```

## Register Mapping Summary

### Position Tracking
- **CurrentPosition** (2007-2008) - Distance to elevator in mm
- **DistanceToPickingRobot** (2009-2010) - Distance to picking robot in mm

### State Tracking
- **RunningMode** (2003) - Overall device state (Stop/Running/Debug)
- **MovingStatus** (2004) - Current movement direction (Forward/Backward/Standby)
- **BehaviorStatus** (2006) - Docking state (Approaching/Docking/Docked)

### Task Management
- **MovingTarget** (2005) - Target destination (Picking Robot/Lift)
- **TaskType** (2022) - Task identifier
- **RoomID** (2019) - Room/Location ID
- **ShelfID** (2020) - Shelf/Position ID
- **CurrentFloor** (2021) - Floor/Level number

### Status & Control
- **CollectedMushroomCount** (2013) - Mushroom collection counter
- **BasketStatus** (2018) - Basket position state
- **ESTOP** (2014) - Emergency stop flag
- **Error** (2015) - Error state flag
- **ErrorCode** (2016) - Specific error code
