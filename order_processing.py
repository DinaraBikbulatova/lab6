# Константы для магических чисел
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
MIN_TOTAL_AFTER_DISCOUNT = 0

# Константы для скидок
DISCOUNT_RATES = {
    "SAVE10": 0.10,
    "SAVE20": 0.20,
    "SAVE20_MIN": 0.05,  # Минимальная скидка для SAVE20
}
DISCOUNT_THRESHOLDS = {
    "SAVE20": 200,
    "VIP": 100,
}
FIXED_DISCOUNTS = {
    "VIP": 50,
    "VIP_MIN": 10,
}


def parse_request(request: dict):
    """Извлекает данные из запроса."""
    return (
        request.get("user_id"),
        request.get("items"),
        request.get("coupon"),
        request.get("currency"),
    )


def validate_order_data(user_id, items, currency):
    """Валидирует основные данные заказа."""
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if currency is None:
        return DEFAULT_CURRENCY
    return currency


def validate_items(items):
    """Валидирует список товаров."""
    if not isinstance(items, list):
        raise ValueError("items must be a list")

    if len(items) == 0:
        raise ValueError("items must not be empty")

    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")


def calculate_subtotal(items):
    """Вычисляет общую стоимость товаров."""
    return sum(item["price"] * item["qty"] for item in items)


def calculate_discount(subtotal, coupon):
    """Вычисляет размер скидки на основе купона."""
    if not coupon:
        return 0

    if coupon == "SAVE10":
        return int(subtotal * DISCOUNT_RATES["SAVE10"])

    elif coupon == "SAVE20":
        if subtotal >= DISCOUNT_THRESHOLDS["SAVE20"]:
            return int(subtotal * DISCOUNT_RATES["SAVE20"])
        else:
            return int(subtotal * DISCOUNT_RATES["SAVE20_MIN"])

    elif coupon == "VIP":
        if subtotal >= DISCOUNT_THRESHOLDS["VIP"]:
            return FIXED_DISCOUNTS["VIP"]
        else:
            return FIXED_DISCOUNTS["VIP_MIN"]

    else:
        raise ValueError("unknown coupon")


def apply_discount(subtotal, discount):
    """Применяет скидку и проверяет минимальную сумму."""
    total_after_discount = subtotal - discount
    return max(total_after_discount, MIN_TOTAL_AFTER_DISCOUNT)


def calculate_tax(amount):
    """Вычисляет налог на сумму."""
    return int(amount * TAX_RATE)


def generate_order_id(user_id, items_count):
    """Генерирует ID заказа."""
    return f"{user_id}-{items_count}-X"


def build_order_response(user_id, items, currency, subtotal, discount, tax, total):
    """Собирает итоговый ответ."""
    return {
        "order_id": generate_order_id(user_id, len(items)),
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }


def process_checkout(request: dict) -> dict:
    """Обрабатывает заказ покупателя."""
    # Шаг 1: Парсинг запроса
    user_id, items, coupon, currency = parse_request(request)

    # Шаг 2: Валидация
    currency = validate_order_data(user_id, items, currency)
    validate_items(items)

    # Шаг 3: Подсчёт суммы
    subtotal = calculate_subtotal(items)

    # Шаг 4: Расчёт скидки
    discount = calculate_discount(subtotal, coupon)

    # Шаг 5: Применение скидки
    total_after_discount = apply_discount(subtotal, discount)

    # Шаг 6: Расчёт налога
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    # Шаг 7: Формирование ответа
    return build_order_response(
        user_id=user_id,
        items=items,
        currency=currency,
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total
    )