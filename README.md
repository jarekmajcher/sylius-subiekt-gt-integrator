# Sylius Subiekt GT integrator
Skrypt odpowiada za synchronizację cen i stanów magazynowych pomiędzy Subiektem GT a sklepem internetowym opartym na Syliusie.

## Konfiguracja Subiektem GT

### 1. Przykładowy config
Pliki z configami zapisywane są jako pliki json. Zapisz plik jako default_config.json
```
{
    "mssql": {
        "server": "192.168.1.100\\SQL",
        "db": "Default",
        "user": "sa",
        "pass": "example"
    },
    "subiekt": {
        "price": "CenaBrutto1",
        "warehouse": "1"
    },
    "sylius": {
        "url": "https://127.0.0.1:8000",
        "user": "api.integracja@sylius.com",
        "pass": "example"
    },
    "app": {
        "log": true,
        "log_path": "C:\TMP\log\default\",
        "full_integration": true
    }
}
```

### 2. Uruchomienie skryptu

Windows PowerShell
```bash
py -B main.py default
```

Macos
```bash
python -B main.py default
```

### 3. Skąd pobrać ID produktu w Subiekt GT?
Integrator łączy produkty z Sylius oraz Subiekt GT na podstawie ID produktu w bazie Subiekt GT. To nie jest to samo pole co Symbol. Aby pobrać ID produktów można skorzystać z tego zapytania SQL. Zapytanie można dodać w Subiekt GT w sekkcji Zestawienia.

```sql
SELECT
    T.tw_Id AS [Kod do integracji (ID)],
    T.tw_Symbol AS [Symbol Subiekt],
    T.tw_Nazwa AS Nazwa
FROM tw__Towar T
WHERE T.tw_Zablokowany = 0
```
W Sylius wymagane jest uzupełnienie tylko pola ID. Integrator sam nadpisze wartości Symbol oraz Typ.

## Konfiguracja Sylius

Integrator działa poprawnie z Sylius w wersji 1.13. Nie testowano na innych wersjach. Do poprawnego działania integratora musisz wykonać kilka czynności opisanych poniżej.

### 1. Nadać administratorowi prawa dostępu do API
Zalecane jest utworzenie nowego użytkownika. Następnie można nadać mu uprawnienia za pomocą polecenia:
```bash
 bin/console sylius:user:promote change-me@sylius.com ROLE_API_ACCESS --user-type=admin 
```

### 2. Rozszerzyć encję ProductVariant o dodatkowe pola.

```PHP
# src/Entity/Product/ProductVariant.php

<?php

declare(strict_types=1);

namespace App\Entity\Product;

use Doctrine\ORM\Mapping as ORM;
use Sylius\Component\Core\Model\ProductVariant as BaseProductVariant;

/**
 * @ORM\Entity
 * @ORM\Table(name="sylius_product_variant")
 */
class ProductVariant extends BaseProductVariant
{
    /** @ORM\Column(type="string", nullable=true) */
    private $subiektId;

    /** @ORM\Column(type="string", nullable=true) */
    private $subiektCode;

    /** @ORM\Column(type="string", nullable=true) */
    private $subiektType;
    
    // Getters and setters
}
```

### 3. Dodać obsługę pól w serializerze

```XML
# config/serialization/ProductVariant.xml

<?xml version="1.0" ?>

<serializer xmlns="http://symfony.com/schema/dic/serializer-mapping"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://symfony.com/schema/dic/serializer-mapping https://symfony.com/schema/dic/serializer-mapping/serializer-mapping-1.0.xsd"
>
    <class name="Sylius\Component\Core\Model\ProductVariant">
        <attribute name="id">
            <group>admin:product_variant:read</group>
            <group>admin:product_variant:update</group>
        </attribute>
        <attribute name="onHand">
            <group>admin:product_variant:read</group>
            <group>admin:product_variant:update</group>
        </attribute>
        <attribute name="onHold">
            <group>admin:product_variant:read</group>
            <group>admin:product_variant:update</group>
        </attribute>
        <attribute name="subiektId">
            <group>admin:product_variant:read</group>
            <group>admin:product_variant:update</group>
        </attribute>
        <attribute name="subiektCode">
            <group>admin:product_variant:read</group>
            <group>admin:product_variant:update</group>
        </attribute>
        <attribute name="subiektType">
            <group>admin:product_variant:read</group>
            <group>admin:product_variant:update</group>
        </attribute>
    </class>
</serializer>
```

### 4. Dodać pola do formularzy

Rozszerzyć formularz wariantu produktu.

```php
# src/Form/Extension/ProductTypeExtension.php

<?php

declare(strict_types=1);

namespace App\Form\Extension;

use Sylius\Bundle\ProductBundle\Form\Type\ProductVariantType;
use Symfony\Component\Form\AbstractTypeExtension;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;

final class ProductVariantTypeExtension extends AbstractTypeExtension
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('subiektId', TextType::class, [
                'required' => false,
                'label' => 'app.ui.subiekt_id',
            ])
            ->add('subiektCode', TextType::class, [
                'required' => false,
                'label' => 'app.ui.subiekt_code',
            ])
        ;
    }

    public static function getExtendedTypes(): array
    {
        return [ProductVariantType::class];
    }
}
```

### 5. Dodać pola do widoku formularzy

Formularz edycji produktu:
```twig
# templates/bundles/SyliusAdminBundle/Product/Tab/_details.html.twig

...

{% if product.simple %}
    {{ form_row(form.variant.subiektId) }}
    {{ form_row(form.variant.subiektCode, {'attr' : {'readonly': true }}) }}
{% endif %}

...
```

Formularz edycji wariantu:
```twig
# templates/bundles/SyliusAdminBundle/ProductVariant/Tab/_details.html.twig

...

{{ form_row(form.subiektId) }}
{{ form_row(form.subiektCode, {'attr' : {'readonly': true }}) }}

...
```
