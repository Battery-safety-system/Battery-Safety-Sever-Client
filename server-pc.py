#!/usr/bin/python3
import time
import os
import csv
import pickle
import socket
###
path= os.getcwd();
ip_addr='192.168.137.1'
#### get current time and put the current to the floder name
# file system: 
# Battery-System-database
#   --current1(Battery-System %m-%Y)
#       --summary floder
#       --voltage floder
#   --current2
#   --current3 
#       --
# create the floder
current=time.strftime('Battery-System %m-%Y')
if(not os.path.isdir(path+"/"+"Battery-System-database")):
    os.mkdir(path+"/"+"Battery-System-database")
floder=path+"/"+"Battery-System-database"+"/"+current
if (not os.path.isdir(floder)):
    os.mkdir(floder)
summary_floder=path+"/"+"Battery-System-database"+"/"+current+"/summary floder"
voltage_floder=path+"/"+"Battery-System-database"+"/"+current+"/voltage_floder"
if(not os.path.isdir(summary_floder)):
    os.mkdir(summary_floder)

if(not os.path.isdir(voltage_floder)):
    os.mkdir(voltage_floder)

###
file="log"+time.strftime('-Battery-System %d-%m-%Y')+"-"+time.strftime('%H-%M-%S')+".csv"
day=time.strftime('%d')
### there is several global variable we need to consider: 
# summary_floder, voltage_floder, floder(current), file(day)
# enum： summary info -1, voltage info -2, 
  ## CVS writting function
def WritetoCVS(list_vol_temp, type):
    
    current_month=time.strftime('Battery-System %m-%Y')
    global current
    global floder
    global file
    global day
    global summary_floder
    global voltage_floder
    # update the floder, current, day, file, 
    if(current_month!=current):
        current=current_month
        floder=path+"/"+"Battery-System-database"+"/"+current
        os.mkdir(floder)
        summary_floder=floder+"/summary floder"
        voltage_floder=floder+"/voltage_floder"
        os.mkdir(summary_floder)
        os.mkdir(voltage_floder)
    current_day=time.strftime('%d')
    if(current_day!=day):
        day=current_day
        file="log"+time.strftime('-Battery-System %d-%m-%Y')+"-"+time.strftime('%H-%M-%S')+".csv"
    
    ### write the file 
    if(type==1):
        if(not os.path.isfile(summary_floder+"/"+file)):
            summary_head=["date" , "time", "battery1-temp","battery1-voltage", "battery2-temp","battery2-voltage", "temperature-high", "voltage-limit"]
            with open(summary_floder+"/"+file,'a',newline='') as csvfile:
                writer1=csv.writer(csvfile)
                writer1.writerow(summary_head)
        with open(summary_floder+"/"+file,'a',newline='') as csvfile:
            writer1=csv.writer(csvfile)
            date1= time.strftime('%d-%m-%Y')
            time1= time.strftime('%H:%M:%S')
            list_vol_temp.insert(0,time1)
            list_vol_temp.insert(0,date1)
            print(list_vol_temp)
            writer1.writerow(list_vol_temp)
    elif(type==2):
        if(not os.path.isfile(voltage_floder+"/"+file)):
            voltage_head=["date" , "time", "battery1-voltage1","battery1-voltage2","battery1-voltage3","battery1-voltage4","battery1-voltage5","battery1-voltage6","battery1-voltage7","battery1-voltage8","battery1-voltage9", "battery1-voltage10","battery1-voltage11","battery1-voltage12","battery2-voltage1","battery2-voltage2","battery2-voltage3","battery2-voltage4","battery2-voltage5","battery2-voltage6","battery2-voltage7","battery2-voltage8","battery2-voltage9","battery2-voltage10","battery2-voltage11","battery2-voltage12"]
            with open(voltage_floder+"/"+file,'a',newline='') as csvfile:
                writer1=csv.writer(csvfile)
                writer1.writerow(voltage_head)
        with open(voltage_floder+"/"+file,'a',newline='') as csvfile:
            writer=csv.writer(csvfile)
            date1= time.strftime('%d-%m-%Y')
            time1= time.strftime('%H:%M:%S')
            list_vol_temp.insert(0,time1)
            list_vol_temp.insert(0,date1)
            writer.writerow(list_vol_temp)




# create the socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket and the ip is the server ip and port is 6688
server.bind((ip_addr, 6689))
# start to listen
server.listen(5)

print(u'waiting for connect...')
# wiat to connect a
connect, (host, port) = server.accept()
connect.settimeout(5) 
print(u'the client %s:%s has connected.' % (host, port))


if __name__ == '__main__':
    while True: 
        try: 

            cvs_list = pickle.loads(connect.recv(3072))
            print("battery1-temp: "+str(cvs_list[0])+", battery1-voltage: "+str(cvs_list[1]))
            print("battery2-temp: "+str(cvs_list[2])+", battery2-voltage: "+str(cvs_list[3]))
            str1="status: Pump is "
            if(cvs_list[4]==True):
                str1+="on"
            else:
                str1+="off"
            str1+=" Relay is "
            if(cvs_list[5]==True):
                str1+="off"
            else :
                str1+="on"
            print(str1)


            connect.sendall(b'your words has received.')
            voltage_list= pickle.loads(connect.recv(3072))

            connect.sendall(b'your words has received.')


            WritetoCVS(cvs_list, type=1);
            WritetoCVS(voltage_list, type=2);
            print("finish")
        except Exception as e:
            print(e)
            print("try reconnecting!! wait ")
            while(True):
                try:
                                # create the socket
                    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket and the ip is the server ip and port is 6688
                    server.bind((ip_addr, 6689))
# start to listen
                    server.listen(5)
                    print(u'waiting for connect...')
# wiat to connect a
                    connect, (host, port) = server.accept()
                    connect.settimeout(5) 
                    print(u'the client %s:%s has connected.' % (host, port))
                    break;
                except Exception as e:
                    print(e)
                    






