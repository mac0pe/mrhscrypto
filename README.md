# MRHScrypto

MRHScrypto is an experimental Python library implementing a cryptosystem based on MRHS equations.

The project is currently under development. The current implementation mainly supports the one-sparse case, meaning `d = 1`.

> **Warning**
>
> This library is experimental and is not intended for real cryptographic use.

## Features

- public and private key generation,
- creating a cryptosystem instance from an existing key,
- encryption of byte messages,
- decryption of byte ciphertexts,
- support for the one-sparse case with `d = 1`,
- saving and loading public and private keys.

## Installation

### Local Installation

```bash
git clone https://github.com/mac0pe/mrhscrypto.git
cd mrhscrypto
pip install -e .
```

### Installation From GitHub

```bash
pip install "mrhscrypto @ git+https://github.com/mac0pe/mrhscrypto.git@main"
```

## Basic Usage

First generate a key pair. Then create an `MRHSCrypto` instance from the key you want to use.

```python
from mrhscrypto import MRHSCrypto

keypair = MRHSCrypto.generate_keypair(d=1, security=128)

encryptor = MRHSCrypto.new(keypair.public_key)
decryptor = MRHSCrypto.new(keypair.private_key)

message = b"1234567890abcdef"  # 16 bytes = 128 bits

ciphertext = encryptor.encrypt(message)
decrypted_message = decryptor.decrypt(ciphertext)

print("Success:", message == decrypted_message)
```

For `security=128`, the message must be 16 bytes long. For `security=256`, the message must be 32 bytes long.

## Saving and Loading Keys

```python
keypair.public_key.save("public_key.npz")
keypair.private_key.save("private_key.npz")

public_key = MRHSCrypto.import_key("public_key.npz")
private_key = MRHSCrypto.import_key("private_key.npz")

encryptor = MRHSCrypto.new(public_key)
decryptor = MRHSCrypto.new(private_key)
```

If only the private key is available, the public key can be derived from it:

```python
public_key = private_key.public_key()
```

You can differentiate between the private and public key using has_private method: 

```python
key.has_private()
```
## Project Status

Currently implemented:

- key generation,
- encryption,
- decryption,
- one-sparse solver,
- key serialization.

## Documentation

More detailed API documentation is available in:

```text
docs/
```

## License

This project is licensed under the MIT license.
