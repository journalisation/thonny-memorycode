def text_inserted(self, event):
       if event.text_widget == self.text and "\n" in event.text:
           pass
            
def add_to_file(file, text):
    try:
        with open(file, 'a') as f:
            f.write(text)
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier {file}: {e}")