#!/usr/bin/env python3
"""
MQTT Broker & Client Simulator
Simulates MQTT broker and clients for testing
"""

import paho.mqtt.client as mqtt
import json
import time
import logging
import threading
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

class MQTTSimulator:
    """
    Simulates MQTT clients publishing robot status
    """
    
    def __init__(self, broker='localhost', port=1885):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id="mqtt-simulator")
        self.running = False
        
        # Simulation state
        self.robot_state = {
            'DeviceID': 2001,
            'RunningMode': 2,        # 1=Stop, 2=Running, 3=Debug
            'MovingStatus': 1,       # 1=Forward, 2=Backward, 3=Standby
            'BehaviorStatus': 1,     # 1=Approaching, 2=Docking, 3=Docked
            'CurrentPosition': 1000,
            'DistanceToPickingRobot': 500,
            'CollectedMushroomCount': 42,
            'ESTOP': 0,
            'Error': 0,
            'ErrorCode': 0,
            'BasketStatus': 0,
            'RoomID': 3,
            'ShelfID': 5,
            'CurrentFloor': 2,
            'TaskType': 1,
        }
        
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """
        Setup MQTT callbacks
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for connection
        """
        if rc == 0:
            logger.info(f"✓ MQTT Simulator connected to broker at {self.broker}:{self.port}")
            # Subscribe to command topics
            client.subscribe("AgaricusBisporusHarvesting/PR0001", qos=1)
            client.subscribe("AgaricusBisporusHarvesting/EL0001", qos=1)
        else:
            logger.error(f"✗ Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """
        Callback for incoming messages
        """
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📨 Received from {msg.topic}: {payload}")
            
            # Simulate responding to commands
            if msg.topic == "AgaricusBisporusHarvesting/PR0001":
                logger.info("🤖 Picking robot command received")
            elif msg.topic == "AgaricusBisporusHarvesting/EL0001":
                logger.info("🛗 Elevator command received")
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from {msg.topic}")
    
    def on_disconnect(self, client, userdata, rc):
        """
        Callback for disconnection
        """
        if rc != 0:
            logger.warning(f"⚠️  Unexpected disconnection: {rc}")
    
    def connect(self):
        """
        Connect to MQTT broker
        """
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to MQTT: {str(e)}")
            return False
    
    def simulate_behavior(self):
        """
        Simulate robot behavior and publish updates
        """
        logger.info("🤖 Starting MQTT behavior simulation...")
        
        cycle = 0
        while self.running:
            cycle += 1
            
            # Simulate movement
            if cycle % 3 == 0:
                self.robot_state['CurrentPosition'] -= 50
                if self.robot_state['CurrentPosition'] <= 100:
                    self.robot_state['BehaviorStatus'] = 2  # Docking
                    logger.info("📍 Entering docking mode...")
            
            if cycle % 10 == 0:
                self.robot_state['CollectedMushroomCount'] += 1
                logger.info(f"🍄 Collected! Total: {self.robot_state['CollectedMushroomCount']}")
            
            # Simulate occasional errors
            if random.random() < 0.05:
                self.robot_state['Error'] = 1
                self.robot_state['ErrorCode'] = random.randint(101, 199)
                logger.warning(f"⚠️  Error: {self.robot_state['ErrorCode']}")
            else:
                self.robot_state['Error'] = 0
                self.robot_state['ErrorCode'] = 0
            
            # Publish status
            payload = json.dumps({
                **self.robot_state,
                'timestamp': datetime.now().isoformat()
            })
            
            self.client.publish(
                "AgaricusBisporusHarvesting/TR2001",
                payload,
                qos=0
            )
            
            logger.debug(f"📤 Published to TR2001: {payload[:80]}...")
            
            time.sleep(2)  # Publish every 2 seconds
    
    def start(self):
        """
        Start the MQTT simulator
        """
        self.running = True
        
        if not self.connect():
            return
        
        time.sleep(1)  # Wait for connection
        
        # Start behavior simulation
        behavior_thread = threading.Thread(target=self.simulate_behavior, daemon=True)
        behavior_thread.start()
        
        logger.info("🚀 MQTT Simulator started")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping simulator...")
            self.stop()
    
    def stop(self):
        """
        Stop the simulator
        """
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("✓ MQTT Simulator stopped")


if __name__ == "__main__":
    # Try to connect to local MQTT broker
    simulator = MQTTSimulator(broker='localhost', port=1885)
    simulator.start()
