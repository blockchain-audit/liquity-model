"""
Debug file to identify issues with trove IDs in vault_model.py
"""

import sys
import os
from pathlib import Path

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from vault_model import BoldProtocol, Trove, InterestBatch, MIN_DEBT, DECIMAL_PRECISION, MCR_WETH, CCR_WETH

def main():
    # Create protocol
    protocol = BoldProtocol(initial_eth_price=2000.0)
    
    # Create troves
    a_trove_id = protocol.open_trove("UserA", 2.0, 3500.0, 0.01)
    b_trove_id = protocol.open_trove("UserB", 5.0, 7000.0, 0.02)
    c_trove_id = protocol.open_trove("UserC", 10.0, 2000.0, 0.03)
    
    print(f"Trove IDs: A={a_trove_id}, B={b_trove_id}, C={c_trove_id}")
    print(f"Troves dict keys: {list(protocol.troves.keys())}")
    
    # Drop price
    drop_price = 1000.0
    protocol.update_eth_price(drop_price)
    
    # Check keys again
    print(f"Troves dict keys after price update: {list(protocol.troves.keys())}")
    
    # Try to access trove A
    if a_trove_id in protocol.troves:
        print(f"Trove A is still in the protocol with ICR: {protocol.troves[a_trove_id].icr(drop_price)}")
    else:
        print(f"Trove A (ID {a_trove_id}) is no longer in the protocol!")
    
    # Check all troves
    for trove_id, trove in protocol.troves.items():
        print(f"Trove {trove_id}: ICR = {trove.icr(drop_price)} at price {drop_price}")

if __name__ == "__main__":
    main()