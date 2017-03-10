#!/usr/bin/python

import socket
import sys
import select
import time

class scottSock( socket.socket ):
	def __init__( self, HOST, PORT, timeout=None ):
		socket.socket.__init__( self, socket.AF_INET, socket.SOCK_STREAM )
		
		
		#self.settimeout(timeout)
		HOST = socket.gethostbyname(HOST)
		#print HOST, int( PORT )
		self.connect( ( HOST, int( PORT ) ) )
		
	def talk( self, message ):
		#print "Sending message:", message
		self.send( message )

	def listen( self ):
		test = True
		resp = ""
		while test:	
			try:
				ready = select.select([self], [], [], 1.0)
				if ready[0]:	
					newStuff = self.recv( 100 )
			except socket.timeout:
				return resp
				
			
			if newStuff:
				resp+=newStuff
			else:
				return resp
		
	def converse( self, message ):
		self.talk( message )
		return self.listen( )
	

if __name__ == "__main__":
	
	if len( sys.argv ) > 3:
		soc = scottSock( sys.argv[1], sys.argv[2] )
		print soc.talk( sys.argv[3] )
		
		
