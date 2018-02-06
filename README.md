# About:

BatteryMonitor is(will) be the swiss army knife of battery tasks for GameBoyZero.

Firstly Thank You to @HoolyHoo and @Camble - without there inspiration and code I would be nowhere.
Please Check out there Repo's

https://github.com/HoolyHoo/gbzbatterymonitor
https://github.com/Camble/Safe-Power-Monitor

For there Sudomod Threads and related posts:

### @Camble
https://sudomod.com/forum/viewtopic.php?f=38&t=2348

### @HoolyHoo
https://www.sudomod.com/forum/viewtopic.php?f=38&t=3699

### Discussion
https://sudomod.com/forum/viewtopic.php?f=43&t=4858&start=30

# Features:

* My script has several features which I wanted :
* Daemonised - has a daemon base class that allows POSIX standard Daemon (start|stop|restart|status)
* Single location for Config
* More unified code - a more coherent method for displaying the icon file - rather than having two scripts communicating via an open
* Rather than toggling the icon I've got it stet up on a timer - but will be configurable to be a toggle 
* As the value changes and it cycles through the percent range it will display the icon i.e. if it was 75% and it drops to 50% the indicator will display the 50% icon

# Compatible Components:

* ADS1015
* ADS1115
* Camble's SafeShutdown Bangood and Powerboost Version (comming soon)


# Wiring Diagrams:
### ADS Wiring for ADS1015 and ADS1115
![ADS1015](https://i.imgur.com/hsFYtSR.jpg)

# TODO:

### Now this is a work in progress and still needs alot of work; things I want to add ASAP.
- [ ] Add any contributions in code (i.e. pilfered code) 
- [ ] Implement Low Battery Warning System - Flashing Icon and Sound
- [ ] Add Licence to each code file
- [ ] Dynamic Button Config - config buttons in config i.e. presses or held, hold time, GPIO pin, associated function (currently shutdown or monitor)
- [ ] Create init.d script to tie into Debians services
- [ ] Integrate Cambles code base into this allowing configuration and use of Cambles SafeShutdown board.
- [ ] Create a Install script
- [ ] Documentation


