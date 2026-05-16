#!/usr/bin/env python3
"""
Testing Script - Run the monitoring system with simulators

This script starts both Modbus and MQTT simulators, then runs the monitor.
Perfect for testing without real hardware!
"""

import subprocess
import time
import sys
import os
import signal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self):
        self.processes = []
    
    def start_simulator(self, script_name, description):
        """
        Start a simulator process
        """
        logger.info(f"🚀 Starting {description}...")
        try:
            process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self.processes.append(process)
            logger.info(f"✓ {description} started (PID: {process.pid})")
            return process
        except Exception as e:
            logger.error(f"✗ Failed to start {description}: {str(e)}")
            return None
    
    def run_monitor(self):
        """
        Run the monitoring system
        """
        logger.info("🎯 Starting monitoring system...")
        
        try:
            # Import and run monitor
            from mushroom_robot_monitor import MushroomRobotMonitor
            
            monitor = MushroomRobotMonitor()
            monitor.start(duration=300)  # Run for 5 minutes
        except Exception as e:
            logger.error(f"✗ Monitor error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def cleanup(self):
        """
        Clean up all processes
        """
        logger.info("🧹 Cleaning up...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        logger.info("✓ Cleanup complete")
    
    def run(self):
        """
        Run the full test suite
        """
        logger.info("="*60)
        logger.info("🤖 MUSHROOM ROBOT MONITOR - TEST SUITE")
        logger.info("="*60)
        
        try:
            # Note: Modbus simulator with server requires special handling
            # For now, we'll skip it and use the MQTT simulator
            
            # Start MQTT simulator
            self.start_simulator('mqtt_simulator.py', 'MQTT Simulator')
            
            # Wait for simulator to start
            time.sleep(2)
            
            # Run the monitor
            self.run_monitor()
            
        except KeyboardInterrupt:
            logger.info("\n⏹️  Test interrupted by user")
        finally:
            self.cleanup()
            logger.info("✓ Test complete")


if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
