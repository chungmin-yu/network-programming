from socket import *
import random
import _thread
import threading
import argparse
from select import select

host='127.0.0.1'
defaultport=7980

parser=argparse.ArgumentParser()
parser.add_argument('inputport', nargs='?', default=defaultport)
args = parser.parse_args()

port = int(args.inputport)

serverAddr=(host, port)
account=0
trans=[]
#random.seed()
threadCount=0

#TCP
serverTCP = socket(AF_INET, SOCK_STREAM)
#UDP
#serverUDP = socket(AF_INET, SOCK_DGRAM)

#TCP
serverTCP.bind(serverAddr)
serverTCP.listen(15)
#UDP
#serverUDP.bind(serverAddr)

#print('Waiting for Connection...')

lock=threading.Lock()

def client_tcp(conn, ip, port, usr, trans):
	fd=[conn, ]
	global account
	while True:
		s_input,s_output,s_except = select(fd,[],[])
		Exit=False
		for ss in s_input:
			#TCP
			if ss == conn:
				data=conn.recv(2048)
				if not data:
					Exit=True
					break
				msg = str(data, encoding='utf-8')
				#print(msg)
				column=msg.split()
				if column[0] == 'withdraw':
					moneyout = int(column[1])
					with lock:
						
						if moneyout > account:
							res='Withdraw excess money from the account.'
						else:
							account-=moneyout
							res='Successfully withdraw '+str(moneyout)+' from the account.'
							temp1='user'+usr+' withdraws '+str(moneyout)+' from the account.\nRemaining Amount: '+str(account)+'\n'
							trans.append(temp1)
						conn.send(res.encode())

				elif column[0] == 'deposit':
					moneyin = int(column[1])
					with lock:						
						account+=moneyin
						res='Successfully deposit '+str(moneyin)+' into the account.'
						temp2='user'+usr+' deposits '+str(moneyin)+' into the account.\nRemaining Amount: '+str(account)+'\n'
						trans.append(temp2)					
						conn.send(res.encode())

				elif column[0] == 'show-account':
					with lock:
						res ='There is '+ str(account)+' in the account.'
						conn.send(res.encode())
				elif column[0] == 'record-account':
					with lock:
						res=''
						for m in trans:
							res+=m
						conn.send(res.encode())

				elif column[0] == 'exit':
					print('User '+usr+' '+ip+':'+port+' disconnected.')				
					Exit=True
					break

			
		if Exit:
			break
	conn.close()







while True:	
	threadCount +=1	
	client, address=serverTCP.accept()			
	print('New connection from ' + str(address[0]) + ' : ' + str(address[1]) +' user'+str(threadCount))
	_thread.start_new_thread(client_tcp, (client, str(address[0]), str(address[1]), str(threadCount), trans))
	#print('Thread number '+ str(threadCount) + ' is executed.')
serverTCP.close()



	

