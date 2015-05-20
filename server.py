import select
import socket
import threading
import time
import os
import subprocess
import sys


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
					print "closing"
					self.client.close()
					running = 0
				
				
				
             	
			else:
				print "closing"
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
 
	def __init__( self, port, handler=Client, killSwitch=False ):
		self.host = ''
		self.port = port
		self.backlog = 5
		self.size = 1024
		self.server = None
		self.threads = []
		self.handler = handler
		self.running = True
		self.killSwitch = killSwitch
		if killSwitch:
			self.killLock = threading.Lock()

			
		
		
	def open_socket( self ):
		try:
			self.server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.server.bind( ( self.host, self.port ) )
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.listen( 5 )
		except socket.error, ( value, message ):
		
			if self.server:
				self.server.close()
				print "Could not open socket: " + message
				sys.exit( 1 )

		
		
	def run( self ):
		self.open_socket()
		
		
		input = [self.server, sys.stdin ]
		
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
			c.join()

	def kill( self ):
		self.running = 0
