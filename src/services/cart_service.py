class CartService:
    _instance = None
    _cart = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CartService, cls).__new__(cls)
        return cls._instance
    
    def add_item(self, product_id, product_name, price, store_id, store_name, quantity=1):
        if product_id not in self._cart:
            self._cart[product_id] = {
                'product_id': product_id,
                'product_name': product_name,
                'price': price,
                'store_id': store_id,
                'store_name': store_name,
                'quantity': 0
            }
        self._cart[product_id]['quantity'] += quantity
    
    def remove_item(self, product_id):
        if product_id in self._cart:
            del self._cart[product_id]
    
    def update_quantity(self, product_id, quantity):
        if product_id in self._cart:
            if quantity <= 0:
                self.remove_item(product_id)
            else:
                self._cart[product_id]['quantity'] = quantity
    
    def get_cart(self):
        return self._cart.copy()
    
    def get_total(self):
        total = 0.0
        for item in self._cart.values():
            total += item['price'] * item['quantity']
        return total
    
    def get_items_count(self):
        count = 0
        for item in self._cart.values():
            count += item['quantity']
        return count
    
    def clear(self):
        self._cart = {}
    
    def get_stores_in_cart(self):
        stores = {}
        for item in self._cart.values():
            store_id = item['store_id']
            if store_id not in stores:
                stores[store_id] = {
                    'store_id': store_id,
                    'store_name': item['store_name'],
                    'items': []
                }
            stores[store_id]['items'].append(item)
        return stores


