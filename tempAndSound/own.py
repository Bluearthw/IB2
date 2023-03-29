import math #to calculate
import mysql.connector  # connect to mysql
import datetime  # get the present time
from gpiozero import MCP3008  #to measure
from time import sleep # to wait
import pygame # to play music


############################ pygame ##################################
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)  # preset the mixer init arguments, set the value first then initialize
pygame.mixer.init()  # initialize the mixer module

speaker_volume = 0.5  # set volume
pygame.mixer.music.set_volume(speaker_volume)

lst = ["/home/student/Kinderliedjes/Baa.mp3",
       "/home/student/Kinderliedjes/Slaap.mp3",
       "/home/student/Kinderliedjes/Sleep.mp3"]  # music address

inp = 0
song = lst[inp]
pygame.mixer.music.load(song)

checktime = 10  # how long the song play
pygame.mixer.music.pause()

############### temp and sound ################################
temp = MCP3008(channel=0)
sound = MCP3008(channel=1)
# tempTest = MCP3008(channel=2)

################### database ##############################
mydb = mysql.connector.connect(
    host="mysql.studev.groept.be",
    user="a22ib2b05",
    password="secret",
    database="a22ib2b05"
)
IndexInTheTable = 1  # start from 1
tableClear = False
mycursor = mydb.cursor()
mycursor.execute("truncate table Data_rPi")  # clear the table

sqlInsert = "INSERT INTO Data_rPi (measurement, temperature, dBlevel, timeStamp) VALUES (%s, %s,%s,%s)"

##The queries
queryMusicStart = "select BabyCrySong from BabyCry order by idBabyCry desc limit 1"
querySong = "select WhatLullaby from UILullaby order by Lullaby desc limit 1"
queryOnOff = "select AanUitcol from AanUit order by idClick desc limit 1"
queryDBLevel = "select dBLevel from dBLevel order by iddBLevel desc limit 1"

########################while true###############################

while True:
    ##keep getting data
    mycursor = mydb.cursor()
    mycursor.execute(queryOnOff)
    for AanUitcol in mycursor:
        isOn = AanUitcol[0]

    # mycursor.execute(queryDBLevel)
    # for dBLevel in mycursor:
    #     threshold = dBLevel[0]
    ##
    if isOn == 1:  # start or not
        ##clear table first
        if tableClear:
            mycursor.execute("truncate table Data_rPi")  # clear the table
            tableClear = False
        ##measuring
        temperature = round(temp.value * 75 - 22.1, 2)
        decibel = round(math.log(sound.value * 100) * 10.601 + 76.694, 1)

        print('The temperature is', temperature, "°C")
        print('The sound level is', decibel, 'dB')

        ##getting the time
        now = datetime.datetime.now()
        current = now.strftime("%H:%M:%S")
        ##inset the value
        val = (IndexInTheTable, temperature, decibel, current)
        IndexInTheTable += 1
        mycursor.execute(sqlInsert, val)
        mydb.commit()
        sleep(1)

        ##get threshole
        mycursor.execute(queryDBLevel)
        for dBLevel in mycursor:
            threshold = dBLevel[0]

        ##every check time
        if IndexInTheTable % checktime == 0:  # every 10 second we check whether the baby is still crying

            ##get baby crying or not
            mycursor.execute(queryMusicStart)
            for avg in mycursor:
                dbGet = avg[0]

            if dbGet == 1:  ## if baby cry
                if not pygame.mixer.music.get_busy():
                    ## which song
                    mycursor.execute(querySong)
                    for lul in mycursor:
                        getlul = lul[0]
                    song = lst[getlul - 1]
                    pygame.mixer.music.load(song)
                    pygame.mixer.music.play(-1)  # play forever

            else:
                pygame.mixer.music.pause()
    else:
        print("off")
        sleep(1)
        pygame.mixer.music.pause()
        tableClear = True
        IndexInTheTable = 1
