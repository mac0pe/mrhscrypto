# API

Tento súbor popisuje verejné API knižnice MRHScrypto.

## `MRHSCrypto`

Trieda `MRHSCrypto` je hlavné rozhranie knižnice.

Import:

```python
from mrhscrypto import MRHSCrypto
```

### Konštruktor

```python
MRHSCrypto(d: int, security: int)
```

### Parametre konštruktora

#### `d`

Parameter riedkosti.

Určuje, ktorý riešič sa použije pri dešifrovaní.

Aktuálne je podporované iba d = 1.

Pre nepodporované hodnoty by mala knižnica vyhodiť výnimku.

#### `security`

Bezpečnostný parameter.

V aktuálnej implementácii zároveň určuje dĺžku vstupnej správy. Správa musí byť binárny vektor dĺžky `security`. Podporované veľkosti sú 128 a 256

Interné parametre `n` a `m` sa vypočítajú automaticky.

#### Návratová hodnota

Konštruktor nevytvára návratovú hodnotu. Vytvorí objekt typu `MRHSCrypto`.

#### Výnimky

- `ParameterError`  
  Vyhodená v prípade neplatných parametrov.

- `UnsupportedSolverError`  
  Vyhodená v prípade, že pre danú hodnotu `d` nie je implementovaný riešič.

#### Príklad

```python
from mrhscrypto import MRHSCrypto

scheme = MRHSCrypto(d=1, security=128)
```

## `scheme.parameters`

Každá inštancia `MRHSCrypto` obsahuje vypočítané parametre v objekte:

```python
scheme.parameters
```

Tento objekt obsahuje:

- `d`,
- `security`,
- `n`, - dĺžka plaintextu vytvoreného zo správy 
- `m`. - počet blokov matice súkromného kľúča

Tieto parametre sa ukladajú aj spolu s kľúčmi, aby bolo možné pri načítavaní overiť kompatibilitu kľúča s aktuálnou inštanciou kryptosystému.

## `generate_keypair`

Vygeneruje nový pár kľúčov.

### Metóda
```python
scheme.generate_keypair() -> KeyPair
```

### Parametre

Táto metóda nemá žiadne vstupné parametre. Používa parametre uložené v inštancii `MRHSCrypto`.

### Návratová hodnota

Vracia objekt typu `KeyPair`.

Objekt `KeyPair` obsahuje:

```python
keypair.public_key
keypair.private_key
```

### Výnimky

- `KeyValidationError`  
  Môže byť vyhodená v prípade, že vygenerované kľúče majú neplatný tvar alebo neplatné parametre.


### Príklad

```python
keypair = scheme.generate_keypair()

public_key = keypair.public_key
private_key = keypair.private_key
```

## `encrypt`

Zašifruje binárnu správu pomocou verejného kľúča.

### Metóda

```python
scheme.encrypt(message: np.ndarray, public_key: PublicKey) -> np.ndarray
```

Zašifruje binárnu správu pomocou verejného kľúča.

### Parametre

- `message`  
  Binárny NumPy vektor obsahujúci vstupnú správu.

  Dĺžka správy musí byť:

  ```python
  scheme.parameters.security
  ```

- `public_key`  
  Verejný kľúč typu `PublicKey`.


### Návratová hodnota

Vracia šifrovaný text ako NumPy vektor. 

### Výnimky

- `MessageValidationError`  
  Vyhodená v prípade, že správa nemá správnu dĺžku alebo správny formát.

- `KeyValidationError`  
  Vyhodená v prípade, že verejný kľúč nie je kompatibilný s aktuálnou inštanciou kryptosystému.

### Príklad

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

## `decrypt`

Dešifruje šifrovaný text pomocou súkromného kľúča.

Dešifrovanie využíva MRHS riešič zvolený podľa parametra `d`.

V aktuálnej verzii je implementovaný solver pre one-sparse prípad, teda pre:

```text
d = 1
```

### Metóda

```python
scheme.decrypt(ciphertext: np.ndarray, private_key: PrivateKey) -> np.ndarray
```

### Parametre

- `ciphertext`  
  NumPy vektor obsahujúci šifrovaný text.

- `private_key`  
  Súkromný kľúč typu `PrivateKey`.

### Návratová hodnota

Vracia dešifrovanú správu ako NumPy vektor.

### Výnimky

