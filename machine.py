#!python3
import time

class State(object):
		
	def __init__(self):
		print ('Processing current state:', str(self))

	def update(self):
		"""
		Handle Events
		"""
		pass
		
	def __repr__(self):
		"""
		Leverages the __str__ method to describe the State
		"""
		return self.__str__()
	
	def __str__(self):
		"""
		Returns the name of the State.
		"""
		return self.__class__.__name__
		
class Green(State):
	
	def __init__(self, flashing):
		self.flashing = flashing
	
	def update(self):
		if self._loop:
			print("LOOP")
			time.sleep(1.0)
		return self
		
class Machine(object):

	def __init__(self):
		self.state = TestState(loop=True)
		
	def on_event(self):
		
		self.state = self.state.event()