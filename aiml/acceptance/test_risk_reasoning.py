import unittest
from hyperon import MeTTa

class TestMettaKnowledgeBase(unittest.TestCase):
    def setUp(self):
        """Set up the MeTTa interpreter and load the knowledge base."""
        self.metta = MeTTa()
        try:
            self.metta.run("!(import! &self std)")
            with open("metta/rules/risk_rules.metta", "r") as f:
                self.metta.run(f.read())
        except FileNotFoundError:
            self.metta.run("!(import! &self std)")
            with open("aiml/metta/rules/risk_rules.metta", "r") as f:
                self.metta.run(f.read())

    def test_knowledge_base_facts(self):
        """Tests that MeTTa correctly retrieves facts and handles non-matches."""

        # Test 1: Querying for a volatile asset (SHIB) should return the (VolHigh) fact.
        assertion_shib = "!(volatility-of SHIB)"
        result_shib = self.metta.run(assertion_shib)
        self.assertTrue(result_shib and result_shib[0])
        self.assertEqual(str(result_shib[0][0]), "(VolHigh)")

        # Test 2: Querying for a non-volatile asset (BTC) should return the input expression.
        assertion_btc = "!(volatility-of BTC)"
        result_btc = self.metta.run(assertion_btc)
        
        # THE FIX: This is the correct way to test for a non-match.
        self.assertTrue(result_btc and result_btc[0])
        # We assert that the result is the input, just without the execution wrapper `!(...)`
        self.assertEqual(str(result_btc[0][0]), "(volatility-of BTC)")


if __name__ == "__main__":
    unittest.main()
