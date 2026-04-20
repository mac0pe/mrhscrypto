# Quickstart

Tento súbor ukazuje základné použitie knižnice MRHScrypto.

## Import knižnice

```python
import numpy as np
from mrhscrypto import MRHSCrypto
```

## Vytvorenie inštancie kryptosystému

```python
scheme = MRHSCrypto(d=1, security=128)
```

Parameter `d` určuje typ riedkosti a podľa neho sa vyberá solver použitý pri dešifrovaní.
Aktuálne je podporovaná iba hodnota d = 1


Parameter `security` určuje dĺžku správy. Zároveň sa z neho odvádzajú interné parametre kryptosystému, napríklad `n` (dĺžka plaintextu) a `m`.

## Generovanie kľúčov

```python
keypair = scheme.generate_keypair()
```

Výsledkom je objekt `KeyPair`, ktorý obsahuje:

```python
keypair.public_key
keypair.private_key
```

Verejný kľúč sa používa na šifrovanie.  
Súkromný kľúč sa používa na dešifrovanie.

## Vytvorenie binárnej správy

```python
message = np.random.randint(
    0,
    2,
    size=scheme.parameters.security,
    dtype=np.uint8,
)
```

Správa musí byť binárny NumPy vektor dĺžky:

```python
scheme.parameters.security
```

## Šifrovanie

```python
ciphertext = scheme.encrypt(message, keypair.public_key)
```

Pri šifrovaní sa k správe najskôr pripojí hash tag. Následne sa výsledný plaintext zašifruje pomocou verejného kľúča.

## Dešifrovanie

```python
message = scheme.decrypt(ciphertext, keypair.private_key)
```

## Kompletný príklad

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
recovered_message = scheme.decrypt(ciphertext, keypair.private_key)


print("Pôvodná správa:  ", message)
print("Obnovená správa: ", recovered_message)
print("Úspech:", np.array_equal(message, recovered_message))
```

## Ukladanie kľúčov

Kľúče je možné uložiť pomocou metódy `save`:

```python
keypair.public_key.save("public_key.npz")
keypair.private_key.save("private_key.npz")
```

## Načítavanie kľúčov

Kľúče je možné načítavať cez objekt `MRHSCrypto`:

```python
public_key = scheme.load_public_key("public_key.npz")
private_key = scheme.load_private_key("private_key.npz")
```

Takto môže knižnica skontrolovať, či načítaný kľúč patrí k rovnakým parametrom kryptosystému.