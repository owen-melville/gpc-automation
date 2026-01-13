#!/usr/bin/env python3
"""
Simple Experiment Creation Test - Using Wyatt's Exact Approach

This follows the exact pattern from Wyatt's command_line_app.py
to create an experiment using their intended workflow.
"""

import os
import uuid
from datetime import datetime
from astra_admin import AstraAdmin

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    """
    Simple experiment creation using Wyatt's exact approach
    """
    log("🚀 Simple Experiment Creation Test")
    log("Following Wyatt's exact pattern from command_line_app.py")
    
    # Step 1: Set automation identity (exactly like Wyatt does)
    log("=== Step 1: Setting Automation Identity ===")
    client_id = uuid.uuid4().hex
    
    AstraAdmin().set_automation_identity(
        "Simple Test App", 
        "1.0.0.0",
        os.getpid(),
        client_id,
        1
    )
    log("✓ Automation identity set")
    
    # Step 2: Wait for instruments (exactly like Wyatt does)
    log("=== Step 2: Waiting for Instruments ===")
    log("Calling AstraAdmin().wait_for_instruments()...")
    
    try:
        AstraAdmin().wait_for_instruments()
        log("✓ Instruments detected")
    except Exception as e:
        log(f"✗ Error waiting for instruments: {e}")
        return False
    
    # Step 3: Create experiment (exactly like Wyatt does)
    log("=== Step 3: Creating Experiment ===")
    method_path = r"//dbf/Method Builder/Owen/test_method_3"
    log(f"Template: {method_path}")
    log("Calling AstraAdmin().new_experiment_from_template()...")
    
    try:
        experiment_id = AstraAdmin().new_experiment_from_template(method_path)
        log(f"✓ Experiment created successfully - ID: {experiment_id}")
        
        # Get experiment name to confirm it's working
        try:
            exp_name = AstraAdmin().get_experiment_name(experiment_id)
            log(f"✓ Experiment name: {exp_name}")
        except Exception as e:
            log(f"⚠ Could not get experiment name: {e}")
        
        # Close experiment when done
        log("=== Cleanup ===")
        try:
            AstraAdmin().close_experiment(experiment_id)
            log("✓ Experiment closed")
        except Exception as e:
            log(f"⚠ Error closing experiment: {e}")
        
        return True
        
    except Exception as e:
        log(f"✗ Error creating experiment: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 SUCCESS: Experiment creation worked using Wyatt's approach!")
    else:
        print("\n✗ FAILED: Issue with Wyatt's intended workflow")
        print("This tells us where the real problem is")
        
    print("\nThis test uses ONLY Wyatt's intended methods:")
    print("• AstraAdmin().set_automation_identity()")
    print("• AstraAdmin().wait_for_instruments()")  
    print("• AstraAdmin().new_experiment_from_template()")
    print("• No direct COM calls, no timeouts, no workarounds")