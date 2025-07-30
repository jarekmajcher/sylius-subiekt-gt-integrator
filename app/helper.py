from datetime import datetime

class Helper:

    @staticmethod
    def create_dict_by_key(array, key, prefix=False, suffix=False):
        result_dict = {}

        for sub_dict in array:
            dict_key = str(sub_dict[key])
            if prefix:
                dict_key = str(prefix) + dict_key
            if suffix:
                dict_key = dict_key + str(suffix)

            result_dict[dict_key] = sub_dict

        return result_dict

    @staticmethod
    def combine_data(subiekt_products, sylius_variants, full_integration):
        combined = []

        for sylius_variant in sylius_variants:

            # Sylius vars
            sylius_id = sylius_variant['@id']
            sylius_code = sylius_variant['code']
            sylius_stock = sylius_variant['onHand']
            sylius_stock_hold = sylius_variant['onHold']
            sylius_subiekt_id = sylius_variant['subiektId']
            sylius_subiekt_code = sylius_variant['subiektCode']
            sylius_subiekt_type = sylius_variant['subiektType']
            sylius_pricings = sylius_variant['channelPricings']

            key = "id_" + str(sylius_subiekt_id)
            subiekt_product = subiekt_products.get(key)

            if subiekt_product is not None:

                # Subiekt vars
                subiekt_price = round(subiekt_product['cena'] * 100)
                subiekt_code = str(subiekt_product['symbol'])
                subiekt_type = str(subiekt_product['rodzaj'])

                subiekt_stock = round(subiekt_product['dostepne'])
                if(subiekt_stock < sylius_stock_hold):
                    subiekt_stock = sylius_stock_hold

                # Is same vars
                is_same_price = True
                for sylius_pricing_k, sylius_pricing_v in sylius_pricings.items():
                    if (sylius_pricing_v['price'] != subiekt_price and not sylius_pricing_v['appliedPromotions']) or sylius_pricing_v['originalPrice'] != subiekt_price:
                        is_same_price = False

                is_same_stock = subiekt_stock == sylius_stock
                is_same_code = subiekt_code == sylius_subiekt_code
                is_same_type = subiekt_type == sylius_subiekt_type

                # Create combined array
                if full_integration or not is_same_price or not is_same_stock or not is_same_code or not is_same_type:
                    pricing = []
                    for sylius_pricing_k, sylius_pricing_v in sylius_pricings.items():
                        pricing.append({
                            'id': sylius_pricing_v['@id'],
                            'code': sylius_pricing_k,
                            'price': subiekt_price
                        })

                    combined.append({
                        'id': sylius_id,
                        'code': str(subiekt_code),
                        'type': str(subiekt_type),
                        'stock': subiekt_stock,
                        'price': subiekt_price,
                        'pricing': pricing,
                        'sylius_variant': sylius_variant,
                        'subiekt_product': subiekt_product
                    })

        return combined
    
    @staticmethod
    def add_timestamp(text):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

        return f"{timestamp} {text}"