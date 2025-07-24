bootstrap-dht
=============

The DHT bootstrap server can be used as an introducer to the bittorrent
DHT network. Like the ones running at ``router.utorrent.com`` and
``router.bittorrent.com``.

ابتدا دستورات زیر رو به صورت تک به تک اجرا کنید:

``sudo apt update``

``sudo apt install -y git libboost-all-dev boost-build python3``

``git clone --branch fix-build https://github.com/arvidn/bootstrap-dht.git``

``sudo apt install -y g++``

``cd ~/bootstrap-dht``

``bjam``

پورت پیش فرض این نود 6881 هست پس اون روی باید روی فایروال باز کنید

``sudo apt install ufw``

``sudo ufw allow 6881/udp``

برای اینکه dht-bootstrap پس از بسته شدن SSH و همچنین بعد از ریستارت سرور به صورت خودکار اجرا بشه، بهترین راه ایجاد یک سرویس systemd هست.

* ساخت سرویس systemd برای dht-bootstrap:

1. ایجاد فایل سرویس systemctl

با ویرایشگر nano (یا هر ویرایشگر دلخواه) فایل زیر رو بساز:


``sudo nano /etc/systemd/system/dht-bootstrap.service``

2. متن زیر رو در فایل سرویس کپی کن:

[Unit]
Description=DHT Bootstrap Node
After=network.target

[Service]
Type=simple
User=``root``
WorkingDirectory=/root/bootstrap-dht
ExecStart=/root/bootstrap-dht/dht-bootstrap ``YourServerIp`` --port ``6881``
Restart=on-failure

[Install]
WantedBy=multi-user.target

* نکته:

قسمت User=root در صورتی‌که می‌خوای با یوزر روت اجرا بشه، اگر یوزر دیگه مدنظرت هست، عوض کن.

قسمت ExecStart رو حتماً با IP واقعی سرورت و مسیرهای درست جایگزین کن.

* ذخیره و خروج (در nano: Ctrl+O و Enter برای ذخیره، Ctrl+X برای خروج)

* فعال و شروع سرویس systemctl:

``sudo systemctl daemon-reload``

``sudo systemctl start dht-bootstrap.service``

``sudo systemctl enable dht-bootstrap.service``

* بررسی وضعیت سرویس:

``sudo systemctl status dht-bootstrap.service``

اگر همه‌چیز درست باشه، باید وضعیت active (running) رو ببینی.

حالا می تونید از نود ( آی پی ) در برنامه های مختلف استفاده کنید.




