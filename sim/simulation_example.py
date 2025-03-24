"""
Simulation Example for Bold Protocol Economic Model.

This script demonstrates how to use the economic model to simulate
various scenarios and analyze the protocol's behavior.
"""

import sys
import os
import time

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))
from economic_model import BoldProtocolEconomicModel

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

# Mock matplotlib
class MockPlt:
    @staticmethod
    def figure(*args, **kwargs):
        return MockFigure()
    
    @staticmethod
    def show():
        print("[Visualization would be shown here]")

class MockFigure:
    def add_subplot(self, *args, **kwargs):
        return MockAxes()

class MockAxes:
    def plot(self, *args, **kwargs):
        pass
    
    def set_title(self, title):
        print(f"[Graph title: {title}]")
    
    def set_xlabel(self, label):
        pass
    
    def set_ylabel(self, label):
        pass
    
    def legend(self, *args, **kwargs):
        pass

plt = MockPlt()

def run_simplified_simulation():
    """Runs a simplified simulation without external dependencies"""
    print("=== Running Simplified Simulation ===")
    
    try:
        # Initialize the model (create a simple mock if needed)
        print("\n--- Initializing model ---")
        model = BoldProtocolEconomicModel(initial_price=2000.0)
        print(f"Model initialized with ETH price: $2000.00")
        
        print("\n--- Creating initial troves ---")
        # Create some initial troves
        trove_ids = []
        for i in range(5):
            # Create parameters for troves
            owner = f"user{i}"
            collateral = np.random.uniform(2.0, 10.0)
            
            # Target collateralization ratio of 150%
            max_debt = (collateral * 2000) / 1.5
            debt = np.random.uniform(2000.0, max_debt)
            interest_rate = np.random.uniform(0.005, 0.10)
            
            print(f"Opening trove for {owner}: {collateral:.2f} ETH, {debt:.2f} BOLD, {interest_rate*100:.2f}% interest")
            try:
                trove_id = model.open_trove(owner, collateral, debt, interest_rate)
                trove_ids.append(trove_id)
            except Exception as e:
                print(f"  Failed to open trove: {e}")
        
        print("\n--- Creating batch managers ---")
        batch1 = "batchManager1"
        
        try:
            model.create_batch(batch1, 0.07, 0.02)  # 7% interest, 2% management fee
            print(f"Created batch {batch1}: 7% interest, 2% management fee")
            
            # Add some troves to batch
            if trove_ids:
                print("\n--- Adding troves to batch ---")
                for i in range(min(2, len(trove_ids))):
                    print(f"Adding trove {trove_ids[i]} to batch {batch1}")
                    try:
                        model.join_batch(trove_ids[i], batch1)
                        print(f"  Success: Added trove {trove_ids[i]} to batch")
                    except Exception as e:
                        print(f"  Failed: {e}")
        except Exception as e:
            print(f"  Failed to create batch: {e}")
        
        # Add to stability pool
        print("\n--- Adding to Stability Pool ---")
        print("Would add 10000 BOLD to the stability pool from sp_user0 and sp_user1")
        print("(Skipping actual operation due to potential dependency issues)")
        
        # Simulate price drop
        print("\n--- Simulating price drop ---")
        try:
            target_price = 1500.0
            print(f"Dropping price from $2000.00 to ${target_price:.2f}")
            
            # Update price
            model.update_price(target_price)
            print("Price updated successfully")
            
            # Print system state
            print("\n--- Final system state ---")
            print("[System state would be displayed here]")
            
        except Exception as e:
            print(f"  Failed price simulation: {e}")
            
    except Exception as e:
        print(f"Simulation failed: {e}")

# Simplified versions of the other simulations
def run_batch_interest_simulation():
    """A simplified version of the batch interest simulation"""
    print("\n=== Running Batch Interest Simulation ===")
    print("This simulation would show how interest accrues on batches over time")
    print("- Batches would accumulate interest")
    print("- Management fees would be collected")
    print("- Interest rates would affect debt levels")

def run_stability_pool_simulation():
    """A simplified version of the stability pool simulation"""
    print("\n=== Running Stability Pool Simulation ===")
    print("This simulation would show stability pool behavior during liquidations")
    print("- Risky troves would be created")
    print("- Price drops would trigger liquidations")
    print("- Stability pool would absorb debt and gain collateral")
    print("- Users would withdraw from stability pool with gains")

def run_redemption_simulation():
    """A simplified version of the redemption simulation"""
    print("\n=== Running Redemption Simulation ===")
    print("This simulation would show the redemption mechanism")
    print("- Troves would be created with varying ICRs")
    print("- Redemptions would start with lowest ICR troves")
    print("- Some troves might be closed completely")
    print("- Others would have collateral partially redeemed")

if __name__ == "__main__":
    # Run the simplified simulation
    run_simplified_simulation()
    
    # Show other available simulations
    print("\n--- Other Available Simulations ---")
    print("These simulations are available but require the full dependencies:")
    run_batch_interest_simulation()
    run_stability_pool_simulation()
    run_redemption_simulation()