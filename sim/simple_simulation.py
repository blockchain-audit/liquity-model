"""
Simple simulation for Bold Protocol Economic Model.

This script demonstrates a minimal simulation of the Bold Protocol.
"""

import time
import sys
import os

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))
from vault_model import BoldProtocol

# Create mock numpy for testing without dependencies
class MockNumpy:
    def __init__(self):
        import random
        self.random = self
        self.uniform = self.random_uniform
    
    @staticmethod
    def random_uniform(low, high):
        import random
        return random.uniform(low, high)

np = MockNumpy()

def run_basic_simulation():
    # Initialize the protocol
    protocol = BoldProtocol(initial_eth_price=2000.0)
    
    print("Creating initial troves...")
    # Create some initial troves
    for i in range(5):
        collateral = np.random.uniform(3.0, 8.0)
        debt = collateral * 2000 / 1.5  # targeting ~150% collateralization
        trove_id = protocol.open_trove(f"user{i}", collateral, debt, 0.05)
        print(f"Trove {trove_id}: {collateral:.2f} ETH, {debt:.2f} BOLD")
    
    # Create a batch
    print("\nCreating batch manager...")
    protocol.create_batch("batch_manager_1", 0.07, 0.02)
    
    # Add some troves to batch
    print("\nAdding troves to batch...")
    for i in range(1, 3):
        try:
            protocol.join_batch(i, "batch_manager_1")
            print(f"Added trove {i} to batch")
        except ValueError:
            print(f"Failed to add trove {i} to batch")
    
    # Add to stability pool
    print("\nAdding to stability pool...")
    protocol.stability_pool.deposit("sp_user_1", 5000)
    print("Added 5000 BOLD to stability pool")
    
    # Run a simplified simulation
    print("\nRunning simplified simulation...")
    # Get initial protocol state
    print("Initial protocol state:")
    
    # Calculate protocol totals
    total_collateral = sum(trove.collateral for trove in protocol.troves.values())
    total_debt = sum(trove.debt for trove in protocol.troves.values())
    
    print(f"  Total collateral: {total_collateral:.2f} ETH")
    print(f"  Total debt: {total_debt:.2f} BOLD")
    print(f"  ETH price: ${protocol.eth_price:.2f}")
    print(f"  Number of troves: {len(protocol.troves)}")
    print(f"  Stability pool balance: {protocol.stability_pool.total_deposits:.2f} BOLD")
    
    # Simulate a price change
    new_price = 1800.0
    print(f"\nSimulating price drop to ${new_price:.2f}")
    protocol.update_eth_price(new_price)
    
    # Check liquidation status after price change
    liquidatable_troves = []
    for trove_id, trove in protocol.troves.items():
        if trove.icr(protocol.eth_price) < 1.1:  # 110% is the MCR
            liquidatable_troves.append(trove_id)
    
    if liquidatable_troves:
        print(f"Troves eligible for liquidation: {liquidatable_troves}")
        # Perform liquidation on the first trove
        if len(liquidatable_troves) > 0:
            protocol.liquidate_trove(liquidatable_troves[0])
            print(f"Liquidated trove {liquidatable_troves[0]}")
    else:
        print("No troves eligible for liquidation at this price")
    
    # Final state
    print("\nFinal protocol state:")
    
    # Calculate protocol totals again
    total_collateral = sum(trove.collateral for trove in protocol.troves.values())
    total_debt = sum(trove.debt for trove in protocol.troves.values())
    
    print(f"  Total collateral: {total_collateral:.2f} ETH")
    print(f"  Total debt: {total_debt:.2f} BOLD")
    print(f"  ETH price: ${protocol.eth_price:.2f}")
    print(f"  Number of troves: {len(protocol.troves)}")
    print(f"  Stability pool balance: {protocol.stability_pool.total_deposits:.2f} BOLD")

if __name__ == "__main__":
    run_basic_simulation()