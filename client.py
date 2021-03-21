from socket import *
import argparse
import sys
from select import select

#host='127.0.0.1'
defaultport=7980

parser = argparse.ArgumentParser()
parser.add_argument('inputhost')
parser.add_argument('inputport', nargs='?', default=defaultport)
args = parser.parse_args()

host = args.inputhost
port = int(args.inputport)

clientAddr=(host, port)
ID=0
User=''
attach=False
join=False
restart=False
chatroom_port=0


#TCP
clientTCP = socket(AF_INET, SOCK_STREAM)
#UDP
clientUDP = socket(AF_INET, SOCK_DGRAM)

#attachfd=clientTCP

#TCP connect
clientTCP.connect(clientAddr)

print("********************************")
print("** Welcome to the BBS server. **")
print("********************************")

def doChatroom(clientTCP, cport, owner):
	chatroom_status=1
	global join
	global attach
	global restart
	global attachfd
	global User

	if join:
		clientChatroom = socket(AF_INET, SOCK_STREAM)
		clientChatroom.connect((host, cport))
		clientChatroom.send(str.encode("join "+User))
	elif restart:
		clientChatroom = socket(AF_INET, SOCK_STREAM)
		clientChatroom.connect((host, cport))
		clientChatroom.send(str.encode("restart "+User))
	elif attach:
		clientChatroom = attachfd
		clientChatroom.send(str.encode("attach "+User))
	else: 
		#create
		clientChatroom = socket(AF_INET, SOCK_STREAM)
		clientChatroom.connect((host, cport))

	leave = False
	while True:
		if leave:
			break
		chatroomlist = [sys.stdin, clientChatroom]
		read_sockets, write_sockets, error_sockets = select(chatroomlist,[],[])  
		for sock in read_sockets:  
			if sock == clientChatroom:  
				message = sock.recv(8192).decode('utf-8')
				print(message)  
				close=message.split()
				if close[-1] == 'close.':
					leave=True
					break
			else:  
				Input = input()
				Buff = Input+' '+User
				clientChatroom.send(str.encode(Buff))
				if Input == 'leave-chatroom':
					chatroom_status = 0
					leave=True
				elif Input == 'detach':	
					if owner == User:			
						attachfd = clientChatroom
						leave=True
					else:
						clientChatroom.send(str.encode(Buff))
	if owner == User:
		if chatroom_status == 0:		
			leavemsg='leave-chatroom ' + User
			clientTCP.send(leavemsg.encode())




