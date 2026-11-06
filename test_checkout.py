import unittest

from checkout import Checkout


class TestCheckoutProject1And2(unittest.TestCase):
    # Project 1: TC-01 through TC-33

    def test_tc_01_shipping_below_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 49.99, 1)
        summary = checkout.calculate_summary()
        self.assertEqual(summary["shipping"], 5.99)
        self.assertEqual(summary["tax"], 4.00)
        self.assertEqual(summary["total"], 59.98)

    def test_tc_02_shipping_at_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 50.00, 1)
        summary = checkout.calculate_summary()
        self.assertEqual(summary["shipping"], 0.00)
        self.assertEqual(summary["tax"], 4.00)
        self.assertEqual(summary["total"], 54.00)

    def test_tc_03_shipping_above_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 50.01, 1)
        summary = checkout.calculate_summary()
        self.assertEqual(summary["shipping"], 0.00)
        self.assertEqual(summary["total"], 54.01)

    def test_tc_04_coupon_drops_below_shipping_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 55.00, 1)
        checkout.apply_coupon("SAVE10")
        summary = checkout.calculate_summary()
        self.assertEqual(summary["discounted_subtotal"], 49.50)
        self.assertEqual(summary["shipping"], 5.99)

    def test_tc_05_valid_minimum_price_item(self):
        checkout = Checkout()
        checkout.add_item("Book", 0.01, 1)
        summary = checkout.calculate_summary()
        self.assertIn("book", checkout.cart)
        self.assertEqual(summary["total"], 6.00)

    def test_tc_06_apply_save10(self):
        checkout = Checkout()
        checkout.apply_coupon("SAVE10")
        self.assertEqual(checkout.coupon_code, "SAVE10")
        self.assertEqual(checkout.discount_percent, 0.10)

    def test_tc_07_apply_save20(self):
        checkout = Checkout()
        checkout.apply_coupon("SAVE20")
        self.assertEqual(checkout.coupon_code, "SAVE20")
        self.assertEqual(checkout.discount_percent, 0.20)

    def test_tc_08_apply_half(self):
        checkout = Checkout()
        checkout.apply_coupon("HALF")
        self.assertEqual(checkout.coupon_code, "HALF")
        self.assertEqual(checkout.discount_percent, 0.50)

    def test_tc_09_coupon_normalization(self):
        checkout = Checkout()
        checkout.apply_coupon("save10")
        self.assertEqual(checkout.coupon_code, "SAVE10")
        self.assertEqual(checkout.discount_percent, 0.10)

    def test_tc_10_invalid_coupon_string(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.apply_coupon("bogustrogus")

    def test_tc_11_empty_coupon_string(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.apply_coupon("")

    def test_tc_12_non_string_coupon(self):
        checkout = Checkout()
        with self.assertRaises(TypeError):
            checkout.apply_coupon(123)

    def test_tc_13_zero_price(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item("Item", 0.00, 1)

    def test_tc_14_negative_price(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item("Item", -5.00, 1)

    def test_tc_15_zero_quantity(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item("Item", 10.00, 0)

    def test_tc_16_negative_quantity(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item("Item", 10.00, -2)

    def test_tc_17_non_integer_quantity(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item("Item", 10.00, 1.5)

    def test_tc_18_empty_item_name(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item("", 10.00, 1)

    def test_tc_19_whitespace_only_item_name(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item(" ", 10.00, 1)

    def test_tc_20_non_string_item_name(self):
        checkout = Checkout()
        with self.assertRaises(ValueError):
            checkout.add_item(123, 10.00, 1)

    def test_tc_21_remove_absent_item(self):
        checkout = Checkout()
        with self.assertRaises(KeyError):
            checkout.remove_item("Laptop")

    def test_tc_22_remove_zero_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        with self.assertRaises(ValueError):
            checkout.remove_item("Book", 0)
        self.assertEqual(checkout.cart["book"]["qty"], 3)

    def test_tc_23_remove_partial_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", 1)
        self.assertEqual(checkout.cart["book"]["qty"], 2)

    def test_tc_24_remove_stored_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", 3)
        self.assertNotIn("book", checkout.cart)

    def test_tc_25_remove_more_than_stored_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", 4)
        self.assertNotIn("book", checkout.cart)

    def test_tc_26_remove_none_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", None)
        self.assertNotIn("book", checkout.cart)

    def test_tc_27_clear_active_coupon(self):
        checkout = Checkout()
        checkout.apply_coupon("SAVE20")
        checkout.clear_coupon()
        self.assertIsNone(checkout.coupon_code)
        self.assertEqual(checkout.discount_percent, 0.0)

    def test_tc_28_clear_without_active_coupon(self):
        checkout = Checkout()
        checkout.clear_coupon()
        self.assertIsNone(checkout.coupon_code)
        self.assertEqual(checkout.discount_percent, 0.0)

    def test_tc_29_discount_rounding(self):
        checkout = Checkout()
        checkout.add_item("Item", 33.33, 1)
        checkout.apply_coupon("SAVE10")
        summary = checkout.calculate_summary()
        self.assertEqual(summary["discount"], 3.33)

    def test_tc_30_tax_rounding(self):
        checkout = Checkout()
        checkout.add_item("Item", 37.47, 1)
        summary = checkout.calculate_summary()
        self.assertEqual(summary["tax"], 3.00)

    def test_tc_31_empty_cart_summary(self):
        checkout = Checkout()
        summary = checkout.calculate_summary()
        self.assertEqual(summary["subtotal"], 0.0)
        self.assertEqual(summary["discount"], 0.0)
        self.assertEqual(summary["discounted_subtotal"], 0.0)
        self.assertEqual(summary["shipping"], 0.0)
        self.assertEqual(summary["tax"], 0.0)
        self.assertEqual(summary["total"], 0.0)
        self.assertIsNone(summary["coupon_applied"])

    def test_tc_32_duplicate_item_quantity_combines(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 1)
        checkout.add_item("book", 10.00, 2)
        self.assertEqual(len(checkout.cart), 1)
        self.assertEqual(checkout.cart["book"]["qty"], 3)

    def test_tc_33_trimmed_item_name(self):
        checkout = Checkout()
        checkout.add_item(" Book ", 10.00, 1)
        self.assertIn("book", checkout.cart)
        self.assertEqual(checkout.cart["book"]["name"], "Book")

    # Project 2: new test case introduced for loop coverage.
    def test_p2_tc01_multiple_cart_entries(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 1)
        checkout.add_item("Pen", 5.00, 2)
        summary = checkout.calculate_summary()
        self.assertEqual(summary["subtotal"], 20.00)
        self.assertEqual(summary["shipping"], 5.99)
        self.assertEqual(summary["tax"], 1.60)
        self.assertEqual(summary["total"], 27.59)


if __name__ == "__main__":
    unittest.main()
