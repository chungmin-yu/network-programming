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
account1=0
account2=0
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

def client_tcp(conn, ip, port, usr):
	fd=[conn, ]
	global account1
	global account2
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
					which, moneyout = column[1], int(column[2])
					with lock:
						if which == 'ACCOUNT1':
							if moneyout > account1:
								res='Withdraw excess money from accounts.'
							else:
								account1=moneyout
								res='Successfully withdraws '+str(moneyout)+' from ACCOUNT1.'
						elif which == 'ACCOUNT2':
							if moneyout > account2:
								res='Withdraw excess money from accounts.'
							else:
								account2=moneyout
								res='Successfully withdraws '+str(moneyout)+' from ACCOUNT2.'
						
						conn.send(res.encode())

				elif column[0] == 'deposit':
					which2, moneyin = column[1], int(column[2])
					with lock:
						if which2 == 'ACCOUNT1':
							account1=moneyin
							res='Successfully deposits '+str(moneyin)+' into ACCOUNT1.'
						elif which2 == 'ACCOUNT2':
							account2=moneyin
							res='Successfully deposits '+str(moneyin)+' into ACCOUNT2.'
						
						conn.send(res.encode())

				elif column[0] == 'show-accounts':
					with lock:
						res =''
						res += ('ACCOUNT1: '+ str(account1) + '\n')
						res += ('ACCOUNT2: '+ str(account2) )

						conn.send(res.encode())

				elif column[0] == 'exit':
					print(ip+':'+port+' disconnected '+usr)				
					Exit=True
					break

			
		if Exit:
			break
	conn.close()







while True:	
	threadCount +=1	
	Name=''	
	if threadCount == 1:
		Name='userA'
	elif threadCount == 2:
		Name='userB'
	elif threadCount == 3:
		Name='userC'
	elif threadCount == 4:
		Name='userD'
	if threadCount < 5:	
		client, address=serverTCP.accept()			
		print('New connection from ' + str(address[0]) + ' : ' + str(address[1]) + ' '+Name)
		client.send(str.encode('success'))
		_thread.start_new_thread(client_tcp, (client, str(address[0]), str(address[1]), Name))
	else: 
		client, address=serverTCP.accept()
		print('exceed maximum')
		client.send(str.encode('exceed maximum'))
		client.close()
	#print('Thread number '+ str(threadCount) + ' is executed.')
serverTCP.close()



	

