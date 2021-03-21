from socket import *
import random
from _thread import *
import threading
from signal import signal, SIGINT
import sys
from select import select
import datetime
import argparse

host='127.0.0.1'
defaultport=7980

parser=argparse.ArgumentParser()
parser.add_argument('inputport', nargs='?', default=defaultport)
args = parser.parse_args()

port = int(args.inputport)

serverAddr=(host, port)
userInfo={}
board={}
chatroom={}
SN=0
#{name:[index,moderator,{S/N:[title,content,author,date,[user+comment] ]}}
random.seed()
threadCount=0

#TCP
serverTCP = socket(AF_INET, SOCK_STREAM)
#UDP
serverUDP = socket(AF_INET, SOCK_DGRAM)

#TCP
serverTCP.bind(serverAddr)
serverTCP.listen(15)
#UDP
serverUDP.bind(serverAddr)

print('Waiting for Connection...')

lock=threading.Lock()

def gettime():
	todaytime = str(datetime.datetime.today())
	today = todaytime.split()
	tt = today[1].split(':')
	time = tt[0] + ':' + tt[1]
	return time

def chatroom_thread(server, owner, connlist, chatting):
	detach=False
	while True:
		read_sockets, write_sockets, error_sockets = select(connlist,[],[])
		for sock in read_sockets:
			if sock == server:
				chatconn, chataddr = server.accept()
				connlist.append(chatconn)
				print (str(chataddr[1]) + " connected.")
				#join and restart
				tempchat=''
				if len(chatting)>=3:
					tempchat+=(chatting[-3]+'\n'+chatting[-2]+'\n'+chatting[-1])
					#chatconn.send(str.encode(tempchat))
				else:
					for i in range(len(chatting)):
						tempchat+=(chatting[i]+'\n')
				chatconn.send(str.encode(tempchat))

			else:
				#chatconn.send(str.encode("Welcome to this chatroom!"))
				#while True:  
				try:  
					temp = sock.recv(8192).decode('utf-8')					
					temp2=temp.split()
					user=temp2[-1]
					message=' '.join(temp2[:-1])
					print("user <" + user + ">: " + temp)
					print("chat:["+message+"]")
					print(detach)
					
					if message != 'join' and message != 'restart' and message != 'attach' and message != 'detach' and message != 'leave-chatroom':
						message_to_send = user + "[" + gettime() + "]: " + message  
						chatting.append(message_to_send)						                
						for clients in connlist:  
							try:
								if clients != server and clients != sock:    
									if detach:
										if clients != owner:
											clients.send(str.encode(message_to_send))
									else:
										clients.send(str.encode(message_to_send))
							except:  
								clients.close() 
								connlist.remove(clients)


					elif message == 'join':
						for clients in connlist:  
							if clients != server and clients != sock:  
								if detach:
									if clients != owner:
										message_to_send = "sys[" + gettime() + "]: " + user + " join us."
										clients.send(str.encode(message_to_send))
								else:
									message_to_send = "sys[" + gettime() + "]: " + user + " join us."
									clients.send(str.encode(message_to_send))

					elif message == 'restart':
						owner=sock						

					elif message == 'attach':
						detach=False
						tempchat=''
						if len(chatting)>=3:
							tempchat=chatting[-3]+'\n'+chatting[-2]+'\n'+chatting[-1]
							#sock.send(str.encode(tempchat))
						else:
							for i in range(len(chatting)):
								tempchat+=(chatting[i]+'\n')
						sock.send(str.encode(tempchat))

					elif message == 'detach':
						if sock == owner:
							detach=True
						else:
							message_to_send = user + "[" + gettime() + "]: " + message  
							chatting.append(message_to_send)						                
							for clients in connlist:  
								if clients != server and clients != sock:    
									if detach:
										if clients != owner:
											clients.send(str.encode(message_to_send))
									else:
										clients.send(str.encode(message_to_send))


					elif message == 'leave-chatroom':
						if sock == owner:
							for clients in connlist:
								if clients != server and clients != sock: 
									#sys
									message_to_send = "sys[" + gettime() + "]: the chatroom is close."
									clients.send(str.encode(message_to_send))
							#detach=True
							connlist.clear()
							connlist.append(server)
							#connlist.append(owner)
						else:
							connlist.remove(sock)
							for clients in connlist:  
								if clients != server and clients != sock:  
									if detach:
										if clients != owner:
											message_to_send = "sys[" + gettime() + "]: " + user +" leave us."
											clients.send(str.encode(message_to_send))
									else:
										message_to_send = "sys[" + gettime() + "]: " + user +" leave us."
										clients.send(str.encode(message_to_send))


				except Exception as e: 
					print(e) 


