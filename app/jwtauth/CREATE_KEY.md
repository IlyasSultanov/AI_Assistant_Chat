Create private key for work on jwt

shell openssl genrsa -out jwt-private.pem 2048

Create public key for work on jwt

shell openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem