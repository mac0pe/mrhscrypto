# MRHScrypto

MRHScrypto je experimentálna Python knižnica implementujúca kryptosystém založený na MRHS rovniciach.

Projekt je momentálne vo vývoji. Aktuálne je implementovaný hlavne one-sparse prípad, teda parameter `d = 1`.

> **Upozornenie**
>
> Táto knižnica je experimentálna a nie je určená na reálne kryptografické použitie.

## Funkcionalita

- generovanie kľúčov,
- šifrovanie binárnych správ,
- dešifrovanie,
- podpora one-sparse prípadu pre `d = 1`,
- ukladanie a načítavanie verejných a súkromných kľúčov.

## Inštalácia

### Lokálna inštalácia

```bash
git clone https://github.com/mac0pe/mrhscrypto.git
cd mrhscrypto
pip install -e .
```

### Inštalácia z GitHubu

```bash
pip install "mrhscrypto @ git+https://github.com/mac0pe/mrhscrypto.git@main"
```

## Základné použitie

```python
import numpy as np
from mrhscrypto import MRHSCrypto

scheme = MRHSCrypto(d=1, security=128)

keypair = scheme.generate_keypair()

message = np.random.randint(
    0,
    2,
    size=scheme.parameters.security,
    dtype=np.uint8,
)

ciphertext = scheme.encrypt(message, keypair.public_key)
decrypted_message = scheme.decrypt(ciphertext, keypair.private_key)

print("Úspech:", np.array_equal(message, decrypted_message))
```

## Ukladanie a načítavanie kľúčov

```python
keypair.public_key.save("public_key.npz")
keypair.private_key.save("private_key.npz")

public_key = scheme.load_public_key("public_key.npz")
private_key = scheme.load_private_key("private_key.npz")
```

Ak má používateľ uložený iba súkromný kľúč, verejný kľúč je možné dopočítať:

```python
public_key = private_key.public_key()
```

## Stav projektu

Aktuálne je implementované:

- generovanie kľúčov,
- šifrovanie,
- dešifrovanie,
- one-sparse riešič,
- serializácia kľúčov.

## Dokumentácia

Podrobnejší popis API sa nachádza v priečinku:

```text
docs/
```

## Licencia

Projekt je licencovaný pod licenciou MIT.