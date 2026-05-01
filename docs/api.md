# API

This file describes the public API of the MRHScrypto library.

---

## `MRHSCrypto`

The `MRHSCrypto` class is the main interface of the library.

The current usage flow is:

1. generate or load a key,
2. create an `MRHSCrypto` instance from that key,
3. call `encrypt` or `decrypt` depending on the key type.

### Import

```python
from mrhscrypto import MRHSCrypto
```

### Constructor

```python
MRHSCrypto(key: Key)
```

In normal usage, the `new` class method is used:

```python
scheme = MRHSCrypto.new(key)
```

### Constructor Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `Key` | Public or private key used by the instance. |

### Return Value

The constructor creates an object of type `MRHSCrypto`.

### Exceptions

| Exception | Description |
|---|---|
| `KeyValidationError` | Raised when `key` is not an instance of `Key`. |

### Example

```python
keypair = MRHSCrypto.generate_keypair(d=1, security=128)

encryptor = MRHSCrypto.new(keypair.public_key)
decryptor = MRHSCrypto.new(keypair.private_key)
```

---

## `scheme.key`

Each `MRHSCrypto` instance stores its key in:

```python
scheme.key
```

Cryptosystem parameters are stored directly in the key:

```python
scheme.key.parameters
```

### Parameter Attributes

| Attribute | Type | Description |
|---|---|---|
| `d` | `int` | Sparsity parameter. |
| `security` | `int` | Security parameter and input message length in bits. |
| `n` | `int` | Length of the plaintext formed from the message and tag. |
| `m` | `int` | Number of private-key matrix blocks. |

---

## `MRHSCrypto` Methods

| Method | Return Value | Description |
|---|---|---|
| `MRHSCrypto.generate_keypair(d, security)` | `KeyPair` | Generates a new public/private key pair. |
| `MRHSCrypto.new(key)` | `MRHSCrypto` | Creates a cryptosystem instance from a key. |
| `encrypt(message)` | `bytes` | Encrypts a byte message with the key stored in the instance. |
| `decrypt(ciphertext)` | `bytes` | Decrypts a byte ciphertext with the private key stored in the instance. |
| `MRHSCrypto.import_key(path)` | `PublicKey` or `PrivateKey` | Loads a key from a file according to the stored key type. |

---

### `generate_keypair`

Generates a new key pair. This is a static method, so no `MRHSCrypto` object has to be created before calling it.

#### Method

```python
MRHSCrypto.generate_keypair(d: int, security: int) -> KeyPair
```

#### Parameters

| Parameter | Type | Description |
|---|---|---|
| `d` | `int` | Sparsity parameter. Currently, only `1` is supported. |
| `security` | `int` | Security parameter and input message length in bits. Supported values are `128` and `256`. |

The internal parameters `n` and `m` are computed automatically.

#### Return Value

Returns a `KeyPair` object containing:

- `public_key`,
- `private_key`.

#### Exceptions

| Exception | Description |
|---|---|
| `ParameterError` | Raised for unsupported values of `d` or `security`. |

#### Example

```python
keypair = MRHSCrypto.generate_keypair(d=1, security=128)

public_key = keypair.public_key
private_key = keypair.private_key
```

---

### `new`

Creates an `MRHSCrypto` instance from a public or private key.

#### Method

```python
MRHSCrypto.new(key: Key) -> MRHSCrypto
```

#### Parameters

| Parameter | Type | Description |
|---|---|---|
| `key` | `Key` | Key used by the new instance. |

#### Example

```python
encryptor = MRHSCrypto.new(public_key)
decryptor = MRHSCrypto.new(private_key)
```

---

### `encrypt`

Encrypts a byte message using the public part of the key stored in the instance.

If the instance was created from a private key, the public key is derived before encryption by calling `private_key.public_key()`.

Before encryption, a hash tag is internally appended to the message. The resulting plaintext has this form:

```text
message || tag
```

#### Method

```python
scheme.encrypt(message: bytes) -> bytes
```

#### Parameters

| Parameter | Type | Description |
|---|---|---|
| `message` | `bytes` | Input message. Its length in bits must equal `scheme.key.parameters.security`. |

For `security=128`, the message must be 16 bytes long. For `security=256`, the message must be 32 bytes long.

#### Return Value

Returns the ciphertext as `bytes`.

#### Exceptions

| Exception | Description |
|---|---|
| `MessageValidationError` | Raised when the message is not `bytes` or has an invalid length. |
| `KeyValidationError` | May be raised for an invalid private key if a public key cannot be derived from it. |

#### Example

```python
encryptor = MRHSCrypto.new(keypair.public_key)

message = b"1234567890abcdef"
ciphertext = encryptor.encrypt(message)
```

---

### `decrypt`

Decrypts a ciphertext using the private key stored in the instance.

Decryption requires a private key. If the instance was created only from a public key, this method raises `KeyValidationError`.

The current version implements a solver for the one-sparse case:

```text
d = 1
```

During decryption, the internal plaintext has this form:

```text
message || tag
```

The hash tag is used to validate candidate plaintexts. Only the original message without the tag is returned to the user.

#### Method

```python
scheme.decrypt(ciphertext: bytes) -> bytes
```

#### Parameters

| Parameter | Type | Description |
|---|---|---|
| `ciphertext` | `bytes` | Byte ciphertext produced by `encrypt`. |

#### Return Value

Returns the decrypted message as `bytes`.

#### Exceptions

