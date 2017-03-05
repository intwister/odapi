# odapi

A Raspberry PI application to look up lists of words from the Oxford Dictionaries API and display the word and definition on a TM1638 LED display. It is a kind of retro vocabulary builder that sits in the corner and teaches you new words.

This project uses the TM1638 library from https://github.com/justinfoley/py-tm1638 which was forked from prior work.

A video can be seen here: [video](https://1drv.ms/v/s!AocT69KY_1N9llVdOE8FnISPd_Pl)


*Install Git*
```
sudo apt-get install git-core
```

*Clone source*
```
cd /home/pi
git clone https://github.com/justinfoley/odapi odapi
```

*Add python modules*
```
sudo apt-get install python-requests
```

*Setup your ODAPI Key*

1. Register at developer.oxforddictionaries.com
2. Add the details to the config file

```
cp config-template.json config.json
vi config.json
<Fill in your api key details>
```

*Install start script*
```
sudo chmod 644 /home/pi/odapi/odapi.service
sudo cp /home/pi/odapi/odapi.service /lib/systemd/system/odapi.service

sudo systemctl daemon-reload
sudo systemctl enable odapi.service
sudo reboot
sudo systemctl status odapi.service
```
