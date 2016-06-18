import select
import socket
import threading
import time
import os
import subprocess
import sys
import psutil

#Class to parse input from socket and send output
#opened by Server class
class Client( threading.Thread ):
	def __init__( self, (client, address)  ):
		threading.Thread.__init__(self)
		self.client = client
		self.address = address
		self.size = 1024
		self.killWord = None		

	def run(self):
		running = 1
		
		while running:
			data = self.client.recv(self.size)
		
			if data:
				
				
				if self.handle( data ) == 0:
					
					self.client.close()
					running = 0
				
				
				
             	
			else:
				self.client.close()
				running = 0
				
			
				
	def handle( self, data ):
		print " Packet ( {data} ) recieved from {ADDR} ".format(data=data.strip(), ADDR=self.address )
		if self.killWord and self.killWord == data.strip():
			self.killLock.acquire()
			self.client.send("DIEING\n")
			
			
		
		return 0;


	def setKill( self, lock, word ):
		self.killLock = lock
		self.killWord = word

class Server:
	""" Class to listen for requests or commands
 Opens a socket and waits for input
 When socket connection is made 
 an instance of the client class is made
 To parse input and send output. """
 
	def __init__( self, port, handler=Client, killSwitch=False, tryagain=False ):
		self.host = ''
		self.port = port
		self.backlog = 5
		self.size = 1024
		self.server = None
		self.threads = []
		self.handler = handler
		self.running = True
		self.killSwitch = killSwitch
		self.tryagain = tryagain
		if killSwitch:
			self.killLock = threading.Lock()

			
		
		
	def open_socket( self ):
		try:
			self.server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.server.bind( ( self.host, self.port ) )
			self.server.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
			self.server.listen( 5 )
			
			return 0
		except socket.error as err :
		
			if self.server:

				self.server.close()
				print "Could not open socket: " + err.strerror

				t0 = time.time()
				if err.errno == 98 and self.tryagain:		
								
					print "checking for lost socket..."			
					for conn in psutil.net_connections():
						if conn.laddr[1] == self.port:
							
							print "Found socket {}".format(conn)
							if conn.pid:
								psutil.Process(conn.pid).kill()
								return 10
							else:
								return 60
							
				
			return -1
	def test(self):
		print "TESTING"
		
	def run( self ):
		resp = self.open_socket()
		if resp < 0:
			return 
		elif resp > 0:
			print "Process is trying to use this address, giving them {}s to close".format(resp)
			t0 = time.time()
			while ( time.time() - t0 ) < resp:
				sys.stdout.write( str(int(time.time()-t0)) )
				sys.stdout.flush()
				time.sleep(0.5)
				sys.stdout.write('\r')
			print
			resp = self.open_socket()
			
			if resp != 0:
				print "didn't work check to see who is using this socket."
				return 
			else:
				print "Success"
				
		input = [self.server ]
	
		while self.running:

			if self.killSwitch and self.killLock.locked():
				self.running = 0
			
			inputready,outputready,exceptready = select.select( input, [] ,[], 3 )

			
			for s in inputready:
				#print "inputready"
				
				if s == self.server:
                    # handle the server socket
               
					c = self.handler( self.server.accept() ) 
					self.threads.append( c )
					self.threads = [ thread for thread in self.threads if thread.is_alive() ]


					if self.killSwitch:
						c.setKill( self.killLock, self.killSwitch )
					c.start()
					
        # close all threads

		self.server.close()
		for c in self.threads:
			try:
				c.client.close()
			except socket.error:
				pass	
		
			c.join()

	def kill( self ):
		self.running = 0
		
		
if __name__ == "__main__":
	usage = "usage: server.py [portnum]  \n Like: server.py 6543"

	if len(sys.argv) != 2:
		print usage
	else:
		try:
			s=Server( int(sys.argv[1]), tryagain=True )
			s.run()
		except NameError:
			print usage
			
	