- `CiphertextValidationError`  
  Vyhodená v prípade, že šifrovaný text nemá správnu dĺžku alebo správny formát.

- `KeyValidationError`  
  Vyhodená v prípade, že súkromný kľúč nie je kompatibilný s aktuálnou inštanciou kryptosystému.

- `DecryptionError`  
  Vyhodená v prípade, že sa nepodarí nájsť platnú správu.

### Príklad

```python
recovered_message = scheme.decrypt(ciphertext, keypair.private_key)
```


## `load_public_key`

Načíta verejný kľúč zo súboru.

Kľúč sa načítava cez inštanciu `MRHSCrypto`, aby bolo možné overiť, či parametre uloženého kľúča zodpovedajú aktuálnej inštancii kryptosystému.

### Metóda

```python
scheme.load_public_key(path: str) -> PublicKey
```

### Parametre

- `path`  
  Cesta k súboru s uloženým verejným kľúčom.

### Návratová hodnota

Vracia objekt typu `PublicKey`.

### Výnimky

- `KeyValidationError`  
  Vyhodená v prípade, že súbor neobsahuje verejný kľúč alebo parametre kľúča nesedia s aktuálnou inštanciou.

### Príklad

```python
public_key = scheme.load_public_key("public_key.npz")
```

## `load_private_key`

Načíta súkromný kľúč zo súboru.

Kľúč sa načítava cez inštanciu `MRHSCrypto`, aby bolo možné overiť kompatibilitu parametrov.

### Metóda

```python
scheme.load_private_key(path: str) -> PrivateKey
```

### Parametre

- `path`  
  Cesta k súboru s uloženým súkromným kľúčom.

### Návratová hodnota

Vracia objekt typu `PrivateKey`.

### Výnimky

- `KeyValidationError`  
  Vyhodená v prípade, že súbor neobsahuje súkromný kľúč alebo parametre kľúča nesedia s aktuálnou inštanciou.

### Príklad

```python
private_key = scheme.load_private_key("private_key.npz")
```

## `load_key`

Načíta verejný alebo súkromný kľúč zo súboru.

Typ kľúča sa určí podľa informácie uloženej v súbore.

### Metóda

```python
scheme.load_key(path: str) -> PublicKey | PrivateKey
```

### Parametre

- `path`  
  Cesta k súboru s uloženým kľúčom.

### Návratová hodnota

Vracia buď:

- `PublicKey`,
- alebo `PrivateKey`.

### Výnimky

- `KeyValidationError`  
  Vyhodená v prípade neplatného formátu súboru, neznámeho typu kľúča alebo nekompatibilných parametrov.

### Príklad

```python
key = scheme.load_key("key_file.npz")
```

# Kľúčové triedy

Knižnica používa spoločnú abstraktnú triedu `Key`, z ktorej dedia konkrétne typy kľúčov:

- `PublicKey`,
- `PrivateKey`.

Oba typy kľúčov obsahujú parametre kryptosystému, ku ktorým patria.

## `Key`

Abstraktná základná trieda pre kľúče.

Táto trieda nie je určená na priame používanie. Slúži ako spoločný základ pre verejný a súkromný kľúč.

### Atribúty

- `parameters`  
  Objekt obsahujúci parametre kryptosystému, napríklad `d`, `security`, `n` a `m`.

### Metódy

```python
key.save(path: str) -> None
```

Uloží kľúč do súboru.

Konkrétny spôsob uloženia závisí od toho, či ide o verejný alebo súkromný kľúč.

```python
key.has_private() -> bool
```

Vráti informáciu o tom, či daný objekt obsahuje súkromnú časť kľúča.

Pre `PublicKey` vracia:

```text
False
```

Pre `PrivateKey` vracia:

```text
True
```

---

## `PublicKey`

Trieda reprezentujúca verejný kľúč.

Verejný kľúč sa používa pri šifrovaní.

### Atribúty

- `parameters`  
  Parametre kryptosystému, ku ktorým verejný kľúč patrí.

- `G`  
  Verejná matica použitá pri šifrovaní.

### Metódy

```python
public_key.save(path: str) -> None
```

Uloží verejný kľúč do súboru.

### Parametre

- `path`  
  Cesta k súboru, do ktorého sa má verejný kľúč uložiť.

### Návratová hodnota

Metóda nevracia žiadnu hodnotu.

### Príklad

```python
public_key.save("public_key.npz")
```

