class FakeFile:
  def poll(self):
    return False
 
  def communicate(self):
    return '', ''