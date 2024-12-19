#!/usr/bin/env bash

BASE_PATH="${PWD}/certs"
mkdir -p "${BASE_PATH}"

if [ ! -f "${BASE_PATH}/ca.crt" ] || [ ! -f "${BASE_PATH}/ca.key" ] || [ ! -f "${BASE_PATH}/bumper.crt" ] || [ ! -f "${BASE_PATH}/bumper.key" ]; then
  echo "Creating CA certificate..."
  openssl ecparam -name prime256v1 -genkey -out "${BASE_PATH}/ca.key"
  openssl req -new -x509 -sha256 -days 6669 -key "${BASE_PATH}/ca.key" -out "${BASE_PATH}/ca.crt" \
    -subj "/O=ecovacs/CN=ECOVACS CA"
  chmod 600 "${BASE_PATH}/ca.key"

  echo "Creating Server certificate..."
  openssl ecparam -name prime256v1 -genkey -out "${BASE_PATH}/bumper.key"
  openssl req -new -sha256 -key "${BASE_PATH}/bumper.key" -out "${BASE_PATH}/bumper.csr" \
    -subj "/O=ecovacs/CN=*.ecouser.net" \
    -config <(
      : 'cat /etc/ssl/openssl.cnf ; \'
      echo '[req]'
      echo 'distinguished_name=req'
      echo 'req_extensions=v3_req'
      echo 'x509_extensions=v3_req'
      echo "[v3_req]"
      echo "subjectAltName=IP:127.0.0.1,DNS:localhost,DNS:ecouser.net,DNS:*.ecouser.net,DNS:ecovacs.com,DNS:*.ecovacs.com,DNS:*.area.robotcn.ecouser.net,DNS:*.area.robotww.ecouser.net,DNS:*.area.ww.ecouser.net,DNS:*.cn.ecouser.net,DNS:*.dc-as.ww.ecouser.net,DNS:*.dc-eu.ww.ecouser.net,DNS:*.dc-na.ww.ecouser.net,DNS:*.dc.cn.ecouser.net,DNS:*.dc.robotcn.ecouser.net,DNS:*.dc.robotww.ecouser.net,DNS:*.dc.ww.ecouser.net,DNS:*.robotcn.ecouser.net,DNS:*.robotww.ecouser.net,DNS:*.ww.ecouser.net,DNS:ca.robotcn.ecouser.net,DNS:ca.robotww.ecouser.net,DNS:*.eu-central-1.aliyuncs.com,DNS:*.openaccount.aliyun.com,DNS:*.iot-as-mqtt.cn-shanghai.aliyuncs.com,DNS:*.itls.eu-central-1.aliyuncs.com"
    )

  openssl x509 -req -in "${BASE_PATH}/bumper.csr" -CA "${BASE_PATH}/ca.crt" -CAkey "${BASE_PATH}/ca.key" -CAcreateserial \
    -sha256 -days 6669 -out "${BASE_PATH}/bumper.crt" \
    -extensions v3_req \
    -extfile <(
      : 'cat /etc/ssl/openssl.cnf ; \'
      echo '[req]'
      echo 'distinguished_name=req'
      echo 'req_extensions=v3_req'
      echo 'x509_extensions=v3_req'
      echo "[v3_req]"
      echo "subjectAltName=IP:127.0.0.1,DNS:localhost,DNS:ecouser.net,DNS:*.ecouser.net,DNS:ecovacs.com,DNS:*.ecovacs.com,DNS:*.area.robotcn.ecouser.net,DNS:*.area.robotww.ecouser.net,DNS:*.area.ww.ecouser.net,DNS:*.cn.ecouser.net,DNS:*.dc-as.ww.ecouser.net,DNS:*.dc-eu.ww.ecouser.net,DNS:*.dc-na.ww.ecouser.net,DNS:*.dc.cn.ecouser.net,DNS:*.dc.robotcn.ecouser.net,DNS:*.dc.robotww.ecouser.net,DNS:*.dc.ww.ecouser.net,DNS:*.robotcn.ecouser.net,DNS:*.robotww.ecouser.net,DNS:*.ww.ecouser.net,DNS:ca.robotcn.ecouser.net,DNS:ca.robotww.ecouser.net,DNS:*.eu-central-1.aliyuncs.com,DNS:*.openaccount.aliyun.com,DNS:*.iot-as-mqtt.cn-shanghai.aliyuncs.com,DNS:*.itls.eu-central-1.aliyuncs.com"
    ) 2>/dev/null

  echo "Cleaning up temporary files..."
  rm "${BASE_PATH}/bumper.csr"
  rm "${BASE_PATH}/ca.srl"

  echo "Certificates created successfully in ${BASE_PATH}"
else
  echo "All needed certificate files already exist, nothing to do!"
fi
