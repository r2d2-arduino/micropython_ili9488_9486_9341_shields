import machine, os, vfs

sd = machine.SDCard( slot = 2 ) # for Esp32: sck=18, cs=5, miso=19, mosi=23
#sd = machine.SDCard( slot = 2, miso = 13, mosi = 11, sck = 12, cs = 10 ) #for Esp32-s3
#print(sd.info())

vfs.mount( sd, '/sd' ) # mount

print(os.listdir( '/sd' ))    # list directory contents

vfs.umount( '/sd' )    # eject