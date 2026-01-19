#!/bin/bash
mkdir -p certs
cd certs

# Create the key and the certificate of the CA
openssl req -new -x509 -days 365 -nodes -out ca.crt -keyout ca.key -subj "/CN=TwinSecurityCA"

# Create the key and request (CSR) for the host agent
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj "/CN=localhost" -addext "subjectAltName = DNS:localhost,IP:127.0.0.1"

# Sign the certificate with CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -copy_extensions copy

# Create the key and request for the twin server
openssl req -new -newkey rsa:2048 -nodes -keyout client.key -out client.csr -subj "/CN=TwinClient"

# Sign the certificate with CA
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365

# Clean directory
rm *.csr *.srl
chmod 600 *.key
cd ..