# score-tesseract

by reyzeal (Rizal Ardhi Rahmadani)

Environment Ubuntu Server
Python 3.x
Tesseract-OCR
OpenCV 4.x

## Manual Installation

1. First of all, make sure you have Python3 installed
    sudo apt-get install python3 python3-pip
2. Install Tesseract-ocr
    sudo apt-get install tesseract-ocr
3. Install the dependency library
    sudo apt-get install libsm
4. Download my source code to your specified server directory
    cd ~
    git clone https://github.com/reyzeal/score-tesseract
    cd score-tesseract
5. Install the virtualenv to make python environment for this project
    pip3 install virtualenv
    python3 -m virtualenv venv
6. Activate the environment
    source venv/bin/activate
7. Install all requirements library using requirements.txt
    pip3 install -r requirements.txt
8. you can try to run it:
    venv/bin/gunicorn -b 127.0.0.1:5000 app:app


```
by reyzeal (Rizal Ardhi Rahmadani)
```
9. Done, if you prefer to run it as server service, stop the execution and do the following steps
    below.

## Deploy as Systemd Service

1. You can use the template file that I’ve put in the folder server > score.service. If you know
    how to use vim / nano, you can directly create new file in
    **/etc/systemd/system/score.service** using this command : “sudo nano
    **/etc/systemd/system/score.service** ”.
    [Unit]
    Description=Reyzeal Score Tesseract Gunicorn daemon
    After=network.target

```
[Service]
User= ubuntu
Group= ubuntu
WorkingDirectory= /home/ubuntu/score-tesseract
ExecStart= /home/ubuntu/score-tesseract/ venv/bin/gunicorn -w 3 -b
127.0.0.1:5000 app:app
```
```
[Install]
WantedBy=multi-user.target
```
2. Change all variables, focus on the red mark:

User= **<your username>**
Group= **<your username>**
WorkingDirectory= **/path/to/project**
ExecStart= **/path/to/project/** venv/bin/gunicorn -w 3 -b 127.0.0.1:5000 app:app

3. Save the file on **/etc/systemd/system/score.service.** Just save and close it if you already
    using vim / nano directly.
4. Enable and start:
    sudo systemctl enable score.service
    sudo systemctl start score.service


by reyzeal (Rizal Ardhi Rahmadani)

5. Check the status, it must be look like this:

sudo systemctl status score.service

## Apache2 Configuration

If you want to make proxy through apache2 (make it public), you can add this following lines to
your current site config file.

ProxyPreserveHost On
ProxyPass / [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
ProxyPassReverse / [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

**Note : Make sure you have these mod enabled:**
sudo a2enmod proxy
sudo a2enmod proxy_http


