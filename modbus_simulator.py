#!/usr/bin/env python3
"""
Modbus TCP Simulator
Simulates a PLC with Modbus TCP server for testing
"""

import threading
import time
import logging
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

try:
    from pymodbus.server import StartTcpServer
    from pymodbus.datastore import ModbusSequentialDataStore
    from pymodbus.device import ModbusDeviceIdentification
    from pymodbus.datastore.store import ModbusSlaveContext, ModbusServerContext
except ImportError:
    logger.error("pymodbus not installed. Install with: pip install pymodbus")
    exit(1)

class ModbusSimulator:
    """
    Simulates a Modbus TCP server with realistic robot behavior
    """
    
    def __init__(self, host='0.0.0.0', port=502):
        self.host = host
        self.port = port
        self.running = False
        self.server_thread = None
        
        # Register values (will be updated by simulation)
        self.registers = {
            2000: 2001,      # DeviceID
            2001: 1,         # DeviceType
            2002: 1001,      # MatchedDeviceID
            2003: 2,         # RunningMode (1=Stop, 2=Running, 3=Debug)
            2004: 3,         # MovingStatus (1=Forward, 2=Backward, 3=Standby)
            2005: 1,         # MovingTarget (1=PickingRobot, 2=Lift)
            2006: 1,         # BehaviorStatus (1=Approaching, 2=Docking, 3=Docked)
            2007: 1000,      # CurrentPosition (high word)
            2008: 0,         # CurrentPosition (low word)
            2009: 500,       # DistanceToPickingRobot (high word)
            2010: 0,         # DistanceToPickingRobot (low word)
            2011: 1,         # PickingRobotDetected (0/1)
            2012: 1,         # CuttingReady (0/1)
            2013: 42,        # CollectedMushroomCount
            2014: 0,         # ESTOP (0/1)
            2015: 0,         # Error (0/1)
            2016: 0,         # ErrorCode
            2017: 100,       # HorizontalMaxCount
            2018: 0,         # BasketStatus (0=Waiting, 1=Extended, 2=Full, 3=Retracted)
            2019: 3,         # RoomID
            2020: 5,         # ShelfID
            2021: 2,         # CurrentFloor
            2022: 1,         # TaskType
        }
        
        self.simulation_state = {
            'mode': 'moving',  # moving, docking, docked, error
            'position': 1000,
            'target_position': 100,
            'mushroom_count': 42,
            'basket_status': 0,
            'error_triggered': False
        }
    
    def create_server(self):
        """
        Create and configure Modbus TCP server
        """
        # Create data store
        store = ModbusSequentialDataStore()
        context = ModbusSlaveContext(
            di=store,
            co=store,
            hr=store,
            ir=store
        )
        
        # Initialize holding registers
        for address, value in self.registers.items():
            context.setValues(3, address, [value])  # 3 = holding registers
        
        contexts = {0x00: context}
        identity = ModbusDeviceIdentification(
            info_name='Mushroom Robot Simulator',
            info_code='MR2001',
            info_url='http://localhost:502'
        )
        
        return ModbusServerContext(contexts, single=False), identity
    
    def simulate_behavior(self):
        """
        Simulate realistic robot behavior
        """
        logger.info("🤖 Starting Modbus behavior simulation...")
        
        cycle = 0
        while self.running:
            cycle += 1
            
            # Simulate different behaviors
            state = self.simulation_state['mode']
            
            if state == 'moving':
                # Robot is moving toward target
                self.simulation_state['position'] -= 50
                if self.simulation_state['position'] <= 100:
                    self.simulation_state['mode'] = 'docking'
                    logger.info("📍 Entering docking mode...")
                
                self.registers[2004] = 1  # MovingStatus = Forward
                self.registers[2006] = 1  # BehaviorStatus = Approaching
            
            elif state == 'docking':
                # Robot is docking
                self.registers[2004] = 3  # MovingStatus = Standby
                self.registers[2006] = 2  # BehaviorStatus = Docking
                
                if cycle % 3 == 0:
                    self.simulation_state['mode'] = 'docked'
                    logger.info("✓ Docking complete!")
            
            elif state == 'docked':
                # Robot is docked
                self.registers[2006] = 3  # BehaviorStatus = Docked
                self.registers[2012] = 1  # CuttingReady
                
                # Simulate mushroom collection
                if cycle % 5 == 0 and self.simulation_state['mushroom_count'] < 100:
                    self.simulation_state['mushroom_count'] += 1
                    logger.info(f"🍄 Collected mushroom! Total: {self.simulation_state['mushroom_count']}")
                
                # After some time, move basket
                if cycle % 15 == 0:
                    self.simulation_state['mode'] = 'basket_extend'
                    self.simulation_state['basket_status'] = 1
                    logger.info("📦 Extending basket...")
            
            elif state == 'basket_extend':
                # Basket extending
                self.simulation_state['basket_status'] = 2
                self.registers[2018] = 2  # BasketStatus = Full
                
                if cycle % 5 == 0:
                    self.simulation_state['mode'] = 'return_home'
                    logger.info("🔄 Returning to home position...")
            
            elif state == 'return_home':
                # Return to home
                self.simulation_state['position'] += 100
                self.registers[2004] = 2  # MovingStatus = Backward
                
                if self.simulation_state['position'] >= 1000:
                    self.simulation_state['mode'] = 'moving'
                    self.simulation_state['position'] = 1000
                    self.simulation_state['basket_status'] = 0
                    self.registers[2018] = 0  # BasketStatus = Waiting
                    logger.info("🏠 Back at home position!")
            
            # Update registers
            self.registers[2003] = 2  # RunningMode = Running
            self.registers[2007] = (self.simulation_state['position'] >> 16) & 0xFFFF
            self.registers[2008] = self.simulation_state['position'] & 0xFFFF
            self.registers[2013] = self.simulation_state['mushroom_count']
            self.registers[2018] = self.simulation_state['basket_status']
            
            # Occasionally trigger an error (10% chance)
            if random.random() < 0.02 and not self.simulation_state['error_triggered']:
                self.registers[2015] = 1  # Error
                self.registers[2016] = random.randint(101, 199)  # Error code
                self.simulation_state['error_triggered'] = True
                logger.warning(f"⚠️  Error triggered! Code: {self.registers[2016]}")
            
            # Clear error after a few cycles
            if self.simulation_state['error_triggered'] and cycle % 10 == 0:
                self.registers[2015] = 0
                self.registers[2016] = 0
                self.simulation_state['error_triggered'] = False
                logger.info("✓ Error cleared")
            
            time.sleep(1)  # Update every 1 second
    
    def start(self):
        """
        Start the Modbus simulator
        """
        self.running = True
        
        # Start behavior simulation in background
        behavior_thread = threading.Thread(target=self.simulate_behavior, daemon=True)
        behavior_thread.start()
        
        logger.info(f"🚀 Modbus TCP Simulator starting on {self.host}:{self.port}")
        logger.info("Press Ctrl+C to stop")
        
        try:
            # Note: StartTcpServer is blocking, so we need to handle it differently
            # For now, we'll use a simple loop that updates values
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
        logger.info("✓ Simulator stopped")


if __name__ == "__main__":
    simulator = ModbusSimulator(host='0.0.0.0', port=502)
    simulator.start()
