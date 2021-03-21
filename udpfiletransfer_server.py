from socket import *
import random
import _thread
import threading
import argparse
import sys
import os
from select import select

host='127.0.0.1'
port=int(sys.argv[1])
serverAddr=(host, port)

'''
host='127.0.0.1'
defaultport=7980
parser=argparse.ArgumentParser()
parser.add_argument('inputport', nargs='?', default=defaultport)
args = parser.parse_args()
port = int(args.inputport)
'''


#TCP
#serverTCP = socket(AF_INET, SOCK_STREAM)
#UDP
serverUDP = socket(AF_INET, SOCK_DGRAM)

#TCP
#serverTCP.bind(serverAddr)
#serverTCP.listen(15)
#UDP
serverUDP.bind(serverAddr)

print('Waiting for Connection...')



#client, address=serverTCP.accept()	
fd=[serverUDP,]
while True:
	s_input,s_output,s_except = select(fd,[],[])
	for ss in s_input:
		#UDP
		if ss == serverUDP:
			data, addr = serverUDP.recvfrom(8192)
			msg = str(data, encoding='utf-8')
			print(msg)
			column=msg.split()

			if column[0] == 'get-file-list':
				filelist = os.listdir('.')
				res=''
				for ls in filelist:
					res +=(ls+' ')
				serverUDP.sendto(res.encode(), (addr[0],addr[1]) )							
			elif column[0] == 'get-file':
				for i in range(1,len(column)):
					file = column[i]
					with open(file,'r') as f:
						text=f.read()
						print(text)
					serverUDP.sendto(text.encode(), (addr[0],addr[1]) )
	
serverUDP.close()



	

