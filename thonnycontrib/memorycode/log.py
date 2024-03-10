from time import time

def text_inserted(self, event):
       if event.text_widget == self.text and "\n" in event.text:
           pass
            
def add_to_file(file, text):
    if not file or not text:
        return
    try:
        with open(file, 'a') as f:
            f.write(text)
    except IOError as e:
        print(f"Memorycode log: error writing to {file}: {e}")