def client_threadTCP(host, conn, addr, userInfo, board, chatroom):
	while True:
	
		#TCP	
		data=conn.recv(8192)
		if not data:
			break
		msg = str(data, encoding='utf-8')
		print(msg)
		column=msg.split()
		#hw1

		if column[0] == 'register':
			username, email, password = column[1], column[2], column[3]
			with lock:
				if username in userInfo:
					res = 'Username is already used'
				else:
					userInfo.update({username:[email,password,[]]})
					res = 'Register successfully.'
			conn.send(res.encode())			
					
		elif column[0] == 'whoami':
			whoID = int(column[1])
			with lock:
				whoState=False
				for whoUser in userInfo:
					if whoID in userInfo[whoUser][2]:
						res = whoUser
						whoState=True
						break
				if not whoState:
					res='Please login first'
			conn.send(res.encode())	

		elif column[0] == 'login':
			loginUser, loginPassword = column[1], column[2]
			with lock:
				if loginUser not in userInfo:
					res = 'Login failed.'
				else:
					if loginPassword != userInfo[loginUser][1]:
						res = 'Login failed.'	
					else:
						ID = random.randint(1,1000000000)
						userInfo[loginUser][2].append(ID)
						if loginUser in chatroom:
							userport=chatroom[loginUser][1]
						else:
							userport=0
						res = 'Welcome, '+ loginUser +'. '+str(ID)+' '+str(userport)
			conn.send(res.encode())			

		elif column[0] == 'logout':
			logoutID = int(column[1])
			with lock:
				logoutState=False
				for logoutUser in userInfo:
					if logoutID in userInfo[logoutUser][2]:					
						logoutState=True
						if logoutUser in chatroom:
							if chatroom[logoutUser][0]=='open':
								res = 'Please do “attach” and “leave-chatroom” first.'
							else:
								userInfo[logoutUser][2].remove(logoutID)
								res = 'Bye, '+ logoutUser +'.'
						else:
							userInfo[logoutUser][2].remove(logoutID)
							res = 'Bye, '+ logoutUser +'.'
						break

				if not logoutState:
					res = 'Please login first'
			conn.send(res.encode())

		elif column[0] == 'list-user':
			with lock:
				res ='Name Email\n'
				for listUser in userInfo:
					res += (listUser + ' '+ userInfo[listUser][0] + '\n')
			conn.send(res.encode())

		#hw2
		elif column[0] == 'create-board':
			with lock:
				boardname, boardmoderator = column[1], column[2]
				if boardname in board:
					res = 'Board already exists.'
				else:
					#{name:[index,moderator,{S/N:[title,content,author,date,[user+comment] ]}}
					index = str( len(board)+1 )							
					board.update( {boardname:[index, boardmoderator,{}]} )
					res ='Create board successfully.'
			conn.send(res.encode())

		elif column[0] == 'create-post':
			postuser, postboard = column[1], column[2]
			with lock:
				if postboard not in board:
					res = 'Board does not exist.'
				else:
					#{name:[index,moderator,{S/N:[title,content,author,date,[user+comment] ]}}
					temp, t, realInfo = msg.partition('--title ')
					title, c, text = realInfo.partition('--content ')							
					content = text.replace('<br>', '\n')
					print('title--'+title)
					print('content--'+content)
					#get-time
					todaytime = str(datetime.datetime.today())
					today = todaytime.split()
					dd = today[0].split('-')
					date = dd[1] + '/' + dd[2]
					global SN
					SN +=1
					print(SN)
					board[postboard][2].update( {SN:[title, content, postuser, date, [] ]} ) 
					res = 'Create post successfully.'
			conn.send(res.encode())

		elif column[0] == 'list-board':
			with lock:
				res = 'Index Name Moderator\n'
				for listboard in board:
					res += ( board[listboard][0] +' '+ listboard +' '+ board[listboard][1] + '\n')
			conn.send(res.encode())

		elif column[0] == 'list-post':
			LPboard = column[1]
			with lock:
				if LPboard not in board:
					res = 'Board does not exist.'
				else:
					res='S/N    Title    Author    Date\n'
					for listSN in board[LPboard][2]:
						res += ( str(listSN) +'    '+board[LPboard][2][listSN][0]+'   '+board[LPboard][2][listSN][2]+'    '+board[LPboard][2][listSN][3]+'\n')
			conn.send(res.encode())

		elif column[0] == 'read':
			msgSN = column[1]
			readSN = int(msgSN)
			with lock:
				readpost=False
				for readboard in board:
					if readSN in board[readboard][2]:
						#{name:[index,moderator,{S/N:[title,content,author,date,[user+comment] ]}}
						res=''
						res+=('Author: '+board[readboard][2][readSN][2]+'\nTitle: '+board[readboard][2][readSN][0]+'\nDate: '+board[readboard][2][readSN][3])
						res+=('\n--\n' + board[readboard][2][readSN][1] + '\n--\n')
						for readcomment in board[readboard][2][readSN][4]:
							res+=(readcomment+'\n')
						readpost=True
						break
				if not readpost:
					res = 'Post does not exist.'
				conn.send(res.encode())

		elif column[0] == 'delete-post':
			msgSN, deleteuser = column[1], column[2]
			deleteSN = int(msgSN)
			with lock:
				deletepost=False
				for deleteboard in board:
					if deleteSN in board[deleteboard][2]:
						if deleteuser != board[deleteboard][2][deleteSN][2]:
							res = 'Not the post owner.'
							deletepost=True
							break
						else:
							del board[deleteboard][2][deleteSN]
							res = 'Delete successfully.'
							deletepost=True
							break
				if not deletepost:
					res = 'Post does not exist.'
			conn.send(res.encode())

		elif column[0] == 'update-post':
			updateuser, msgSN = column[1], column[2]
			updateSN = int(msgSN)
			with lock:
				updatepost=False
				for updateboard in board:
					if updateSN in board[updateboard][2]:
						if updateuser != board[updateboard][1]:
							res = 'Not the post owner.'
							updatepost=True
							break
						else:
							#{name:[index,moderator,{S/N:[title,content,author,date,[user+comment] ]}}
							t = msg.find('--title')
							if t == -1: 
								temp1, c, text = msg.partition('--content ')
								updatecontent = text.replace('<br>', '\n')
								board[updateboard][2][updateSN][1] = updatecontent
								print('content--'+updatecontent)
							else:
								temp2, c, updatetitle = msg. partition('--title ')
								board[updateboard][2][updateSN][0] = updatetitle
								print('title--'+updatetitle)
							res = 'Update successfully.'
							updatepost=True
							break
				if not updatepost:
					res = 'Post does not exist.'
			conn.send(res.encode())

		elif column[0] == 'comment':
			commentuser, msgSN = column[1], column[2]
			commentSN = int(msgSN)
			with lock:
				commentpost=False
				for commentboard in board:
					if commentSN in board[commentboard][2]:
						temp1, temp2, comment = msg.partition(msgSN)
						commenttext = commentuser + ':' + comment
						board[commentboard][2][commentSN][4].append(commenttext)
						res = 'Comment successfully.'
						commentpost=True
						break
				if not commentpost:
					res = 'Post does not exist.'
			conn.send(res.encode())

		elif column[0] == 'exit':
			#Exit=True
			break


		#hw3
		elif column[0] == 'create-chatroom':
			cport, cuser = int(column[1]), column[2]
			with lock:
				chat=True
				if cuser in chatroom:
					chat=False
				if not chat:
					res='User has already created the chatroom.'
					conn.send(res.encode())
				else:
					#{name:[status,port]}
					chatroom.update({cuser:['open', cport]})
					res=str(cport)
					conn.send(res.encode())

					#chatroomserver
					server = socket(AF_INET, SOCK_STREAM)
					server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
					server.bind((host, cport))
					server.listen(10)
					connlist=[]
					chatting=[]
					connlist.append(server)
					chatconn, chataddr = server.accept()
					connlist.append(chatconn)
					print (str(chataddr[1]) + " connected.")
					start_new_thread(chatroom_thread,(server, chatconn, connlist, chatting))				
					#continue
					#conn.close()  
					#server.close()

		elif column[0] == 'join-chatroom':
			joinuser = column[1]
			with lock:
				#{name:[status,port]}
				join=False
				if joinuser in chatroom:
					if chatroom[joinuser][0] == 'open':
							res=str(chatroom[joinuser][1])
							join=True
				if not join:
					res='The chatroom does not exist or the chatroom is close.'				
			conn.send(res.encode())

		elif column[0] =='leave-chatroom':
			with lock:
				leaveuser = column[1]
				chatroom[leaveuser][0]='close'

		elif column[0] == 'restart-chatroom':
			with lock:
				cuser = column[1]
				restart=False
				running=False
				if cuser in chatroom:
					restart=True
					if chatroom[cuser][0]=='open':
						running=True					
					else:
						cport=chatroom[cuser][1]

				if running:
					res='Your chatroom is still running.'
					conn.send(res.encode())
				elif not restart:
					res='Please create-chatroom first.'
					conn.send(res.encode())
				else:
					#{name:[status,port]}
					#chatroom.update({cuser:['open', cport]})
					chatroom[cuser][0]='open'
					res=str(cport)
					conn.send(res.encode())

					'''
					#chatroomserver
					server = socket(AF_INET, SOCK_STREAM)
					server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
					server.bind((host, cport))
					server.listen(10)
					connlist=[]
					connlist.append(server)
					chatconn, chataddr = server.accept()
					connlist.append(chatconn)
					print (str(chataddr[1]) + " connected.")
					start_new_thread(chatroom_thread,(server, chatconn, connlist, chatroom))				
					#continue
					#conn.close()  
					#server.close()
					'''		
			
	conn.close()



