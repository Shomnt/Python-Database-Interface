import customtkinter as CTk
from ScrollBarVertical import ScrollBar as sc


class ScrollBar(CTk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollbar = sc(master=self, orientation="vertical")
        self.scrollbar.grid(row=0, column=0)

    def change_size(self, width: int) -> None:
        self.configure(width=width)
        self.configure(height=self.scrollbar.cget("height")+15)
