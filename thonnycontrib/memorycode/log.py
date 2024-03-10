from time import time


class Log:
    def __init__(self, file=None):
        self.file = file

    def set_file(self, file):
        self.file = file

    def add_to_file(self, text):
        if not self.file or not text:
            return
        try:
            with open(self.file, 'a') as f:
                f.write(text)
        except IOError as e:
            print(f"Memorycode log: error writing to {self.file}: {e}")

    def get_time(self):
        return hex(int(time()))[2:]

    def log(self, event):
        if not hasattr(event, 'sequence'):
            # Discard: no sequence
            print(type(event))
            print(event.type)
            return
        print(event.sequence)
        if event.sequence == "TextInsert":
            if 'shell' in str(event.text_widget):  # in shell
                self.add_to_file(f"OP{self.get_time()} {event.text}\n")

        elif event.sequence == "ToplevelResponse" and event.command_name == "Run":
            self.add_to_file(f"RN{self.get_time()} \n")

        elif event.sequence == "<<Cut>>":
            self.add_to_file(f"CT{self.get_time()} \n")
        elif event.sequence == "<<Copy>>":
            self.add_to_file(f"CP{self.get_time()} \n")
        elif event.sequence == "<<Paste>>":
            print(dir(event))
            self.add_to_file(f"PS{self.get_time()} \n")
        elif event.sequence == "<<Undo>>":
            self.add_to_file(f"UD{self.get_time()} \n")
        elif event.sequence == "<<Redo>>":
            self.add_to_file(f"RD{self.get_time()} \n")
        elif event.sequence == "<<Find>>":
            print(dir(event))
            self.add_to_file(f"FD{self.get_time()} \n")
        elif event.sequence == "<<Replace>>":
            self.add_to_file(f"RP{self.get_time()} \n")
        elif event.sequence == "<FocusIn>":
            self.add_to_file(f"FI{self.get_time()} \n")
        elif event.sequence == "<FocusOut>":
            self.add_to_file(f"FO{self.get_time()} \n")
        elif event.sequence == "WindowFocusIn":
            self.add_to_file(f"FI{self.get_time()} \n")
        elif event.sequence == "WindowFocusOut":
            self.add_to_file(f"FO{self.get_time()} \n")
