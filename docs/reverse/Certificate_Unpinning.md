# Defeating Android Certificate Pinning for Ecovacs Home App

This document explains how to bypass certificate pinning in the Ecovacs Home Android application using a provided script or manual commands.

## \\\\ Prerequisites

-   Docker (for the automated script)
-   ADB (Android Debug Bridge) for APK installation
-   CA certificate at `./certs/ca.crt`
    -   You can use `./scripts/create-cert.sh` to create needed cert files
-   Optional (manual approach):
    -   Node.js & npm & java
    -   apk-mitm
    -   Android SDK platform-tools

## \\\\ Automated Script

A Bash script is provided at `./scripts/create-unpined-app.sh` in the root of this project. It will:

1. Build a Docker image with all required tools
1. Download and unpin the XAPK
1. Extract the patched APK(s)
1. Install them via ADB (if available)
1. Save the patched XAPK to `./data/eco-patched.xapk`

### // Usage

```sh
$./scripts/create-unpined-app.sh
```

> If `adb` is not in your PATH, the script will skip installation and prompt you to install manually.

## \\\\ Manual Commands

```sh
# Install prerequisites via Snap (Debian/Ubuntu)
sudo snap install android-studio --classic
sudo snap install node --classic
sudo npm install -g apk-mitm

# Download the original XAPK
curl -SLo ./data/eco.xapk \
  https://d.apkpure.net/b/XAPK/com.eco.global.app?version=latest

# Run apk-mitm with your CA certificate
apk-mitm "./data/eco.xapk" --certificate "./certs/ca.crt"

# Extract and install
unzip -o "./data/eco-patched.xapk" -d ./data/apks
~/.android/Sdk/platform-tools/adb install-multiple data/apks/*.apk
```

---

## \\\\ Notes

```sh
$apktool d com.eco.global.app.apk --frame-path /tmp/apktool-framework
# $apktool d -r -s com.eco.global.app.apk --frame-path /tmp/apktool-framework

# $vim com.eco.global.app/res/xml/network_security_config.xml
# $vim com.eco.global.app/res/raw/ca.pem
# $vim com.eco.global.app/res/raw/yiko_ca.cert

$apktool b com.eco.global.app --frame-path /tmp/apktool-framework

$zipalign -v 4 com.eco.global.app com.eco.global.app

$keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias mykey
$~/.android/Sdk/build-tools/36.0.0/apksigner sign --ks my-release-key.jks --v1-signing-enabled true --v2-signing-enabled true *.apk
```

## \\\\ Resources

-   <https://github.com/niklashigi/apk-mitm>
-   <https://github.com/APKLab/APKLab>
-   <https://httptoolkit.com/blog/frida-certificate-pinning/>
-   <https://github.com/sensepost/objection>
-   <https://github.com/JakeWharton/pidcat#install>
-   <https://apktool.org/>
