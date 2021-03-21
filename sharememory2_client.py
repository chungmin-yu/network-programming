from socket import *
import argparse

#host='127.0.0.1'
defaultport=7980

parser = argparse.ArgumentParser()
parser.add_argument('inputhost')
parser.add_argument('inputport', nargs='?', default=defaultport)
args = parser.parse_args()

host = args.inputhost
port = int(args.inputport)

clientAddr=(host, port)
#ID=0

#TCP
clientTCP = socket(AF_INET, SOCK_STREAM)
#UDP
clientUDP = socket(AF_INET, SOCK_DGRAM)

#TCP connect
clientTCP.connect(clientAddr)

print("********************************")
print("Welcome to the account server.")
print("********************************")

while True:
	cmd=input()
	column=cmd.split()

	#TCP
	if column[0] == 'withdraw':
		if len(column)!=2:
			print('Usage: withdraw <money>')
			continue
		elif int(column[1]) <= 0:
			print('Withdraw a non-positive number into accounts.')
			continue		
		else:		
			clientTCP.send(cmd.encode())
			data= clientTCP.recv(8192)
			msg = str(data, encoding='utf-8')
			print(msg)				
			continue
	elif column[0] == 'deposit':
		if len(column)!=2:
			print('Usage: deposit <money>')
			continue
		elif int(column[1]) <= 0:
			print('Deposit a non-positive number into accounts.')
			continue		
		else:		
			clientTCP.send(cmd.encode())
			data= clientTCP.recv(8192)
			msg = str(data, encoding='utf-8')
			print(msg)				
			continue
	elif column[0] == 'show-account':
		clientTCP.send(cmd.encode())
		data= clientTCP.recv(8192)
		msg = str(data, encoding='utf-8')
		print(msg)				
		continue
	elif column[0] == 'record-account':
		clientTCP.send(cmd.encode())
		data= clientTCP.recv(8192)
		msg = str(data, encoding='utf-8')
		print(msg,end='')				
		continue
	elif column[0] == 'exit':
		clientTCP.send(cmd.encode())
		break
	else:
		print('Please retry.')







