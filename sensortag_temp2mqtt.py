#!/usr/bin/env python
#See Readme for details


import pexpect
import sys
import time
import mosquitto
import ConfigParser
bluetooth_adr = sys.argv[1]

config_file = "temp2mqtt.ini"

if __name__ == "__main__":
    try:
        config = ConfigParser.ConfigParser()
        config.readfp(open(config_file, "r"))
    except IOError as e:
        print e
        sys.exit(1)

    try:
        host = config.get("MQTT", "host") 
    except ConfigParser.NoOptionError:
        host = os.getenv("MQTT_BROKER", "localhost")
    try:
        port = config.getint("MQTT", "port") 
    except ConfigParser.NoOptionError:
        port = int(os.getenv("MQTT_BROKER", "1883"))
    try:
        prefix = config.get("MQTT", "prefix") 
    except ConfigParser.NoOptionError:
        prefix = "temperature"



def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t


# This algorithm borrowed from 
# http://processors.wiki.ti.com/index.php/SensorTag_User_Guide#Gatt_Server
# which most likely took it from the datasheet.  I've not checked it, other
# than noted that the temperature values I got seemed reasonable.
#
def calcTmpTarget(objT, ambT):
    m_tmpAmb = ambT/128.0
    Vobj2 = objT * 0.00000015625
    Tdie2 = m_tmpAmb + 273.15
    S0 = 6.4E-14            # Calibration factor
    a1 = 1.75E-3
    a2 = -1.678E-5
    b0 = -2.94E-5
    b1 = -5.7E-7
    b2 = 4.63E-9
    c2 = 13.4
    Tref = 298.15
    S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
    Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
    fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
    tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
    tObj = (tObj - 273.15)
    return "%.2f" % tObj

## Here is where it starts
#
tool = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' --interactive')
tool.expect('.*\[LE\]>', timeout=600)
print "Preparing to connect. You might need to press the side button..."
tool.sendline('connect')
# test for success of connect
# tool.expect('\[CON\].*>')
# Alternative test for success of connect
tool.expect('Connection successful.*\[LE\]>')
tool.sendline('char-write-cmd 0x29 01')
tool.expect('\[LE\]>')
# Initialize mqtt
topic = prefix + bluetooth_adr +"/celsius"
mqtt = mosquitto.Mosquitto()
mqtt.connect(host, port)
mqtt.loop_start()
# Loop forever and read sensor tag each iteration.
# The result is published to mqtt
while True:
    tool.sendline('char-read-hnd 0x25')
    tool.expect('descriptor: .*') 
    rval = tool.after.split()
    objT = floatfromhex(rval[2] + rval[1])
    ambT = floatfromhex(rval[4] + rval[3])
    #print rval
    payload = calcTmpTarget(objT, ambT)
    # publish to mqtt
    print topic, payload
    mqtt.publish(topic, payload, qos=0, retain=False)
    # sleep five seconds
    time.sleep(5)
# close mqtt
mqtt.loop_stop()
mqtt.disconnect()



