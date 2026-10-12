class Checkout:
    FREE_SHIPPING_THRESHOLD = 50.00
    SHIPPING_FEE = 5.99
    TAX_RATE = 0.08

    VALID_COUPONS = {
        "SAVE10": 0.10,
        "SAVE20": 0.20,
        "HALF": 0.50,
    }

    def __init__(self):
        self.cart = {}
        self.coupon_code = None
        self.discount_percent = 0.0

    def add_item(self, item: str, price: float, qty: int = 1):
        if not isinstance(item, str) or not item.strip():
            raise ValueError("Item name must be a non-empty string")
        if price <= 0:
            raise ValueError("Price must be greater than zero")
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer")

        key = item.strip().lower()
        if key in self.cart:
            self.cart[key]["qty"] += qty
        else:
            self.cart[key] = {"name": item.strip(), "price": float(price), "qty": qty}

    def remove_item(self, item: str, qty: int = None):
        key = item.strip().lower()
        if key not in self.cart:
            raise KeyError(f"Item '{item}' not found in cart")

        if qty is None or qty >= self.cart[key]["qty"]:
            del self.cart[key]
        elif qty <= 0:
            raise ValueError("Removal quantity must be a positive integer")
        else:
            self.cart[key]["qty"] -= qty

    def apply_coupon(self, code: str):
        if not isinstance(code, str):
            raise TypeError("Coupon code must be a string")

        normalized = code.strip().upper()
        if normalized not in self.VALID_COUPONS:
            raise ValueError(f"Invalid coupon code: '{code}'")

        self.coupon_code = normalized
        self.discount_percent = self.VALID_COUPONS[normalized]

    def clear_coupon(self):
        self.coupon_code = None
        self.discount_percent = 0.0

    def calculate_summary(self) -> dict:
        subtotal = round(sum(d["price"] * d["qty"] for d in self.cart.values()), 2)

        if subtotal == 0.0:
            return {
                "subtotal": 0.0,
                "discount": 0.0,
                "discounted_subtotal": 0.0,
                "shipping": 0.0,
                "tax": 0.0,
                "total": 0.0,
                "coupon_applied": self.coupon_code,
            }

        discount = round(subtotal * self.discount_percent, 2)
        discounted_subtotal = round(max(0.0, subtotal - discount), 2)
        shipping = 0.0 if discounted_subtotal >= self.FREE_SHIPPING_THRESHOLD else self.SHIPPING_FEE
        tax = round(discounted_subtotal * self.TAX_RATE, 2)
        total = round(discounted_subtotal + shipping + tax, 2)

        return {
            "subtotal": subtotal,
            "discount": discount,
            "discounted_subtotal": discounted_subtotal,
            "shipping": shipping,
            "tax": tax,
            "total": total,
            "coupon_applied": self.coupon_code,
        }


def main():
    checkout = Checkout()
    print("=== Checkout System ===")
    print("Enter your items below. Type 'done' as the item name when finished.\n")

    while True:
        item_name = input("Item name (or 'done'): ").strip()
        if item_name.lower() == "done":
            break
        if not item_name:
            print("Item name cannot be empty. Try again.")
            continue

        try:
            price = float(input(f"Price for '{item_name}': $"))
            qty = int(input(f"Quantity for '{item_name}': "))
            checkout.add_item(item_name, price, qty)
            print(f"Added {qty}x {item_name} to cart.\n")
        except ValueError as err:
            print(f"Error: {err}. Please re-enter this item.\n")

    if not checkout.cart:
        print("\nCart is empty. Exiting.")
        return

    coupon_input = input("\nEnter coupon code (press Enter to skip): ").strip()
    if coupon_input:
        try:
            checkout.apply_coupon(coupon_input)
            print(f"Coupon '{coupon_input.upper()}' applied successfully!")
        except ValueError as err:
            print(f"Notice: {err}. Proceeding without discount.")

    summary = checkout.calculate_summary()

    print("\n" + "=" * 32)
    print("         ORDER RECEIPT          ")
    print("=" * 32)
    for item in checkout.cart.values():
        line_cost = item["price"] * item["qty"]
        print(f"{item['name']:<16} x{item['qty']:<3} ${line_cost:>7.2f}")

    print("-" * 32)
    print(f"{'Subtotal:':<22} ${summary['subtotal']:>7.2f}")
    if summary["discount"] > 0:
        print(f"{'Discount (' + summary['coupon_applied'] + '):':<22} -${summary['discount']:>6.2f}")
        print(f"{'Discounted Subtotal:':<22} ${summary['discounted_subtotal']:>7.2f}")
    print(f"{'Shipping:':<22} ${summary['shipping']:>7.2f}")
    print(f"{'Tax (8%):':<22} ${summary['tax']:>7.2f}")
    print("=" * 32)
    print(f"{'Total:':<22} ${summary['total']:>7.2f}")
    print("=" * 32)


if __name__ == "__main__":
    main()