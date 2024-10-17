import sys
from app.config import AppConfig
from app.http import HTTP
from app.helper import Helper

class Sylius(object):

    def __init__(self):
        self.config = AppConfig()
        self.token = self.get_token()

    def get_token(self):
        http = HTTP()

        headers = {
            'Content-Type': 'application/ld+json'
        }

        data = {
            "email": self.config.SYLIUS_USER,
            "password": self.config.SYLIUS_PASS
        }

        response = http.post('/api/v2/admin/administrators/token', headers=headers, data=data)

        if(response != False):
            return response['token']
        else:
            print('Błąd podczas pobierania tokena Sylius')
            sys.exit(1)
    
    def get_variants(self):
        http = HTTP()

        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/ld+json'
        }

        response = http.get('/api/v2/admin/product-variants?page=1&itemsPerPage=999999', headers=headers)

        if 'hydra:member' in response:
            return response['hydra:member']
        else:
            print('Błąd podczas pobierania wariantów Sylius')
            sys.exit(1)
    
    def update_variants(self, variant):
        http = HTTP()

        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/ld+json'
        }

        data = {
            'onHand': variant['stock'],
            'subiektCode': variant['code'],
            'subiektType': variant['type'],
        }

        if round(variant['subiekt_product']['cena']) > 0:
            channel_pricings = {}
            for pricing in variant['pricing']:
                channel_pricings[pricing['code']] = {
                    '@id': pricing['id'],
                    '@type': 'ChannelPricing',
                    'price': pricing['price'],
                    'originalPrice': pricing['price']
                }
            data['channelPricings'] = channel_pricings


        response = http.put(variant['id'], headers=headers, data=data)

        return response