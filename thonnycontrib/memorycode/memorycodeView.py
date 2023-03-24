from tkinter import ttk, Canvas, Frame, Label, Scrollbar

class MemorycodeView (ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self._label = ttk.Label(self, text="Memorycode")
        self._label.grid(row=0, column=0, sticky="nsew")

        canvas = Canvas(self, bg="purple")

        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

#        self.scrollable_frame.update_idletasks()  # Update frame info before adding it to canvas
        canvas.create_window((0, 0), anchor="nw", window=self.scrollable_frame)
       # canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=0, sticky="nse")

        for i in range(50):
            rect = Canvas(self.scrollable_frame, bg="blue", height=50)
            rect.grid(row=i, column=0, sticky="nsew")
            label = Label(rect, text=str(i + 1), fg="white", bg="blue")
            label.place(relx=0.5, rely=0.5, anchor="center")

if __name__ == "__main__":
    # For testing
    from tkinter import Tk
    root = Tk()
    root.geometry("400x400")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    MemorycodeView(root).grid(row=0, column=0, sticky="nsew")

    root.mainloop()