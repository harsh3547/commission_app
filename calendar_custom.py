import Tkinter
import ttkcalendar
import datetime
import tkSimpleDialog


class CalendarDialog(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    def body(self, master):
        self.calendar = ttkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.selection

# Demo code:


class CalendarFrame(Tkinter.LabelFrame):
    def __init__(self, master):
        Tkinter.LabelFrame.__init__(self, master, text="CalendarDialog Demo")

        def getdate():
            cd = CalendarDialog(self)
            result = cd.result
            self.selected_date.set(result.strftime("%d/%m/%Y"))

        self.selected_date = Tkinter.StringVar()
        self.selected_date.set("abc")

        Tkinter.Label(self, textvariable=self.selected_date,width=15).pack(side=Tkinter.LEFT)
        Tkinter.Button(self, text="Choose a date", command=getdate).pack(side=Tkinter.LEFT)


def main():
    root = Tkinter.Tk()
    root.wm_title("CalendarDialog Demo")
    CalendarFrame(root).pack()
    root.mainloop()

if __name__ == "__main__":
    main()