while True:
	cmd=input('% ')
	column=cmd.split()

	#hw1
	#UDP
	if column[0] == 'register':
		if len(column) != 4:
			print('Usage: register <username> <email> <password>')
			continue
		else:
			clientTCP.send(cmd.encode())
			data= clientTCP.recv(8192)
			#clientUDP.sendto(cmd.encode('utf-8'), clientAddr)
			#data, addr = clientUDP.recvfrom(2048)
			#msg = data.decode('utf-8')
			msg = str(data, encoding='utf-8')
			print(msg)
			continue
	elif column[0] == 'whoami':
		buff = cmd + ' ' + str(ID)
		clientTCP.send(buff.encode())
		data= clientTCP.recv(8192)
		#clientUDP.sendto(buff.encode(), clientAddr)
		#data, addr = clientUDP.recvfrom(2048)
		msg = str(data, encoding='utf-8')
		print(msg)
		continue

	#TCP
	elif column[0] == 'login':
		if len(column) != 3:
			print('Usage: login <username> <password>')
			continue
		else:
			if ID != 0:
				print('Please logout first')
				continue
			else:
				clientTCP.send(cmd.encode())					
				data= clientTCP.recv(8192)
				msg = str(data, encoding='utf-8')
				if msg[0] == 'L':
					print(msg)
				else:
					temp=msg.split()
					ID=int(temp[2])
					chatroom_port=int(temp[3])
					User=temp[1][:-1]
					print(temp[0] + ' ' + temp[1])
					
				continue
	elif column[0] == 'logout':
		buff = cmd + ' ' + str(ID)
		clientTCP.send(buff.encode())
		data = clientTCP.recv(8192)
		msg = str(data, encoding='utf-8')
		if msg[0] == 'B':
			ID=0
			User=''
		print(msg)
		continue

	elif column[0] == 'list-user':
		clientTCP.send(cmd.encode())
		data = clientTCP.recv(8192)
		msg = str(data, encoding='utf-8')
		print(msg,end='')
		continue

	#hw2
	elif column[0] == 'create-board':
		if ID == 0:
			print('Please login first.')
			continue
		else:
			if len(column) != 2:
				print('Usage: create-board <name>')
				continue
			else:
				buff = cmd + ' ' + User
				clientTCP.sendall(buff.encode())
				data= clientTCP.recv(8192)
				msg = str(data, encoding='utf-8')
				print(msg)
		continue
		
	elif column[0] == 'create-post':
		if ID == 0:
			print('Please login first.')
			continue
		else:
			t = cmd.find('--title')
			c = cmd.find('--content')
			if t==-1 or c==-1:
				print('Usage: create-post <board-name> --title <title> --content <content>')
				continue
			elif column[2]!='--title':
				print('Usage: create-post <board-name> --title <title> --content <content>')
				continue
			else:			
				temp = 'create-post ' + User
				buff = cmd.replace('create-post', temp)
				clientTCP.send(buff.encode())
				data= clientTCP.recv(8192)
				msg = str(data, encoding='utf-8')
				print(msg)
		continue
		
	elif column[0] == 'list-board':
		clientTCP.send(cmd.encode())
		data= clientTCP.recv(8192)
		msg = str(data, encoding='utf-8')
		print(msg,end='')
		continue
		
	elif column[0] == 'list-post':
		if len(column) != 2:
			print('Usage: list-post <board-name>')
			continue
		else:
			clientTCP.send(cmd.encode())
			data= clientTCP.recv(8192)
			msg = str(data, encoding='utf-8')
			if msg[0]=='B':
				print(msg)
			else:
				print(msg,end='')
		continue
		
	elif column[0] == 'read':
		if len(column) != 2:
			print('Usage: read <post-S/N>')
			continue
		else:
			clientTCP.send(cmd.encode())
			data= clientTCP.recv(8192)
			msg = str(data, encoding='utf-8')
			if msg[0]=='P':
				print(msg)
			else:
				print(msg,end='')
		continue
	elif column[0] == 'delete-post':
		if ID == 0:
			print('Please login first.')
			continue
		else:
			if len(column) != 2:
				print('Usage: delete-post <post-S/N>')
				continue
			else:
				buff = cmd + ' ' + User 
				clientTCP.send(buff.encode())
				data= clientTCP.recv(8192)
				msg = str(data, encoding='utf-8')
				print(msg)
		continue
	elif column[0] == 'update-post':
		if ID == 0:
			print('Please login first.')
			continue
		else:
			if column[2]!='--title' and column[2]!='--content':
				print('Usage: update-post <post-S/N> --title/content <new>')
				continue
			else:
				temp ='update-post ' + User
				buff = cmd.replace('update-post',temp)
				clientTCP.send(buff.encode())
				data= clientTCP.recv(8192)
				msg = str(data, encoding='utf-8')
				print(msg)
		continue
	elif column[0] == 'comment':
		if ID == 0:
			print('Please login first.')
			continue
		else:
			if len(column) < 3:
				print('Usage: comment <post-S/N> <comment>')
				continue
			else:
				temp = 'comment ' + User
				buff = cmd.replace('comment', temp)
				clientTCP.send(buff.encode())
				data= clientTCP.recv(8192)
				msg = str(data, encoding='utf-8')
				print(msg)
		continue

	#hw3
	elif column[0] == 'list-chatroom':
		if ID == 0:
			print('Please login first.')
			continue
		else:
			clientUDP.sendto(cmd.encode(), clientAddr)
			data, addr = clientUDP.recvfrom(8192)
			msg = str(data, encoding='utf-8')
			print(msg,end='')
		continue

	elif column[0] == 'create-chatroom':
		if len(column) == 1:
			print('Usage: create-chatroom <port>')
			continue
		if ID == 0:
			print('Please login first.')
			continue
		else:
			buff = cmd +' '+ User
			clientTCP.send(buff.encode())
			data= clientTCP.recv(8192)
			msg = str(data, encoding='utf-8')			
			if msg[0] == 'U':
					print(msg)
			else:
				print("start to create chatroom…")
				print("********************************")
				print("**Welcome to the chatroom**")
				print("********************************")
				chatroom_port=int(msg)
				doChatroom(clientTCP, int(msg), User)
				print('Welcome back to BBS.')
		continue	

	elif column[0] == 'join-chatroom':
		if len(column) == 1:
			print('Usage: join-chatroom <chatroom_name>')
			continue
		if ID == 0:
			print('Please login first.')
			continue
		else:
			clientTCP.send(cmd.encode())
			data= clientTCP.recv(8192)
			msg = str(data, encoding='utf-8')
			if msg[0] == 'T':
				print(msg)
			else:
				join=True
				print("********************************")
				print("**Welcome to the chatroom**")
				print("********************************")
				doChatroom(clientTCP, int(msg), column[1])
				print('Welcome back to BBS.')
				join=False

		continue

	elif column[0] == 'attach':
		if ID == 0:
			print('Please login first.')
			continue
		else:			
			if chatroom_port == 0:
				print("Please create-chatroom first.")
			else:
				attach=True
				print("********************************")
				print("**Welcome to the chatroom**")
				print("********************************")
				doChatroom(clientTCP, chatroom_port, User)
				print('Welcome back to BBS.')
				attach=False

		continue

	elif column[0] == 'restart-chatroom':
		if ID == 0:
			print('Please login first.')
			continue
		else:
			buff = cmd +' '+ User
			clientTCP.send(buff.encode())
			data= clientTCP.recv(8192)
			msg = str(data, encoding='utf-8')
			if msg[0] == 'P' or msg[0] == 'Y':
				print(msg)
			else:
				restart=True
				print("start to create chatroom…")
				print("********************************")
				print("**Welcome to the chatroom**")
				print("********************************")
				chatroom_port=int(msg)
				doChatroom(clientTCP, int(msg), User)
				print('Welcome back to BBS.')
				restart=False

		continue


	elif column[0] == 'exit':
		if ID != 0:
			print('Please logout first.')
			continue
		else:
			clientTCP.send(cmd.encode())
			break
	else:
		print('Please retry.')