| Exception | Description |
|---|---|
| `KeyValidationError` | Raised when the instance does not contain a private key. |
| `CiphertextValidationError` | Raised when the ciphertext is not `bytes` or has an invalid length. |
| `UnsupportedSolverError` | Raised when no solver is implemented for the key's `d` parameter. |
| `DecryptionError` | Raised when no valid message can be recovered. |

#### Example

```python
decryptor = MRHSCrypto.new(keypair.private_key)

recovered_message = decryptor.decrypt(ciphertext)
```

---

### `import_key`

Loads a public or private key from a file.

The key type is determined from the data stored in the file.

#### Method

```python
MRHSCrypto.import_key(path) -> Key
```

#### Parameters

| Parameter | Type | Description |
|---|---|---|
| `path` | `str` or `pathlib.Path` | Path to the stored key file. The file must use the `.npz` extension. |

#### Return Value

Returns either a `PublicKey` object or a `PrivateKey` object.

#### Exceptions

| Exception | Description |
|---|---|
| `KeySerializationError` | Raised for an invalid path, invalid extension, or file reading error. |
| `KeyValidationError` | Raised for an unknown key type stored in the file. |

#### Example

```python
public_key = MRHSCrypto.import_key("public_key.npz")
private_key = MRHSCrypto.import_key("private_key.npz")

encryptor = MRHSCrypto.new(public_key)
decryptor = MRHSCrypto.new(private_key)
```

---

## Key Classes

The library uses a shared abstract base class `Key`, which is inherited by the concrete key types:

- `PublicKey`,
- `PrivateKey`.

Each key contains the cryptosystem parameters it belongs to.

---

### `Key`

Abstract base class for keys.

This class is not intended to be instantiated directly. It is a shared base for public and private keys.

#### Attributes

| Attribute | Type | Description |
|---|---|---|
| `parameters` | `MRHSParameters` | Cryptosystem parameters associated with the key. |

#### Methods

| Method | Return Value | Description |
|---|---|---|
| `save(path)` | `None` | Saves the key to a file. The exact serialization depends on the key type. |
| `has_private()` | `bool` | Indicates whether the object contains the private part of the key. |
| `public_key()` | `PublicKey` | Returns or derives the public key. |

---

### `PublicKey`

Class representing a public key.

The public key is used for encryption.

#### Attributes

| Attribute | Type | Description |
|---|---|---|
| `parameters` | `MRHSParameters` | Cryptosystem parameters associated with the public key. |
| `G` | `np.ndarray` | Public matrix used during encryption. |

#### Methods

| Method | Return Value | Description |
|---|---|---|
| `save(path)` | `None` | Saves the public key to an `.npz` file. |
| `has_private()` | `bool` | Returns `False`, because a public key does not contain the private part. |
| `public_key()` | `PublicKey` | Returns itself. |

#### Example

```python
public_key.save("public_key.npz")

if not public_key.has_private():
    print("This is a public key.")
```

---

### `PrivateKey`

Class representing a private key.

The private key is used for decryption. It contains the information required to solve the MRHS system.

#### Attributes

| Attribute | Type | Description |
|---|---|---|
| `parameters` | `MRHSParameters` | Cryptosystem parameters associated with the private key. |
| `M` | `np.ndarray` | Private sparse block matrix. |
| `R` | `np.ndarray` | Invertible matrix over GF(2). |

#### Methods

| Method | Return Value | Description |
|---|---|---|
| `save(path)` | `None` | Saves the private key to an `.npz` file. |
| `has_private()` | `bool` | Returns `True`, because the object contains the private part of the key. |
| `public_key()` | `PublicKey` | Derives the public key from the private key. |

#### `public_key` Method

The `public_key()` method computes the public key from the private key using:

```text
G = R^{-1} M
```

Before computing the result, it checks whether `R` is invertible. If `R` is not invertible, the method raises `KeyValidationError`.

#### Example

```python
private_key.save("private_key.npz")

if private_key.has_private():
    print("This is a private key.")

public_key = private_key.public_key()
```

---

### `KeyPair`

Class representing a key pair.

A `KeyPair` object is returned by key generation.

#### Attributes

| Attribute | Type | Description |
|---|---|---|
| `public_key` | `PublicKey` | Public key. |
| `private_key` | `PrivateKey` | Private key. |

#### Example

```python
keypair = MRHSCrypto.generate_keypair(d=1, security=128)

public_key = keypair.public_key
private_key = keypair.private_key
```

---

## Distinguishing Key Types

Use `has_private()` to distinguish between public and private keys.

```python
key = MRHSCrypto.import_key("key_file.npz")

if key.has_private():
    print("The loaded key is a private key.")
else:
    print("The loaded key is a public key.")
```

This is useful when loading a key with `import_key` and the user does not know in advance whether the file contains a public or private key.

---

## Exceptions

The library defines custom exceptions for invalid inputs and unsupported operations.

| Exception | Description |
|---|---|
| `MRHSCryptoError` | Base exception of the library. All other custom exceptions inherit from this exception. |
| `ParameterError` | Exception for invalid cryptosystem parameters. |
| `UnsupportedSolverError` | Exception raised when no solver is implemented for the requested value of `d`. |
| `KeyValidationError` | Exception for invalid keys or for using a public key for decryption. |
| `MessageValidationError` | Exception for an invalid input message. |
| `CiphertextValidationError` | Exception for an invalid ciphertext. |
| `DecryptionError` | Exception for decryption failure. |
| `KeySerializationError` | Exception for key serialization or loading failures. |

### Catching Library Errors

Users can catch all library-specific errors with the base exception `MRHSCryptoError`:

```python
from mrhscrypto import MRHSCryptoError

try:
    ...
except MRHSCryptoError as error:
    print(error)
```
