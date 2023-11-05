# DNS

You need to configure your router to point DNS locally to where Bumper is running.  
The easiest way is overriding the main domains used by EcoVacs using DNSMasq/PiHole, by adding address entries in a custom config.

## Custom DNSMasq Config

Typically written at /etc/dnsmasq.d/{##}-{name}.conf

- Ex: `/etc/dnsmasq.d/02-custom.conf`

**File Contents:**

```txt
address=/ecouser.net/{bumper server ip}
address=/ecovacs.com/{bumper server ip}
address=/ecovacs.net/{bumper server ip}
```

**Note:** _Replace `{bumper server ip}` with your server's IP_

If using PiHole, reload FTL to apply changes:

`sudo service pihole-FTL reload`

## Manual Override

If overriding DNS for the top-level domains isn't an option, you'll need to configure your router DNS to point a number of domains used by the app/robot to the Bumper server.

**Note:** Depending on country, your phone/robot may be using a different domain. Most of these domains contain country-specific placeholders.

Not all domains have been documented at this point, and this list will be updated as more are identified/seen. The preferred way to ensure Bumper works is to override the full domains as above.
**Note:** The app dynamically gets the required domains from the endpoint `api/appsvr/service/list` and therefore ecovacs can use different domains for different models.

Replacement Examples:

- {countrycode}
  - If you see `eco-{countrycode}-api.ecovacs.com` and you live in the US/North America you would use: `eco-us-api.ecovacs.com`
  - **Note**: {countrycode} may also be generalized regions such as "EU".
- {region}
  - If you see `portal-{region}.ecouser.net` and you live in the US/North America you would use: `portal-na.ecouser.net`
  - **Note**: {region} may also be generalized regions such as "EU".

| Address                                  | Description                                    |
| ---------------------------------------- | ---------------------------------------------- |
| `lb-{countrycode}.ecovacs.net`           | Load-balancer that is checked by the app/robot |
| `lb-{countrycode}.ecouser.net`           | Load-balancer that is checked by the app/robot |
| `lbus.ecouser.net`                       | Load-balancer that is checked by the app/robot |
| `lb{countrycode}.ecouser.net`            | Load-balancer that is checked by the app/robot |
| `eco-{countrycode}-api.ecovacs.com`      | Used for Login                                 |
| `gl-{countrycode}-api.ecovacs.com`       | Used by EcoVacs Home app                       |
| `gl-{countrycode}-openapi.ecovacs.com`   | Used by EcoVacs Home app                       |
| `portal.ecouser.net`                     | Used for Login and Rest API                    |
| `portal-{countrycode}.ecouser.net`       | Used for Login and Rest API                    |
| `portal-{region}.ecouser.net`            | Used for Login and Rest API                    |
| `portal-ww.ecouser.net`                  | Used for various Rest APIs                     |
| `msg-{countrycode}.ecouser.net`          | Used for XMPP                                  |
| `msg-{region}.ecouser.net`               | Used for XMPP                                  |
| `msg-ww.ecouser.net`                     | Used for XMPP                                  |
| `mq-{countrycode}.ecouser.net`           | Used for MQTT                                  |
| `mq-{region}.ecouser.net`                | Used for MQTT                                  |
| `mq-ww.ecouser.net`                      | Used for MQTT                                  |
| `gl-{countrycode}-api.ecovacs.com`       | Used by Ecovacs Home app for API               |
| `recommender.ecovacs.com`                | Used by Ecovacs Home app                       |
| `bigdata-international.ecovacs.com`      | Telemetry/tracking                             |
| `bigdata-northamerica.ecovacs.com`       | Telemetry/tracking                             |
| `bigdata-europe.ecovacs.com`             | Telemetry/tracking                             |
| `bigdata-{unknown regions}.ecovacs.com`  | Telemetry/tracking                             |
| `api-app.ww.ecouser.net`                 | Api for App (v2+)                              |
| `api-app.dc-{region}.ww.ecouser.net`     | Api for App (v2+)                              |
| `users-base.dc-{region}.ww.ecouser.net`  | Accounts for App (v2+)                         |
| `jmq-ngiot-{region}.dc.ww.ecouser.net`   | MQTT for App (v2+)                             |
| `api-rop.dc-{region}.ww.ecouser.net`     | App (v2+)                                      |
| `jmq-ngiot-{region}.area.ww.ecouser.net` | App (v2+)                                      |

| Domain                                   | IP             | Port |
| :--------------------------------------- | :------------- | :--- |
| api-app.dc-as.ww.ecouser.net             | 13.213.212.149 | 443  |
| api-app.dc-eu.ww.ecouser.net             | 52.58.74.156   | 443  |
| api-app.ww.ecouser.net                   | 52.58.74.156   | 443  |
| portal-ww.ecouser.net                    | 3.68.172.231   | 443  |
| users-base.dc-eu.ww.ecouser.net          | 52.58.74.156   | 443  |
| jmq-ngiot-eu.dc.ww.ecouser.net           | 3.127.110.57   | 8883 |
| msg-eu.ecouser.net                       | 18.196.130.16  | 5223 |
| api-base.robotww.ecouser.net             | 13.56.199.251  | 443  |
|                                          |                |      |
| gl-de-api.ecovacs.com                    | 3.123.55.28    | 443  |
| gl-de-api.ecovacs.com                    | 52.58.23.18    | 443  |
| gl-de-openapi.ecovacs.com                | 3.123.55.28    | 443  |
| gl-us-api.ecovacs.com                    | 52.10.83.13    | 443  |
| gl-us-api.ecovacs.com                    | 54.186.31.147  | 443  |
| gl-us-pub.ecovacs.com                    | 108.138.7.23   | 443  |
| gl-us-pub.ecovacs.com                    | 108.138.7.64   | 443  |
| gl-us-pub.ecovacs.com                    | 13.224.222.120 | 443  |
| recommender.ecovacs.com                  | 116.62.93.217  | 443  |
| sa-eu-datasink.ecovacs.com               | 18.193.135.83  | 443  |
| sa-eu-datasink.ecovacs.com               | 3.123.96.17    | 443  |
| site-static.ecovacs.com                  | 13.32.27.60    | 443  |
|                                          |                |      |
| living-account.eu-central-1.aliyuncs.com | 8.211.2.91     | 443  |
| sgp-sdk.openaccount.aliyun.com           | 8.219.176.883  | 443  |

### Current domains with TLS error

| Domain                                           | IP  | Port |
| :----------------------------------------------- | :-- | :--- |
| a2JaaxoKXLq.iot-as-mqtt.cn-shanghai.aliyuncs.com |     |      |
| jmq-ngiot-na.dc.robotww.ecouser.net              |     |      |
| jmq-ngiot-eu.dc.robotww.ecouser.net              |     |      |
| public.itls.eu-central-1.aliyuncs.com            |     |      |
