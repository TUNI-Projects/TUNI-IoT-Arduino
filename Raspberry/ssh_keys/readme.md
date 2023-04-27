# SSH Keys

This folder should contain a file, `awesome_secret.pub`. This file will be used to encrypt and send the encrypted data over the Internet to CoAP server. If there's no `.pub` file, it will just send the data unencrypted.

Ideally, DTLS is the best option to provide security of Data in Transit. However, ATM I don't have the time to do it. (Ibtehaz)
