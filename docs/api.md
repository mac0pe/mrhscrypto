# API

Tento súbor popisuje verejné API knižnice MRHScrypto.

---

## `MRHSCrypto`

Trieda `MRHSCrypto` je hlavné rozhranie knižnice.

Používateľ si vytvorí inštanciu kryptosystému s konkrétnymi parametrami a následne cez ňu generuje kľúče, šifruje, dešifruje a načítava uložené kľúče.

### Import

```python
from mrhscrypto import MRHSCrypto
```

### Konštruktor

```python
MRHSCrypto(d: int, security: int)
```

### Parametre konštruktora

| Parameter | Typ | Popis |
|---|---|---|
| `d` | `int` | Parameter riedkosti. Určuje, ktorý riešič sa použije pri dešifrovaní. Aktuálne je podporovaná iba hodnota `d = 1`. |
| `security` | `int` | Bezpečnostný parameter. V aktuálnej implementácii určuje aj dĺžku vstupnej správy. Podporované hodnoty sú `128` a `256`. |

Interné parametre `n` a `m` sa vypočítajú automaticky.

### Návratová hodnota

Konštruktor vytvorí objekt typu `MRHSCrypto`.

### Výnimky

| Výnimka | Popis |
|---|---|
| `ParameterError` | Vyhodená v prípade neplatných parametrov, napríklad pri nepodporovanej hodnote `d` alebo `security`. |

### Príklad

```python
from mrhscrypto import MRHSCrypto

scheme = MRHSCrypto(d=1, security=128)
```

---

## `scheme.parameters`

Každá inštancia `MRHSCrypto` obsahuje vypočítané parametre v atribúte:

```python
scheme.parameters
```

### Atribúty parametrov

| Atribút | Typ | Popis |
|---|---|---|
| `d` | `int` | Parameter riedkosti. |
| `security` | `int` | Bezpečnostný parameter a dĺžka vstupnej správy. |
| `n` | `int` | Dĺžka plaintextu vytvoreného zo správy a tagu. |
| `m` | `int` | Počet blokov matice súkromného kľúča. |

Tieto parametre sa ukladajú aj spolu s kľúčmi, aby bolo možné pri načítavaní overiť kompatibilitu kľúča s aktuálnou inštanciou kryptosystému.

---

## Metódy triedy `MRHSCrypto`

| Metóda | Návratová hodnota | Popis |
|---|---|---|
| `generate_keypair()` | `KeyPair` | Vygeneruje nový pár verejného a súkromného kľúča. |
| `encrypt(message, public_key)` | `np.ndarray` | Zašifruje binárnu správu pomocou verejného kľúča. |
| `decrypt(ciphertext, private_key)` | `np.ndarray` alebo `None` | Dešifruje šifrovaný text pomocou súkromného kľúča. |
| `load_public_key(path)` | `PublicKey` | Načíta verejný kľúč zo súboru. |
| `load_private_key(path)` | `PrivateKey` | Načíta súkromný kľúč zo súboru. |
| `load_key(path)` | `PublicKey` alebo `PrivateKey` | Načíta všeobecný kľúč zo súboru podľa uloženého typu. |

---

### `generate_keypair`

Vygeneruje nový pár kľúčov.

#### Metóda

```python
scheme.generate_keypair() -> KeyPair
```

#### Parametre

Táto metóda nemá žiadne vstupné parametre. Používa parametre uložené v inštancii `MRHSCrypto`.

#### Návratová hodnota

Vracia objekt typu `KeyPair`.

Objekt `KeyPair` obsahuje:

- `public_key`,
- `private_key`.

#### Príklad

```python
keypair = scheme.generate_keypair()

public_key = keypair.public_key
private_key = keypair.private_key
```

---

### `encrypt`

Zašifruje binárnu správu pomocou verejného kľúča.

Pred samotným šifrovaním sa k správe interne pripojí hash tag. Výsledný plaintext má tvar:

```text
message || tag
```

Následne sa plaintext zašifruje pomocou verejného kľúča.

#### Metóda

```python
scheme.encrypt(message: np.ndarray, public_key: PublicKey) -> np.ndarray
```

#### Parametre

| Parameter | Typ | Popis |
|---|---|---|
| `message` | `np.ndarray` | Binárny NumPy vektor obsahujúci vstupnú správu. Dĺžka správy musí byť `scheme.parameters.security`. |
| `public_key` | `PublicKey` | Verejný kľúč použitý na šifrovanie. |

#### Návratová hodnota

Vracia šifrovaný text ako NumPy vektor.

#### Výnimky

| Výnimka | Popis |
|---|---|
| `MessageValidationError` | Vyhodená v prípade, že správa nemá správnu dĺžku alebo správny formát. |
| `KeyValidationError` | Vyhodená v prípade, že verejný kľúč nie je kompatibilný s aktuálnou inštanciou kryptosystému. |

#### Príklad

