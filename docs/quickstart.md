# Quickstart

This file shows the basic usage of the MRHScrypto library.

## 1. Import the Library

```python
from mrhscrypto import MRHSCrypto
```

## 2. Generate Keys

Keys are generated before creating a cryptosystem instance:

```python
keypair = MRHSCrypto.generate_keypair(d=1, security=128)
```

The `d` parameter determines the sparsity type and the solver used during decryption. Currently, only this value is supported:

```text
d = 1
```

The `security` parameter determines the input message length in bits. Supported values are:

```text
128, 256
```

The `keypair` object contains a public key and a private key:

```python
public_key = keypair.public_key
private_key = keypair.private_key
```

The public key is used for encryption. The private key is used for decryption.

## 3. Create a Cryptosystem Instance From a Key

An `MRHSCrypto` instance always works with one key:

```python
encryptor = MRHSCrypto.new(public_key)
decryptor = MRHSCrypto.new(private_key)
```

An instance created from a public key can encrypt. An instance created from a private key can encrypt and decrypt, because the public key can be derived from the private key.

## 4. Create a Message

The message must be of type `bytes`.

For `security=128`, the message must be 16 bytes long:

```python
message = b"1234567890abcdef"
```

For `security=256`, the message must be 32 bytes long.

## 5. Encrypt

```python
ciphertext = encryptor.encrypt(message)
```

During encryption, a hash tag is internally appended to the message. The user only passes the original message.

## 6. Decrypt

```python
recovered_message = decryptor.decrypt(ciphertext)
```

The `decrypt` method returns the original decrypted message as `bytes`.

Decryption can fail if no valid message can be recovered from the ciphertext. In that case, the method raises `DecryptionError`.

## Complete Example

```python
from mrhscrypto import MRHSCrypto, DecryptionError

keypair = MRHSCrypto.generate_keypair(d=1, security=128)

encryptor = MRHSCrypto.new(keypair.public_key)
decryptor = MRHSCrypto.new(keypair.private_key)

message = b"1234567890abcdef"

ciphertext = encryptor.encrypt(message)

print("Original message: ", message)

try:
    recovered_message = decryptor.decrypt(ciphertext)
    print("Recovered message:", recovered_message)
    print("Success:", message == recovered_message)
except DecryptionError as error:
    print("Decryption failed:", error)
```

## Saving Keys

Keys can be saved with the `save` method:

```python
keypair.public_key.save("public_key.npz")
keypair.private_key.save("private_key.npz")
```

## Loading Keys

Keys are loaded with `MRHSCrypto.import_key`:

```python
public_key = MRHSCrypto.import_key("public_key.npz")
private_key = MRHSCrypto.import_key("private_key.npz")
```

After loading a key, create a new cryptosystem instance from it:

```python
encryptor = MRHSCrypto.new(public_key)
decryptor = MRHSCrypto.new(private_key)
```

## Getting the Public Key From a Private Key

If only the private key is available, the public key can be derived from it:

```python
public_key = private_key.public_key()
```

## Differentiating between the keys

If you don't know if your Key instance is public or private you can use the has_private method to find out:

```python
key.has_private()
```
