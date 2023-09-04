from skyfield.api import load, wgs84
from datetime import datetime, timedelta
from pytz import timezone
import numpy as np
import pandas as pd
import rot2prog
import time
import threading


# Establecemos los parametros del tiempo y del observador
ts = load.timescale()
#t  = ts.tt(2023, 9, 4, 18, 25)
t = ts.now()
Leganes = wgs84.latlon(40.4165, -3.70256, 0)
location1_time = timezone('Europe/Madrid')

# Hacemos una busqueda en celestrak y almacenamos el tle de
# todos los elementos


def get_satellites():
    stations_url = 'http://celestrak.com/NORAD/elements/active.txt'
    satellites = load.tle_file(stations_url)
    sat = get_satellite('NOAA 15', satellites)
    days = t - sat.epoch
    # Esto qes para que no sean muy obsoletas las lineas de tle
    if abs(days) > 7:
        satellites = load.tle_file(stations_url, reload=True)
    return (satellites)


def get_satellite(satelite, satellites):
    by_name = {sat.name: sat for sat in satellites}
    satellite = by_name[satelite]
    return (satellite)


# Tambien establecemos un satelite para que en el caso de que 
# queramos recibir datos de un satelite en espicifico
#  sea de ese
satellite = get_satellite("NOAA 15", get_satellites())

#Creamos una funcion para establecer los nombres de los satelites
def get_list_names():
    satelites = get_satellites()
    nombres = []
    current = 0
    while current < len(satelites):
        nombres.append(satelites[current].name)
        current +=1
    return(nombres)

# funcion que retorna las coordenadas
def get_coordinates():
    difference = satellite - Leganes
    topocentric = difference.at(ts.now())
    alt, az, distance = topocentric.altaz()

    return {"alt": alt.degrees, "az_sat": az.degrees, "dist_sat": distance.km}


def set_satellite(satelite, satellites):
    by_name = {sat.name: sat for sat in satellites}
    satel = by_name[satelite]
    global satellite
    satellite = satel
    print("Satelite establecido")
    print(satellite)

#Definimos un array que me guarde las variables de comienzo y 
# finalizacion de la visiilidad del satelite en los grados
# estalecidos
start_end = []

def get_pases():
    #Primero lo que hacemos es establecer el tiempo de ahora y cargar 
    # los tiempos de vision (>0ºgrados)
    location_time = timezone('Europe/Madrid')
    #hoy = ts.tt(2023, 9, 4, 18, 25)
    hoy = ts.now()
    dt = hoy.astimezone(location_time)
    #print(dt.utc_strftime())
    t1 = dt + timedelta(days=1) #AQUI PUEDO CAMBIAR EL NUMERO DE DIAS
    t, events = satellite.find_events(Leganes, ts.from_datetime(dt), ts.from_datetime(t1), altitude_degrees=0.0)

    datetime_list = []
    pases = []
    start_end.clear()

    #creamos otro array de tiempos para su gestion mas sencilla
    for th in t:
        datetime_list.append(th.astimezone(location_time))

    #Aqui lo que hacemos ees eliminar los tiempos de inicio y finalizado 
    # que nos sobren,los elimino porque para cargar el tiempo tendria 
    # que cargar todo otra vez y es una perdida de recursos
    if events[len(events)-1] == 0 :
        datetime_list.pop()
    elif events[len(events)-1] == 1 :
        datetime_list.pop()
        datetime_list.pop()

    #Si el primer evento es de inicio de vision, entonces cargo los pases 
    # de la manera habitual
    if events[0] == 0:
        for h in range(0,len(datetime_list),3):
            pases.append("EMPIEZA: "+datetime_list[h].strftime('%d/%b/%y %H:%M:%S')+" MÁS ALTO: "+datetime_list[h+1].strftime('%d/%b/%y %H:%M:%S')+" TERMINA: "+datetime_list[h+2].strftime('%d/%b/%y %H:%M:%S'))
            start_end.append({"rising":datetime_list[h],"down":datetime_list[h+2]})

        print("Cargando pases")
        print("\n")
        return (pases)

    #Para el caso de que el primer pase cargado no sea el alcista, inserto 
    # el tiempo actual y, pongo un aviso de que ya empezó
    else:
        if events[0] == 1:
            pases.append("YA HA EMPEZADO -----------> MÁS ALTO: "+datetime_list[0].strftime('%d/%b/%y %H:%M:%S')+" TERMINA: "+datetime_list[1].strftime('%d/%b/%y %H:%M:%S'))
            start_end.append({"rising":dt,"down":datetime_list[1]})
            for h in range(2,len(datetime_list),3):
                pases.append("EMPIEZA: "+datetime_list[h].strftime('%d/%b/%y %H:%M:%S')+" MÁS ALTO: "+datetime_list[h+1].strftime('%d/%b/%y %H:%M:%S')+" TERMINA: "+datetime_list[h+2].strftime('%d/%b/%y %H:%M:%S'))
                start_end.append({"rising":datetime_list[h],"down":datetime_list[h+2]})
            print("Cargando pases")
            print("\n")
            return (pases)
        elif events[0] == 2 :
            pases.append("YA EMPEZÓ -------> MÁS ALTO: YA LLEGÓ -------> TERMINA: "+datetime_list[0].strftime('%d/%b/%y %H:%M:%S'))
            start_end.append({"rising":dt,"down":datetime_list[0]})
            for h in range(1,len(datetime_list),3):
                pases.append("EMPIEZA: "+datetime_list[h].strftime('%d/%b/%y %H:%M:%S')+" MÁS ALTO: "+datetime_list[h+1].strftime('%d/%b/%y %H:%M:%S')+" TERMINA: "+datetime_list[h+2].strftime('%d/%b/%y %H:%M:%S'))
                start_end.append({"rising":datetime_list[h],"down":datetime_list[h+2]})
            print("Cargando pases")
            print("\n")
            return (pases)

def get_mycoordinates(sat):
    satellite1 = get_satellite(sat,get_satellites())
    difference = satellite1 - Leganes
    topocentric = difference.at(ts.from_datetime(ts.now().astimezone(location1_time)))
    alt, az, distance = topocentric.altaz()
    return {"el": alt.degrees, "az": az.degrees, "dist":distance.km}

def get_ID():
  prueba = str(satellite).split("#")
  prueba2 = prueba[1].split()
  print("ID CAMBIADO = "+ prueba2[0])
  return(int(prueba2[0]))

def seguir(end,sat):
    while(1):
        new_az=get_mycoordinates(sat)['az']
        new_el=get_mycoordinates(sat)['el']
        if(new_el<0):
            print("se termino el pase de: ",sat)
            rot2prog.set_pos('0','0')
            break
        else:
            print("actualizando elevacion: "+str(new_el)+"º y azimuth: "+str(new_az)+"º")

            try:
                rot2prog.set_pos(new_az,new_el)
            except:
                print("error al establecer posicion")
            time.sleep(2)

def esperar(start,end,sat):
    while(1):
        if(ts.now().astimezone(location1_time) > start):
            t = threading.Thread(target=seguir,args=(end,sat))
            t.start()
            break


def hilo_espera(pos,sat):
    start = start_end[pos]['rising']
    end = start_end[pos]['down']
    t=threading.Thread(target=esperar,args=(start,end,sat))
    t.start()
    print("se ha creado el hilo con pos: ",pos," y sat: ",sat)