```python
import numpy as np

message = np.random.randint(
    0,
    2,
    size=scheme.parameters.security,
    dtype=np.uint8,
)

ciphertext = scheme.encrypt(message, keypair.public_key)
```

---

### `decrypt`

Dešifruje šifrovaný text pomocou súkromného kľúča.

Dešifrovanie využíva MRHS riešič zvolený podľa parametra `d`.

V aktuálnej verzii je implementovaný riešič pre one-sparse prípad, teda pre:

```text
d = 1
```

Počas dešifrovania sa interne pracuje s plaintextom v tvare:

```text
message || tag
```

Hash tag sa používa na overenie správnosti kandidátov. Používateľovi sa vracia iba pôvodná správa bez tagu.

#### Metóda

```python
scheme.decrypt(ciphertext: np.ndarray, private_key: PrivateKey) -> np.ndarray | None
```

#### Parametre

| Parameter | Typ | Popis |
|---|---|---|
| `ciphertext` | `np.ndarray` | NumPy vektor obsahujúci šifrovaný text. |
| `private_key` | `PrivateKey` | Súkromný kľúč použitý na dešifrovanie. |

#### Návratová hodnota

Vracia dešifrovanú správu ako NumPy vektor.

Ak sa nepodarí nájsť platnú správu, aktuálna implementácia môže vrátiť `None`.

#### Výnimky

| Výnimka | Popis |
|---|---|
| `CiphertextValidationError` | Vyhodená v prípade, že šifrovaný text nemá správnu dĺžku alebo správny formát. |
| `KeyValidationError` | Vyhodená v prípade, že súkromný kľúč nie je kompatibilný s aktuálnou inštanciou kryptosystému. |

#### Príklad

```python
recovered_message = scheme.decrypt(ciphertext, keypair.private_key)
```

---

### `load_public_key`

Načíta verejný kľúč zo súboru.

Kľúč sa načítava cez inštanciu `MRHSCrypto`, aby bolo možné overiť, či parametre uloženého kľúča zodpovedajú aktuálnej inštancii kryptosystému.

#### Metóda

```python
scheme.load_public_key(path: str) -> PublicKey
```

#### Parametre

| Parameter | Typ | Popis |
|---|---|---|
| `path` | `str` | Cesta k súboru s uloženým verejným kľúčom. |

#### Návratová hodnota

Vracia objekt typu `PublicKey`.

#### Výnimky

| Výnimka | Popis |
|---|---|
| `KeyValidationError` | Vyhodená v prípade, že súbor neobsahuje verejný kľúč alebo parametre kľúča nesedia s aktuálnou inštanciou. |

#### Príklad

```python
public_key = scheme.load_public_key("public_key.npz")
```

---

### `load_private_key`

Načíta súkromný kľúč zo súboru.

Kľúč sa načítava cez inštanciu `MRHSCrypto`, aby bolo možné overiť kompatibilitu parametrov.

#### Metóda

```python
scheme.load_private_key(path: str) -> PrivateKey
```

#### Parametre

| Parameter | Typ | Popis |
|---|---|---|
| `path` | `str` | Cesta k súboru s uloženým súkromným kľúčom. |

#### Návratová hodnota

Vracia objekt typu `PrivateKey`.

#### Výnimky

| Výnimka | Popis |
|---|---|
| `KeyValidationError` | Vyhodená v prípade, že súbor neobsahuje súkromný kľúč alebo parametre kľúča nesedia s aktuálnou inštanciou. |

#### Príklad

```python
private_key = scheme.load_private_key("private_key.npz")
```

---

### `load_key`

Načíta verejný alebo súkromný kľúč zo súboru.

Typ kľúča sa určí podľa informácie uloženej v súbore.

#### Metóda

```python
scheme.load_key(path: str) -> PublicKey | PrivateKey
```

#### Parametre

| Parameter | Typ | Popis |
|---|---|---|
| `path` | `str` | Cesta k súboru s uloženým kľúčom. |

#### Návratová hodnota

Vracia buď objekt typu `PublicKey`, alebo objekt typu `PrivateKey`.

#### Výnimky

| Výnimka | Popis |
|---|---|
| `KeyValidationError` | Vyhodená v prípade neplatného formátu súboru, neznámeho typu kľúča alebo nekompatibilných parametrov. |

#### Príklad

```python
key = scheme.load_key("key_file.npz")
```

---

## Kľúčové triedy

Knižnica používa spoločnú abstraktnú triedu `Key`, z ktorej dedia konkrétne typy kľúčov:

- `PublicKey`,
- `PrivateKey`.

Každý kľúč obsahuje parametre kryptosystému, ku ktorým patrí.

---

### `Key`

Abstraktná základná trieda pre kľúče.

Táto trieda nie je určená na priame vytváranie objektov. Slúži ako spoločný základ pre verejný a súkromný kľúč.

#### Atribúty