#udp
def client_threadUDP(udp, chatroom): 
	#list chatroom
	#{name:[status,port]}
	while True:
		data,addr = udp.recvfrom(8192)
		msg = str(data, encoding='utf-8')
		print(msg)
		with lock:
			res='chatroom-name status\n'
			for room in chatroom:
				res+=( room + '  ' + chatroom[room][0] + '\n' )
		udp.sendto(res.encode(), (addr[0], addr[1]) )





def handler(sig, frame):
	# Handle any cleanup here
	serverTCP.close()
	serverUDP.close()
	print(' Close server.')
	sys.exit(0)
    
if __name__ == '__main__':
	# run the handler when SIGINT is recieved
	signal(SIGINT, handler)


	start_new_thread(client_threadUDP, (serverUDP, chatroom))
	while True:
		client, addr=serverTCP.accept()	
		#serveripaddr, serverport=serverTCP.getsockname()
		#clientipaddr, clientport=serverTCP.getpeername()
		print('New connection.') 
		print('Connection from ' + str(addr[0]) + ' : ' + str(addr[1]) )
		start_new_thread(client_threadTCP, (host, client, addr, userInfo, board, chatroom))
		threadCount +=1
		print('Thread number '+ str(threadCount) + ' is executed.')


'''
while True:
	client, addr=serverTCP.accept()	
	#serveripaddr, serverport=serverTCP.getsockname()
	#clientipaddr, clientport=serverTCP.getpeername()
	print('New connection.')
	print('Connection from ' + str(addr[0]) + ' : ' + str(addr[1]) )
	_thread.start_new_thread(client_thread, (client, addr, userInfo, board))
	threadCount +=1
	print('Thread number '+ str(threadCount) + ' is executed.')
serverTCP.close()
serverUDP.close()
'''



	