---

```python
public_key.has_private() -> bool
```

Vráti hodnotu `False`, pretože verejný kľúč neobsahuje súkromnú časť kľúča.

---

## `PrivateKey`

Trieda reprezentujúca súkromný kľúč.

Súkromný kľúč sa používa pri dešifrovaní.

### Atribúty

- `parameters`  
  Parametre kryptosystému, ku ktorým súkromný kľúč patrí.

- `M`  
  Súkromná riedka bloková matica.

- `R`  
  Invertibilná matica nad GF(2).

### Metódy

```python
private_key.save(path: str) -> None
```

Uloží súkromný kľúč do súboru.

### Parametre

- `path`  
  Cesta k súboru, do ktorého sa má súkromný kľúč uložiť.

### Návratová hodnota

Metóda nevracia žiadnu hodnotu.

### Príklad

```python
private_key.save("private_key.npz")
```

---

```python
private_key.has_private() -> bool
```

Vráti hodnotu `True`, pretože objekt `PrivateKey` obsahuje súkromnú časť kľúča.

### Príklad

```python
if private_key.has_private():
    print("Toto je súkromný kľúč.")
```

---

```python
private_key.public_key() -> PublicKey
```

Pred výpočtom sa overí, či je matica `R` invertibilná. Ak matica `R` nie je invertibilná, metóda vyhodí výnimku.

### Parametre

Táto metóda nemá žiadne vstupné parametre.

### Návratová hodnota

Vracia objekt typu `PublicKey`.

### Výnimky

- `KeyValidationError`  
  Vyhodená v prípade, že súkromný kľúč nie je platný, napríklad ak matica `R` nie je invertibilná.

### Príklad

```python
public_key = private_key.public_key()
```

Táto metóda je užitočná v prípade, že používateľ má uložený iba súkromný kľúč, ale potrebuje z neho získať príslušný verejný kľúč.

---

## `KeyPair`

Trieda reprezentujúca pár kľúčov.

Objekt `KeyPair` sa vracia pri generovaní kľúčov.

### Atribúty

- `public_key`  
  Verejný kľúč typu `PublicKey`.

- `private_key`  
  Súkromný kľúč typu `PrivateKey`.

### Príklad

```python
keypair = scheme.generate_keypair()

public_key = keypair.public_key
private_key = keypair.private_key
```

---

## Rozlíšenie verejného a súkromného kľúča

Na rozlíšenie typu kľúča je možné použiť metódu `has_private()`.

```python
key = scheme.load_key("key_file.npz")

if key.has_private():
    print("Načítaný kľúč je súkromný kľúč.")
else:
    print("Načítaný kľúč je verejný kľúč.")
```

Táto metóda je vhodná hlavne pri všeobecnom načítavaní kľúča pomocou `load_key`, keď používateľ dopredu nemusí vedieť, či súbor obsahuje verejný alebo súkromný kľúč.

# Výnimky

Knižnica definuje vlastné výnimky pre chybné vstupy a nepodporované operácie.

## `MRHSCryptoError`

Základná výnimka knižnice.

Všetky ostatné vlastné výnimky by mali dediť od tejto výnimky.

Používateľ môže zachytiť všetky chyby knižnice takto:

```python
try:
    ...
except MRHSCryptoError as error:
    print(error)
```

## `ParameterError`

Výnimka pre neplatné parametre kryptosystému.

Používa sa napríklad pri nesprávnej hodnote `d` alebo `security`.

## `UnsupportedSolverError`

Výnimka pre prípad, že pre zadanú hodnotu `d` nie je implementovaný riešič.

## `KeyValidationError`

Výnimka pre neplatné alebo nekompatibilné kľúče.

Používa sa napríklad pri:

- nesprávnom type kľúča,
- nesprávnych rozmeroch matíc,
- nesúlade parametrov kľúča a kryptosystému.

## `MessageValidationError`

Výnimka pre neplatnú vstupnú správu.

Používa sa napríklad vtedy, keď správa nemá správnu dĺžku alebo nie je binárna.

## `CiphertextValidationError`

Výnimka pre neplatný šifrovaný text.

Používa sa napríklad vtedy, keď ciphertext nemá správnu dĺžku.

## `DecryptionError`

Výnimka pre zlyhanie dešifrovania.

Používa sa v prípade, že sa nepodarí nájsť platný plaintext.