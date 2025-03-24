"""
Visualization simulation for Bold Protocol Economic Model.

This script demonstrates the Bold Protocol with visualizations.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))
from vault_model import BoldProtocol

def run_visualization_simulation():
    # Initialize the protocol
    protocol = BoldProtocol(initial_eth_price=2000.0)
    
    print("Creating initial troves...")
    # Create some initial troves with varying collateral and risk profiles
    for i in range(10):
        collateral = np.random.uniform(2.0, 10.0)
        # Target different collateralization ratios from 120% to 200%
        target_cr = 1.2 + (i * 0.8 / 10)  
        debt = collateral * 2000 / target_cr
        trove_id = protocol.open_trove(f"user{i}", collateral, debt, 0.05)
        print(f"Trove {trove_id}: {collateral:.2f} ETH, {debt:.2f} BOLD, CR: {target_cr*100:.0f}%")
    
    # Create a batch
    print("\nCreating batch manager...")
    protocol.create_batch("batch_manager_1", 0.07, 0.02)
    
    # Add some troves to batch
    print("\nAdding troves to batch...")
    for i in range(1, 6):
        try:
            protocol.join_batch(i, "batch_manager_1")
            print(f"Added trove {i} to batch")
        except ValueError:
            print(f"Failed to add trove {i} to batch")
    
    # Add to stability pool
    print("\nAdding to stability pool...")
    protocol.stability_pool.deposit("sp_user_1", 10000)
    protocol.stability_pool.deposit("sp_user_2", 5000)
    print("Added 15000 BOLD to stability pool")
    
    # Run a simulation with price movements and plot results
    print("\nRunning simulation with visualizations...")
    results = protocol.simulate_market_scenario(30, price_volatility=0.03, plot_results=True)
    
    print("\nSimulation Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    run_visualization_simulation()