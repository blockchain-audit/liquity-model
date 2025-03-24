"""
Unit tests for the Bold protocol vault economic model.
"""

import unittest
import sys
import os
import numpy as np

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))
from vault_model import BoldProtocol, Trove, InterestBatch, StabilityPool


class TestBoldProtocol(unittest.TestCase):
    def setUp(self):
        """Initialize a fresh protocol instance for each test"""
        self.protocol = BoldProtocol(initial_eth_price=2000.0)
    
    def test_open_trove(self):
        """Test creating a new trove"""
        trove_id = self.protocol.open_trove("user1", 3.0, 4000.0, 0.05)
        
        self.assertEqual(trove_id, 1)
        self.assertEqual(len(self.protocol.troves), 1)
        self.assertEqual(self.protocol.troves[trove_id].owner, "user1")
        self.assertEqual(self.protocol.troves[trove_id].collateral, 3.0)
        self.assertEqual(self.protocol.troves[trove_id].debt, 4000.0)
        self.assertEqual(self.protocol.troves[trove_id].interest_rate, 0.05)
        
        # Test system totals
        self.assertEqual(self.protocol.total_system_debt, 4000.0)
        self.assertEqual(self.protocol.total_collateral, 3.0)
    
    def test_open_trove_with_insufficient_collateral(self):
        """Test creating a trove with insufficient collateral"""
        # At ETH price of $2000, for 4000 BOLD, minimum collateral would be:
        # 4000 / 2000 * 1.1 = 2.2 ETH
        with self.assertRaises(ValueError):
            self.protocol.open_trove("user1", 2.0, 4000.0, 0.05)
    
    def test_open_trove_with_invalid_debt(self):
        """Test creating a trove with less than minimum debt"""
        with self.assertRaises(ValueError):
            self.protocol.open_trove("user1", 3.0, 1000.0, 0.05)
    
    def test_open_trove_with_invalid_interest_rate(self):
        """Test creating a trove with invalid interest rate"""
        with self.assertRaises(ValueError):
            self.protocol.open_trove("user1", 3.0, 4000.0, 0.003)  # Below min
        
        with self.assertRaises(ValueError):
            self.protocol.open_trove("user1", 3.0, 4000.0, 3.0)  # Above max
    
    def test_create_batch(self):
        """Test creating a batch manager"""
        self.protocol.create_batch("manager1", 0.07, 0.02)
        
        self.assertEqual(len(self.protocol.batches), 1)
        self.assertIn("manager1", self.protocol.batches)
        self.assertEqual(self.protocol.batches["manager1"].interest_rate, 0.07)
        self.assertEqual(self.protocol.batches["manager1"].management_fee, 0.02)
    
    def test_join_batch(self):
        """Test adding a trove to a batch"""
        # Create a trove and a batch
        trove_id = self.protocol.open_trove("user1", 4.0, 4000.0, 0.05)
        self.protocol.create_batch("manager1", 0.07, 0.02)
        
        # Join the batch
        self.protocol.join_batch(trove_id, "manager1")
        
        # Verify trove is in batch
        self.assertEqual(self.protocol.troves[trove_id].batch_manager, "manager1")
        self.assertEqual(self.protocol.troves[trove_id].interest_rate, 0.07)
        self.assertIn(trove_id, self.protocol.batches["manager1"].troves)
        
        # Verify batch totals
        self.assertEqual(self.protocol.batches["manager1"].total_debt, 4000.0)
        self.assertEqual(self.protocol.batches["manager1"].total_collateral, 4.0)
    
    def test_join_batch_insufficient_collateral(self):
        """Test joining a batch with insufficient collateral ratio"""
        # Create a trove with exactly 110% collateralization (MCR)
        trove_id = self.protocol.open_trove("user1", 2.2, 4000.0, 0.05)
        self.protocol.create_batch("manager1", 0.07, 0.02)
        
        # Joining batch requires MCR + BCR (110% + 10% = 120%)
        with self.assertRaises(ValueError):
            self.protocol.join_batch(trove_id, "manager1")
        
        # Add more collateral to meet batch requirement
        original_collateral = self.protocol.troves[trove_id].collateral
        self.protocol.troves[trove_id].collateral = 3.0  # More than 120% collateralization
        # Recalculate total collateral after modifying the trove
        self.protocol.total_collateral += (3.0 - original_collateral)
        self.protocol.join_batch(trove_id, "manager1")
        
        # Verify trove is now in batch
        self.assertEqual(self.protocol.troves[trove_id].batch_manager, "manager1")
    
    def test_interest_accrual_individual(self):
        """Test interest accrual for an individual trove"""
        trove_id = self.protocol.open_trove("user1", 3.0, 4000.0, 0.05)
        
        # Advance time by 1 year
        self.protocol.update_time(365 * 24 * 60 * 60)
        
        # Apply interest
        self.protocol._apply_interest(trove_id)
        
        # After 1 year at 5% interest, debt should be 4000 * 1.05 = 4200
        expected_debt = 4000.0 * 1.05
        self.assertAlmostEqual(self.protocol.troves[trove_id].debt, expected_debt, delta=1.0)
    
    def test_interest_accrual_batch(self):
        """Test interest accrual for a trove in a batch"""
        # Create a trove and a batch
        trove_id = self.protocol.open_trove("user1", 4.0, 4000.0, 0.05)
        self.protocol.create_batch("manager1", 0.07, 0.02)
        
        # Join the batch
        self.protocol.join_batch(trove_id, "manager1")
        
        # Advance time by 1 year
        self.protocol.update_time(365 * 24 * 60 * 60)
        
        # Apply interest
        self.protocol._apply_interest(trove_id)
        
        # After 1 year at 7% interest, debt should be 4000 * 1.07 = 4280
        expected_debt = 4000.0 * 1.07
        self.assertAlmostEqual(self.protocol.troves[trove_id].debt, expected_debt, delta=1.0)
    
    def test_liquidation_with_stability_pool(self):
        """Test liquidation using the stability pool"""
        # Create a trove just above MCR
        trove_id = self.protocol.open_trove("user1", 2.3, 4000.0, 0.05)
        
        # Add funds to stability pool
        self.protocol.stability_pool.deposit("sp_user1", 5000.0)
        
        # Drop ETH price to trigger liquidation
        # At 1800 USD/ETH, the trove's ICR would be (2.3 * 1800) / 4000 = 1.035 < 1.1 (MCR)
        self.protocol.update_eth_price(1800.0)
        
        # Verify the trove was liquidated
        self.assertNotIn(trove_id, self.protocol.troves)
        
        # Verify stability pool used for liquidation
        self.assertLess(self.protocol.stability_pool.total_deposits, 5000.0)
    
    def test_liquidation_without_stability_pool(self):
        """Test liquidation without stability pool coverage"""
        # Create a trove
        trove_id = self.protocol.open_trove("user1", 2.3, 4000.0, 0.05)
        
        # Drop ETH price to trigger liquidation
        # No stability pool deposits, so it should redistribute
        self.protocol.update_eth_price(1800.0)
        
        # Verify the trove was liquidated
        self.assertNotIn(trove_id, self.protocol.troves)
    
    def test_multiple_troves_and_batches(self):
        """Test a more complex scenario with multiple troves and batches"""
        # Create multiple troves
        trove_ids = []
        for i in range(5):
            collateral = 3.0 + i * 0.5  # 3.0, 3.5, 4.0, 4.5, 5.0
            debt = 4000.0
            trove_id = self.protocol.open_trove(f"user{i}", collateral, debt, 0.05)
            trove_ids.append(trove_id)
        
        # Create batches
        self.protocol.create_batch("manager1", 0.07, 0.02)
        self.protocol.create_batch("manager2", 0.06, 0.01)
        
        # Add troves to batches
        self.protocol.join_batch(trove_ids[0], "manager1")
        self.protocol.join_batch(trove_ids[1], "manager1")
        self.protocol.join_batch(trove_ids[2], "manager2")
        self.protocol.join_batch(trove_ids[3], "manager2")
        # Trove[4] remains individual
        
        # Verify batch assignments
        self.assertEqual(len(self.protocol.batches["manager1"].troves), 2)
        self.assertEqual(len(self.protocol.batches["manager2"].troves), 2)
        
        # Advance time and apply interest
        self.protocol.update_time(180 * 24 * 60 * 60)  # 180 days
        
        # Apply interest to all troves
        for trove_id in self.protocol.troves:
            self.protocol._apply_interest(trove_id)
        
        # Lower ETH price to trigger some liquidations
        self.protocol.update_eth_price(1800.0)
        
        # The least collateralized troves should be liquidated
        # At 1800 USD/ETH:
        # Trove0 (3.0 ETH): ICR = (3.0 * 1800) / (4000 * (1 + 0.07 * 0.5)) ~= 1.26 > 1.1
        # Trove1 (3.5 ETH): ICR = (3.5 * 1800) / (4000 * (1 + 0.07 * 0.5)) ~= 1.47 > 1.1
        # So all troves should survive
        
        # Verify system state
        self.assertEqual(len(self.protocol.troves), 5)
        
        # Drop price further to trigger liquidations
        self.protocol.update_eth_price(1500.0)
        
        # Now some troves should be liquidated
        # At 1500 USD/ETH:
        # Trove0 (3.0 ETH): ICR = (3.0 * 1500) / (4000 * (1 + 0.07 * 0.5)) ~= 1.05 < 1.1
        # Trove1 (3.5 ETH): ICR = (3.5 * 1500) / (4000 * (1 + 0.07 * 0.5)) ~= 1.23 > 1.1
        
        # First trove should be liquidated
        self.assertNotIn(trove_ids[0], self.protocol.troves)
        
        # Verify remaining troves
        self.assertGreaterEqual(len(self.protocol.troves), 4)
    
    def test_trove_icr_calculation(self):
        """Test Individual Collateralization Ratio calculation"""
        trove = Trove(id=1, owner="user1", collateral=3.0, debt=4000.0, interest_rate=0.05)
        eth_price = 2000.0
        
        # ICR should be (3.0 * 2000) / 4000 = 1.5
        self.assertAlmostEqual(trove.icr(eth_price), 1.5)
        
        # Test zero debt case (should return infinity)
        trove.debt = 0
        self.assertEqual(trove.icr(eth_price), float('inf'))
    
    def test_stability_pool_liquidation_distribution(self):
        """Test stability pool distribution during liquidation"""
        # Set up a stability pool with two depositors
        self.protocol.stability_pool.deposit("sp_user1", 3000.0)
        self.protocol.stability_pool.deposit("sp_user2", 2000.0)
        
        # Create a trove
        trove_id = self.protocol.open_trove("user1", 2.3, 4000.0, 0.05)
        
        # Drop ETH price to trigger liquidation
        self.protocol.update_eth_price(1800.0)
        
        # Verify the trove was liquidated
        self.assertNotIn(trove_id, self.protocol.troves)
        
        # Verify stability pool deposits were used
        self.assertLess(self.protocol.stability_pool.total_deposits, 5000.0)
        
        # Remaining deposits should reflect proportional loss
        total_remaining = sum(self.protocol.stability_pool.depositors.values())
        self.assertAlmostEqual(self.protocol.stability_pool.total_deposits, total_remaining, delta=0.001)
    
    def test_market_simulation(self):
        """Test market simulation with price movements"""
        # Create initial troves
        for i in range(5):
            collateral = 3.0 + i * 0.5  # 3.0, 3.5, 4.0, 4.5, 5.0
            debt = 4000.0
            self.protocol.open_trove(f"user{i}", collateral, debt, 0.05)
        
        # Run a short simulation (5 days with low volatility)
        results = self.protocol.simulate_market_scenario(5, price_volatility=0.01, plot_results=False)
        
        # Verify the simulation completed and returned results
        self.assertIn('final_eth_price', results)
        self.assertIn('final_system_debt', results)
        self.assertIn('final_collateral', results)
        self.assertIn('active_troves', results)
        
        # The debt should have increased due to interest
        self.assertGreater(results['final_system_debt'], 5 * 4000.0)


if __name__ == '__main__':
    unittest.main()