"""
Unit tests for the TroveManager module of the Bold protocol.

This module contains tests translated from the Solidity TroveManager.t.sol tests.
"""

import unittest
import sys
import os
import time
from enum import Enum

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from vault_model import BoldProtocol, Trove, InterestBatch, MIN_DEBT, DECIMAL_PRECISION, MCR_WETH, CCR_WETH


class TestVaultModel(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        # Initialize Bold protocol with initial ETH price of $2000
        self.protocol = BoldProtocol(initial_eth_price=2000.0)
        
        # Define constants for testing
        self._100pct = 1.0  # 100% for comparisons
        
        # Users for testing
        self.user_a = "UserA"
        self.user_b = "UserB"
        self.user_c = "UserC"
        self.user_d = "UserD"
    
    def test_liquidate_trove_eligibility(self):
        """Test that a trove must be undercollateralized to be liquidated."""
        # Create a fresh protocol instance
        protocol = BoldProtocol(initial_eth_price=2000.0)
        
        # Create a trove with good collateralization
        a_trove_id = protocol.open_trove(self.user_a, 100.0, 100_000.0, 0.01)
        
        # Try to liquidate a well-collateralized trove - should raise an exception
        with self.assertRaises(ValueError) as context:
            protocol.liquidate_trove(a_trove_id)
        
        # Check error message - should mention "not eligible" or similar
        self.assertIn("not eligible", str(context.exception).lower())
    
    def test_icr_calculation(self):
        """Test the individual collateralization ratio calculation."""
        # Create a fresh protocol instance
        protocol = BoldProtocol(initial_eth_price=2000.0)
        
        # Open a trove
        a_trove_id = protocol.open_trove(self.user_a, 10.0, 10000.0, 0.01)
        
        # Calculate expected ICR: (collateral * price) / debt
        expected_icr = (10.0 * 2000.0) / 10000.0
        
        # Get the actual ICR from the trove
        actual_icr = protocol.troves[a_trove_id].icr(protocol.eth_price)
        
        # Verify ICR calculation
        self.assertAlmostEqual(actual_icr, expected_icr, delta=0.001, msg="ICR calculation incorrect")
        
        # Update price and verify ICR changes
        new_price = 1000.0
        expected_icr_new = (10.0 * 1000.0) / 10000.0
        
        # Check new ICR
        actual_icr_new = protocol.troves[a_trove_id].icr(new_price)
        
        # Verify ICR calculation with new price
        self.assertAlmostEqual(actual_icr_new, expected_icr_new, delta=0.001, msg="ICR calculation with new price incorrect")
    
    def test_auto_liquidation(self):
        """Test that troves are automatically liquidated when price drops."""
        # Create a fresh protocol instance
        protocol = BoldProtocol(initial_eth_price=2000.0)
        
        # Create multiple troves
        a_trove_id = protocol.open_trove(self.user_a, 2.0, 3500.0, 0.01)  # Will be liquidatable at price 1000
        b_trove_id = protocol.open_trove(self.user_b, 5.0, 7000.0, 0.02)  # Also liquidatable at price 1000
        c_trove_id = protocol.open_trove(self.user_c, 10.0, 2000.0, 0.03)  # Safe even at price 1000
        
        # Count total troves
        initial_trove_count = len(protocol.troves)
        self.assertEqual(initial_trove_count, 3, "Should have 3 troves initially")
        
        # Calculate initial ICRs
        a_icr_initial = protocol.troves[a_trove_id].icr(protocol.eth_price)
        b_icr_initial = protocol.troves[b_trove_id].icr(protocol.eth_price)
        c_icr_initial = protocol.troves[c_trove_id].icr(protocol.eth_price)
        
        # All troves should be above MCR initially
        self.assertGreaterEqual(a_icr_initial, MCR_WETH, "Trove A should be above MCR initially")
        self.assertGreaterEqual(b_icr_initial, MCR_WETH, "Trove B should be above MCR initially")
        self.assertGreaterEqual(c_icr_initial, MCR_WETH, "Trove C should be above MCR initially")
        
        # Drop price to make some troves undercollateralized
        drop_price = 1000.0
        protocol.update_eth_price(drop_price)
        
        # update_eth_price should have auto-liquidated troves A and B
        self.assertNotIn(a_trove_id, protocol.troves, "Trove A should have been auto-liquidated")
        self.assertNotIn(b_trove_id, protocol.troves, "Trove B should have been auto-liquidated")
        
        # Trove C should still exist and be well-collateralized
        self.assertIn(c_trove_id, protocol.troves, "Trove C should still exist")
        c_icr_after = protocol.troves[c_trove_id].icr(drop_price)
        self.assertGreaterEqual(c_icr_after, MCR_WETH, "Trove C should remain above MCR after price drop")
        
        # Try to liquidate Trove C, which should fail as it's well-collateralized
        with self.assertRaises(ValueError) as context:
            protocol.liquidate_trove(c_trove_id)
        
        # Check error message mentions not eligible for liquidation
        self.assertIn("not eligible", str(context.exception).lower())


    def test_trove_collateralization_requirements(self):
        """Test trove collateralization requirements when opening a trove."""
        # Create a fresh protocol instance
        protocol = BoldProtocol(initial_eth_price=2000.0)
        
        # Try to open trove with insufficient collateral
        with self.assertRaises(ValueError) as context:
            # This should fail because it's below minimum collateralization ratio
            protocol.open_trove(self.user_a, 1.0, 3000.0, 0.01)
        
        # Check error message mentions "insufficient collateral"
        self.assertIn("insufficient collateral", str(context.exception).lower())
        
        # Try to open trove with debt below minimum
        with self.assertRaises(ValueError) as context:
            # This should fail because debt is below minimum
            protocol.open_trove(self.user_a, 10.0, 10.0, 0.01)
        
        # Check error message mentions "debt must be at least"
        self.assertIn("debt must be at least", str(context.exception).lower())
        
        # Open a valid trove
        try:
            trove_id = protocol.open_trove(self.user_a, 10.0, 10000.0, 0.01)
            self.assertIn(trove_id, protocol.troves, "Trove should be created successfully")
        except ValueError as e:
            self.fail(f"Failed to open a valid trove: {e}")


    def test_batch_management(self):
        """Test batch creation and trove joining a batch."""
        # Create a fresh protocol instance
        protocol = BoldProtocol(initial_eth_price=2000.0)
        
        # Create a batch
        batch_manager = "BatchManager1"
        protocol.create_batch(batch_manager, 0.07, 0.02)  # 7% interest, 2% management fee
        
        # Verify batch exists
        self.assertIn(batch_manager, protocol.batches, "Batch should be created")
        self.assertEqual(protocol.batches[batch_manager].interest_rate, 0.07, "Batch interest rate should be set")
        self.assertEqual(protocol.batches[batch_manager].management_fee, 0.02, "Batch management fee should be set")
        
        # Create troves
        a_trove_id = protocol.open_trove(self.user_a, 10.0, 10000.0, 0.01)
        b_trove_id = protocol.open_trove(self.user_b, 10.0, 10000.0, 0.01)
        
        # Join batch
        protocol.join_batch(a_trove_id, batch_manager)
        
        # Verify trove joined batch
        self.assertEqual(protocol.troves[a_trove_id].batch_manager, batch_manager, 
                         "Trove should join the batch")
        
        # Verify batch data updated
        self.assertIn(a_trove_id, protocol.batches[batch_manager].troves, 
                      "Trove should be in batch's trove list")


if __name__ == "__main__":
    unittest.main()