| Atribút | Typ | Popis |
|---|---|---|
| `parameters` | `MRHSParameters` | Parametre kryptosystému, ku ktorým kľúč patrí. |

#### Metódy

| Metóda | Návratová hodnota | Popis |
|---|---|---|
| `save(path)` | `None` | Uloží kľúč do súboru. Konkrétny spôsob uloženia závisí od typu kľúča. |
| `has_private()` | `bool` | Určuje, či objekt obsahuje súkromnú časť kľúča. |

---

### `PublicKey`

Trieda reprezentujúca verejný kľúč.

Verejný kľúč sa používa pri šifrovaní.

#### Atribúty

| Atribút | Typ | Popis |
|---|---|---|
| `parameters` | `MRHSParameters` | Parametre kryptosystému, ku ktorým verejný kľúč patrí. |
| `G` | `np.ndarray` | Verejná matica používaná pri šifrovaní. |

#### Metódy

| Metóda | Návratová hodnota | Popis |
|---|---|---|
| `save(path)` | `None` | Uloží verejný kľúč do súboru. |
| `has_private()` | `bool` | Vráti `False`, pretože verejný kľúč neobsahuje súkromnú časť. |

#### Príklad

```python
public_key.save("public_key.npz")

if not public_key.has_private():
    print("Toto je verejný kľúč.")
```

---

### `PrivateKey`

Trieda reprezentujúca súkromný kľúč.

Súkromný kľúč sa používa pri dešifrovaní. Obsahuje informácie potrebné na riešenie MRHS systému.

#### Atribúty

| Atribút | Typ | Popis |
|---|---|---|
| `parameters` | `MRHSParameters` | Parametre kryptosystému, ku ktorým súkromný kľúč patrí. |
| `M` | `np.ndarray` | Súkromná riedka bloková matica. |
| `R` | `np.ndarray` | Invertibilná matica nad GF(2). |

#### Metódy

| Metóda | Návratová hodnota | Popis |
|---|---|---|
| `save(path)` | `None` | Uloží súkromný kľúč do súboru. |
| `has_private()` | `bool` | Vráti `True`, pretože objekt obsahuje súkromnú časť kľúča. |
| `public_key()` | `PublicKey` | Dopočíta verejný kľúč zo súkromného kľúča. |

#### Metóda `public_key`

Metóda `public_key()` vypočíta verejný kľúč zo súkromného kľúča podľa vzťahu:

```text
G = R^{-1} M
```

Pred výpočtom sa overí, či je matica `R` invertibilná. Ak `R` nie je invertibilná, metóda vyhodí výnimku `KeyValidationError`.

#### Príklad

```python
private_key.save("private_key.npz")

if private_key.has_private():
    print("Toto je súkromný kľúč.")

public_key = private_key.public_key()
```

---

### `KeyPair`

Trieda reprezentujúca pár kľúčov.

Objekt `KeyPair` sa vracia pri generovaní kľúčov.

#### Atribúty

| Atribút | Typ | Popis |
|---|---|---|
| `public_key` | `PublicKey` | Verejný kľúč. |
| `private_key` | `PrivateKey` | Súkromný kľúč. |

#### Príklad

```python
keypair = scheme.generate_keypair()

public_key = keypair.public_key
private_key = keypair.private_key
```

---

## Rozlíšenie typu kľúča

Na rozlíšenie verejného a súkromného kľúča je možné použiť metódu `has_private()`.

```python
key = scheme.load_key("key_file.npz")

if key.has_private():
    print("Načítaný kľúč je súkromný kľúč.")
else:
    print("Načítaný kľúč je verejný kľúč.")
```

Táto metóda je užitočná najmä pri všeobecnom načítavaní pomocou `load_key`, keď používateľ dopredu nemusí vedieť, či súbor obsahuje verejný alebo súkromný kľúč.

---

## Výnimky

Knižnica definuje vlastné výnimky pre chybné vstupy a nepodporované operácie.

| Výnimka | Popis |
|---|---|
| `MRHSCryptoError` | Základná výnimka knižnice. Všetky ostatné vlastné výnimky by mali dediť od tejto výnimky. |
| `ParameterError` | Výnimka pre neplatné parametre kryptosystému. |
| `UnsupportedSolverError` | Výnimka pre prípad, že pre zadanú hodnotu `d` nie je implementovaný riešič. |
| `KeyValidationError` | Výnimka pre neplatné alebo nekompatibilné kľúče. |
| `MessageValidationError` | Výnimka pre neplatnú vstupnú správu. |
| `CiphertextValidationError` | Výnimka pre neplatný šifrovaný text. |
| `DecryptionError` | Výnimka určená pre zlyhanie dešifrovania. |

### Zachytenie chýb knižnice

Používateľ môže zachytiť všetky chyby knižnice pomocou základnej výnimky `MRHSCryptoError`:

```python
try:
    ...
except MRHSCryptoError as error:
    print(error)
```