from socket import *
import argparse
import sys

host=sys.argv[1]
port=int(sys.argv[2])
clientAddr=(host, port)

'''
defaultport=7980
parser = argparse.ArgumentParser()
parser.add_argument('inputhost')
parser.add_argument('inputport', nargs='?', default=defaultport)
args = parser.parse_args()
host = args.inputhost
port = int(args.inputport)
'''

#TCP
#clientTCP = socket(AF_INET, SOCK_STREAM)
#UDP
clientUDP = socket(AF_INET, SOCK_DGRAM)

#TCP connect
#clientTCP.connect(clientAddr)


while True:
	cmd=input('% ')
	column=cmd.split()

	#UDP
	if column[0] == 'get-file-list':
		clientUDP.sendto(cmd.encode(), clientAddr)
		data, addr = clientUDP.recvfrom(8192)
		msg = str(data, encoding='utf-8')
		print(msg)
		continue
		
	elif column[0] == 'get-file':
		clientUDP.sendto(cmd.encode(), clientAddr)
		for i in range(1,len(column)):
			data, addr = clientUDP.recvfrom(8192)
			msg = str(data, encoding='utf-8')
			print(msg)
			with open(column[i],'w') as f:
				f.write(msg)		
		continue


	elif column[0] == 'exit':
		break
	else:
		print('Please retry.')







