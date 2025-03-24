# Bold Protocol Economic Model

This folder contains a comprehensive Python economic model of the Bold Protocol, a multi-collateral stablecoin system. The model simulates the core components of the protocol including troves (vaults), stability pool, liquidations, redemptions, and interest accrual.

The model is extensively documented with detailed explanations of economic concepts and mechanisms based on the Liquity whitepaper, making it easy for developers and economists to understand the protocol's design and behavior even without prior knowledge of DeFi lending protocols.

## Overview

The Bold Protocol is a decentralized stablecoin system where users can create troves (vaults) by depositing collateral and minting BOLD stablecoins. The system includes several key components:

- **Troves (Vaults)**: Individual positions where users deposit collateral and draw BOLD debt
- **Batches**: Collections of troves managed together with shared interest rates and management fees
- **Stability Pool**: A pool of BOLD tokens used to liquidate risky troves
- **Liquidations**: Process of closing undercollateralized troves
- **Redemptions**: Mechanism to exchange BOLD for collateral

## Project Structure

The model is organized into the following directories:

### `/core`
Core model implementation files:
- `active_pool.py`: Manages the collateral and debt for all active troves
- `bold_token.py`: Simulates the BOLD stablecoin token
- `coll_surplus_pool.py`: Holds surplus collateral from liquidations for users to claim
- `default_pool.py`: Holds collateral and debt from liquidated troves for redistribution
- `stability_pool.py`: Simulates the stability pool for liquidations
- `trove_manager.py`: Core logic for trove operations, liquidations, and redemptions
- `economic_model.py`: Combines all components for a complete system simulation
- `vault_model.py`: Original simplified model (for reference)

### `/sim`
Simulation examples and visualization scripts:
- `simple_simulation.py`: A basic simulation of the Bold Protocol
- `simulation_example.py`: More advanced examples of using the model for different scenarios
- `visualization_simulation.py`: Simulation with visualization outputs

### `/test`
Test files for model validation:
- `test_vault_model.py`: Unit tests for the original model

## Usage

To use the economic model:

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the simulation examples:

```bash
# Run the simple simulation
python -m sim.simple_simulation

# Run the full simulation with different scenarios
python -m sim.simulation_example

# Run the visualization simulation
python -m sim.visualization_simulation
```

3. Import the model in your own scripts:

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
from economic_model import BoldProtocolEconomicModel

# Initialize the model
model = BoldProtocolEconomicModel(initial_price=2000.0)

# Create troves
trove_id = model.open_trove("user1", collateral=3.0, debt=4000.0, interest_rate=0.05)

# Create batches
model.create_batch("manager1", interest_rate=0.07, management_fee=0.02)

# Join batches
model.join_batch(trove_id, "manager1")

# Simulate price movements
model.update_price(1800.0)

# Run full simulations
results = model.simulate_market_scenario(days=30, price_volatility=0.03, plot_results=True)
```

4. Run tests:

```bash
python -m unittest test.test_vault_model
```

## Key Model Features

- **Interest Accrual**: Simulates interest on individual troves and batches
- **Batch Management**: Troves can join batches with shared interest rates and fees
- **Liquidations**: Automatic liquidation of undercollateralized troves
- **Price Simulations**: Random price movements to test system stability
- **Stability Pool**: Deposits, withdrawals, and liquidation handling
- **Redemptions**: Converting BOLD back to collateral
- **Visualizations**: Charts showing system state over time
- **Thorough Documentation**: Detailed explanations of core protocol concepts
- **Economic Mechanism Explanations**: Each function is documented with its economic purpose and how it contributes to protocol stability
- **User-Centric Documentation**: Explains why users would call different functions and their expected outcomes

## Limitations

This model is a simplified version of the full Bold Protocol and has several limitations:

- No gas costs or transaction fees
- Simplified price feed without oracles
- No governance mechanisms
- Limited multi-collateral support (focused on ETH)
- No external integrations with DeFi protocols
- Simplified sorting of troves by interest rate

## License

See the LICENSE file in the parent directory.