#!/usr/bin/env bash

if [ ! -f "ca.crt" ] || [ ! -f "ca.key" ] || [ ! -f "bumper.crt" ] || [ ! -f "bumper.key" ]; then
  echo "Create CA cert ..."
  openssl ecparam -name prime256v1 -genkey -out ca.key
  openssl req -new -x509 -sha256 -days 6669 -key ca.key -out ca.crt \
    -subj "/O=Bumper/CN=Bumper CA"

  echo "Create Server cert ..."
  openssl ecparam -name prime256v1 -genkey -out bumper.key
  openssl req -new -sha256 -key bumper.key -out bumper.csr \
    -subj "/O=Bumper/CN=Bumper Server" \
    -config <(
      : 'cat /etc/ssl/openssl.cnf ; \'
      echo '[req]'
      echo 'distinguished_name=req'
      echo 'req_extensions=v3_req'
      echo 'x509_extensions=v3_req'
      echo "[v3_req]"
      echo "subjectAltName=IP:127.0.0.1,DNS:localhost,DNS:ecovacs.com,DNS:*.ecovacs.com,DNS:ecovacs.net,DNS:*.ecovacs.net,DNS:ecouser.net,DNS:*.ecouser.net,DNS:*.ww.ecouser.net,DNS:*.dc.ww.ecouser.net,DNS:*.dc-as.ww.ecouser.net,DNS:*.dc-eu.ww.ecouser.net,DNS:*.dc-na.ww.ecouser.net,DNS:*.area.ww.ecouser.net,DNS:*.robotww.ecouser.net,DNS:*.dc.robotww.ecouser.net,DNS:*.cn.ecouser.net"
    )
  openssl x509 -req -in bumper.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -sha256 -days 6669 -out bumper.crt \
    -extensions v3_req \
    -extfile <(
      : 'cat /etc/ssl/openssl.cnf ; \'
      echo '[req]'
      echo 'distinguished_name=req'
      echo 'req_extensions=v3_req'
      echo 'x509_extensions=v3_req'
      echo "[v3_req]"
      echo "subjectAltName=IP:127.0.0.1,DNS:localhost,DNS:ecovacs.com,DNS:*.ecovacs.com,DNS:ecovacs.net,DNS:*.ecovacs.net,DNS:ecouser.net,DNS:*.ecouser.net,DNS:*.ww.ecouser.net,DNS:*.dc.ww.ecouser.net,DNS:*.dc-as.ww.ecouser.net,DNS:*.dc-eu.ww.ecouser.net,DNS:*.dc-na.ww.ecouser.net,DNS:*.area.ww.ecouser.net,DNS:*.robotww.ecouser.net,DNS:*.dc.robotww.ecouser.net,DNS:*.cn.ecouser.net"
    ) 2>/dev/null

  echo "Cleanup ..."
  rm bumper.csr
  rm ca.srl

else
  echo "All needed Cert files exists, nothing todo!"
fi

exit 0
