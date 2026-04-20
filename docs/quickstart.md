# Quickstart

Tento súbor ukazuje základné použitie knižnice MRHScrypto.

## 1. Import knižnice

```python
import numpy as np
from mrhscrypto import MRHSCrypto
```

## 2. Vytvorenie kryptosystému

```python
scheme = MRHSCrypto(d=1, security=128)
```

Parameter `d` určuje typ riedkosti a solver použitý pri dešifrovaní.

Aktuálne je podporované iba:

```text
d = 1
```

Parameter `security` určuje dĺžku vstupnej správy. Podporované hodnoty sú:

```text
128, 256
```

Z parametra `security` sa automaticky vypočítajú interné parametre kryptosystému, napríklad `n` a `m`.

## 3. Generovanie kľúčov

```python
keypair = scheme.generate_keypair()
```

Objekt `keypair` obsahuje verejný a súkromný kľúč:

```python
public_key = keypair.public_key
private_key = keypair.private_key
```

Verejný kľúč sa používa na šifrovanie.  
Súkromný kľúč sa používa na dešifrovanie.

## 4. Vytvorenie správy

Správa musí byť binárny NumPy vektor dĺžky `security`.

```python
message = np.random.randint(
    0,
    2,
    size=scheme.parameters.security,
    dtype=np.uint8,
)
```

## 5. Šifrovanie

```python
ciphertext = scheme.encrypt(message, public_key)
```

Pri šifrovaní sa k správe interne pripojí hash tag. Používateľ zadáva iba pôvodnú správu.

## 6. Dešifrovanie

```python
recovered_message = scheme.decrypt(ciphertext, private_key)
```

Metóda `decrypt` vracia pôvodnú dešifrovanú správu.

## Kompletný príklad

```python
import numpy as np
from mrhscrypto import MRHSCrypto

scheme = MRHSCrypto(d=1, security=128)

keypair = scheme.generate_keypair()

public_key = keypair.public_key
private_key = keypair.private_key

message = np.random.randint(
    0,
    2,
    size=scheme.parameters.security,
    dtype=np.uint8,
)

ciphertext = scheme.encrypt(message, public_key)
recovered_message = scheme.decrypt(ciphertext, private_key)

print("Pôvodná správa:  ", message)
print("Obnovená správa: ", recovered_message)
print("Úspech:", np.array_equal(message, recovered_message))
```

## Ukladanie kľúčov

Kľúče je možné uložiť pomocou metódy `save`:

```python
public_key.save("public_key.npz")
private_key.save("private_key.npz")
```

## Načítavanie kľúčov

Kľúče sa načítavajú cez objekt `MRHSCrypto`:

```python
public_key = scheme.load_public_key("public_key.npz")
private_key = scheme.load_private_key("private_key.npz")
```

Pri načítavaní sa kontroluje, či parametre uloženého kľúča zodpovedajú aktuálnej inštancii kryptosystému.

## Získanie verejného kľúča zo súkromného kľúča

Ak má používateľ uložený iba súkromný kľúč, verejný kľúč je možné dopočítať:

```python
public_key = private_key.public_key()
```