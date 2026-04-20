class MRHSCryptoError(Exception):
    """Base exception for the mrhscrypto package."""


class ParameterError(MRHSCryptoError):
    """Invalid scheme parameters."""


class UnsupportedSolverError(MRHSCryptoError):
    """No solver is implemented for the selected density d."""


class KeyValidationError(MRHSCryptoError):
    """The provided key is malformed or incompatible with the scheme."""


class MessageValidationError(MRHSCryptoError):
    """The provided message has an invalid size or format."""


class CiphertextValidationError(MRHSCryptoError):
    """The provided ciphertext has an invalid size or format."""


class DecryptionError(MRHSCryptoError):
    """Decryption failed."""


class KeySerializationError(MRHSCryptoError):
    """Raised when saving or loading a key fails."""