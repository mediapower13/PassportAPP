"""
Generate encryption key for PassportApp
"""

from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key()

print("=" * 60)
print("Encryption Key Generated")
print("=" * 60)
print("\nAdd this line to your .env file:")
print(f"\nENCRYPTION_KEY={key.decode()}")
print("\n" + "=" * 60)
print("\n⚠️  IMPORTANT: Keep this key secret and secure!")
print("⚠️  Never commit .env file to git!")
print("=" * 60)
