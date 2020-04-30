# Thermal Security Camera

A real-time thermal security camera using a raspberry pi with Adafruit AMG8833 thermal sensor, Flask with server sent events, and machine learning to classify human thermal traces.

![Thermal Security Camera Demo](https://github.com/benniferLopez/thermal-security-camera/blob/master/thermalCamDemo.gif)



## Getting Started with this repo

### What hardware you'll need

1. Raspberry pi or other microcontroller (I used Rpi4B)
2. Adafruit AMG8833 thermal sensor
3. Soldering iron
4. Female to female jumper wires


### Setup and preparing pi

Follow tutorial on Adafruit to install necessary software and enable I2C (https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/raspberry-pi-thermal-camera)


### Clone this repo on the pi

```
git clone https://github.com/benniferLopez/thermal-security-camera.git
```

### Install the necessary dependencies
```
pip3 install requirements.txt
```

### Setup Redis on the pi

Following the guide found ![here](https://habilisbest.com/install-redis-on-your-raspberrypi), I've pulled out and cleaned up the steps:

```
cd ~
wget http://download.redis.io/redis-stable.tar.gz
tar xzf redis*
cd redis-stable/
sudo make
sudo make install PREFIX=/usr
sudo mkdir /etc/redis
sudo cp redis.conf /etc/redis/
cd ..
sudo rm -Rf redis*
sudo adduser --system --group --disabled-login redis --no-create-home --shell /bin/nologin --quiet
sudo mkdir -p /var/run/redis
sudo chown -R redis /var/run/redis
sudo nano /etc/init.d/redis-server
sudo chmod +x /etc/init.d/redis-server
sudo update-rc.d redis-server defaults
```

To start the Redis server:

```
sudo service redis-server restart
```

In order to customize this Redis server to our needs we need to change the config by changing daemonize to yes:

```
sudo nano /etc/redis/redis.conf
```
Find the line "daemonize no" and change it to "daemonize yes"


Finally, restart the Redis server for these changes to take effect:

```
sudo service redis-server restart
```


### Launch the Flask app!!

Navigate back to your thermal-security-camera/ directory and run the following to start the flask app locally:

```
sudo flask run -h 0.0.0.0 &>/dev/null & disown
```

This command will start the Flask app with the host of 0.0.0.0 to allow others on the network to access it.
Also, this starts Flask in the background and discards log output.
To retain output omit the ```&>/dev/null``` part
To run this in the foreground omit the last ```&```
Lastly, the process is disowned, allowing you to safely exit the terminal while the process continues to run on your pi.



### Viewing results

In order to see the running Flask app, we will need to know the IP address of the raspberry pi which is hosting it.
This can be easily obtained by running the following command on your pi:

```
hostname -I
```

Take the first, period-separated value which this call returns. Note this number, likely 192.168.XXX.XXX, as it is the local IP address of your pi on the network and will be needed to access your app.

To see the running thermal security camera navigate in any browser that is not IE to http://<your-ip-here>:5000/. 
In my case, http://192.168.1.102:5000/

In this view, you will see the live stream from your raspberry pi thermal security camera with an annotation below denoting if a person is present or not.


### Adjust view settings

Based on the environment in which your thermal camera is operating it may be necessary to adjust the view you see from your system. This can be accomplished painlessly by using URL parameters. The two options are:
  ``` 
      mintemp: Minimum temperature to detect
      maxtemp: Maximum temperature to detect
  ```
An example modification could be http://192.168.1.102:5000/?mintemp=10&maxtemp=60 to detect a much wider range than the default mintemp = 18 and maxtemp = 30.

It is worth noting, however, that the defaults prescribed by Adafruit are usually optimal for contrast viewing of humans given average body temperature.

Also, these parameters only affect viewing and have no bearing on the data classification happening in the backend which is performed on the raw pixel data from the thermal sensors themselves.
