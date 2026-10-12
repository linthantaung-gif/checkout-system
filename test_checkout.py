import unittest

from checkout import Checkout


class TestCheckout(unittest.TestCase):

    # calculate_summary(): free-shipping boundary
    def test_01_below_free_shipping_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 49.99, 1)
        summary = checkout.calculate_summary()

        self.assertEqual(summary["subtotal"], 49.99)
        self.assertEqual(summary["shipping"], 5.99)
        self.assertEqual(summary["tax"], 4.00)
        self.assertEqual(summary["total"], 59.98)

    def test_02_at_free_shipping_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 50.00, 1)
        summary = checkout.calculate_summary()

        self.assertEqual(summary["subtotal"], 50.00)
        self.assertEqual(summary["shipping"], 0.00)
        self.assertEqual(summary["tax"], 4.00)
        self.assertEqual(summary["total"], 54.00)

    def test_03_above_free_shipping_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 50.01, 1)
        summary = checkout.calculate_summary()

        self.assertEqual(summary["subtotal"], 50.01)
        self.assertEqual(summary["shipping"], 0.00)
        self.assertEqual(summary["tax"], 4.00)
        self.assertEqual(summary["total"], 54.01)

    def test_04_discount_moves_subtotal_below_shipping_threshold(self):
        checkout = Checkout()
        checkout.add_item("Item", 55.00, 1)
        checkout.apply_coupon("SAVE10")
        summary = checkout.calculate_summary()

        self.assertEqual(summary["subtotal"], 55.00)
        self.assertEqual(summary["discount"], 5.50)
        self.assertEqual(summary["discounted_subtotal"], 49.50)
        self.assertEqual(summary["shipping"], 5.99)
        self.assertEqual(summary["tax"], 3.96)
        self.assertEqual(summary["total"], 59.45)

    # add_item()
    def test_05_minimum_positive_price(self):
        checkout = Checkout()
        checkout.add_item("Item", 0.01, 1)
        summary = checkout.calculate_summary()

        self.assertEqual(summary["subtotal"], 0.01)
        self.assertEqual(summary["shipping"], 5.99)
        self.assertEqual(summary["total"], 6.00)

    # apply_coupon()
    def test_06_save10_coupon(self):
        checkout = Checkout()
        checkout.add_item("Item", 100.00, 1)
        checkout.apply_coupon("SAVE10")
        summary = checkout.calculate_summary()

        self.assertEqual(summary["discount"], 10.00)
        self.assertEqual(summary["coupon_applied"], "SAVE10")

    def test_07_save20_coupon(self):
        checkout = Checkout()
        checkout.add_item("Item", 100.00, 1)
        checkout.apply_coupon("SAVE20")
        summary = checkout.calculate_summary()

        self.assertEqual(summary["discount"], 20.00)
        self.assertEqual(summary["coupon_applied"], "SAVE20")

    def test_08_half_coupon(self):
        checkout = Checkout()
        checkout.add_item("Item", 100.00, 1)
        checkout.apply_coupon("HALF")
        summary = checkout.calculate_summary()

        self.assertEqual(summary["discount"], 50.00)
        self.assertEqual(summary["coupon_applied"], "HALF")

    def test_09_coupon_is_case_insensitive(self):
        checkout = Checkout()
        checkout.apply_coupon("save10")

        self.assertEqual(checkout.coupon_code, "SAVE10")
        self.assertEqual(checkout.discount_percent, 0.10)

    def test_10_invalid_coupon(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.apply_coupon("bogustrogus")

    def test_11_empty_coupon(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.apply_coupon("")

    def test_12_non_string_coupon(self):
        checkout = Checkout()

        with self.assertRaises(TypeError):
            checkout.apply_coupon(123)

    # Invalid add_item() inputs: each invalid equivalence class is separate.
    def test_13_zero_price(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item("Item", 0.00, 1)

    def test_14_negative_price(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item("Item", -5.00, 1)

    def test_15_zero_quantity(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item("Item", 10.00, 0)

    def test_16_negative_quantity(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item("Item", 10.00, -2)

    def test_17_non_integer_quantity(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item("Item", 10.00, 1.5)

    def test_18_empty_item_name(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item("", 10.00, 1)

    def test_19_whitespace_item_name(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item("   ", 10.00, 1)

    def test_20_non_string_item_name(self):
        checkout = Checkout()

        with self.assertRaises(ValueError):
            checkout.add_item(None, 10.00, 1)

    # remove_item()
    def test_21_remove_missing_item(self):
        checkout = Checkout()

        with self.assertRaises(KeyError):
            checkout.remove_item("Missing", 1)

    def test_22_remove_zero_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)

        with self.assertRaises(ValueError):
            checkout.remove_item("Book", 0)

    def test_23_remove_negative_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)

        with self.assertRaises(ValueError):
            checkout.remove_item("Book", -1)

    def test_24_remove_partial_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", 1)

        self.assertIn("book", checkout.cart)
        self.assertEqual(checkout.cart["book"]["qty"], 2)

    def test_25_remove_exact_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", 3)

        self.assertNotIn("book", checkout.cart)

    def test_26_remove_more_than_current_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", 4)

        self.assertNotIn("book", checkout.cart)

    def test_27_remove_with_none_removes_entire_item(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book")

        self.assertNotIn("book", checkout.cart)

    def test_28_positive_non_integer_remove_quantity(self):
        """
        Documents the current program behavior for a positive non-integer
        removal quantity. remove_item() does not currently reject this input.
        """
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 3)
        checkout.remove_item("Book", 1.5)

        self.assertEqual(checkout.cart["book"]["qty"], 1.5)

    # clear_coupon()
    def test_29_clear_applied_coupon(self):
        checkout = Checkout()
        checkout.apply_coupon("SAVE20")
        checkout.clear_coupon()

        self.assertIsNone(checkout.coupon_code)
        self.assertEqual(checkout.discount_percent, 0.0)

    def test_30_clear_coupon_when_none_is_applied(self):
        checkout = Checkout()
        checkout.clear_coupon()

        self.assertIsNone(checkout.coupon_code)
        self.assertEqual(checkout.discount_percent, 0.0)

    # Rounding and empty-cart behavior
    def test_31_discount_rounding(self):
        checkout = Checkout()
        checkout.add_item("Item", 33.33, 1)
        checkout.apply_coupon("SAVE10")
        summary = checkout.calculate_summary()

        self.assertEqual(summary["discount"], 3.33)
        self.assertEqual(summary["discounted_subtotal"], 30.00)

    def test_32_tax_rounding(self):
        checkout = Checkout()
        checkout.add_item("Item", 37.47, 1)
        summary = checkout.calculate_summary()

        self.assertEqual(summary["tax"], 3.00)

    def test_33_empty_cart_summary(self):
        checkout = Checkout()
        summary = checkout.calculate_summary()

        self.assertEqual(summary["subtotal"], 0.0)
        self.assertEqual(summary["discount"], 0.0)
        self.assertEqual(summary["discounted_subtotal"], 0.0)
        self.assertEqual(summary["shipping"], 0.0)
        self.assertEqual(summary["tax"], 0.0)
        self.assertEqual(summary["total"], 0.0)

    # Additional specified behavior
    def test_34_duplicate_items_accumulate_quantity(self):
        checkout = Checkout()
        checkout.add_item("Book", 10.00, 1)
        checkout.add_item("Book", 10.00, 2)

        self.assertEqual(checkout.cart["book"]["qty"], 3)

    def test_35_item_name_is_trimmed_and_normalized(self):
        checkout = Checkout()
        checkout.add_item("  Book  ", 10.00, 1)

        self.assertIn("book", checkout.cart)
        self.assertEqual(checkout.cart["book"]["name"], "Book")


if __name__ == "__main__":
    unittest.main()
