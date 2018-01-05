import os
from abc import ABCMeta, abstractmethod
import Tkinter as tk
import tkFont
import ttk as ttk
import cx_Oracle
import datetime
import calendar_custom

# TODO check fro gr cash return and credit note adjustment
# error in no salesman check

ip = '127.0.0.1'
port = 1521
SID = ''
try:
    dsn_tns = cx_Oracle.makedsn(ip, port, service_name='dserver')
    connection = cx_Oracle.connect(user="", password="", dsn=dsn_tns,mode=cx_Oracle.SYSDBA)
    connection.current_schema= "RICHIERETAIL"
except:
    dsn_tns = cx_Oracle.makedsn(ip, port, service_name='xe')
    connection = cx_Oracle.connect(user="RICHIERETAIL", password="admin", dsn=dsn_tns)
cr=connection.cursor()
#print cr

root = tk.Tk()
root.wm_title("SALESMAN COMMISSION")

root.protocol("WM_DELETE_WINDOW",root.destroy)
# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# set the dimensions of the screen 
# and where it is placed
root.geometry("+40+10")

class Observer(object):
    __metaclass__ = ABCMeta
 
    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class CalendarFrameCustom(calendar_custom.CalendarFrame):
    def __init__(self, master):
        tk.LabelFrame.__init__(self, master, text="")
        self.__observers = []

        self.selected_date = tk.StringVar()
        i= datetime.datetime.today()
        today= "%s/%s/%s" % (i.day, i.month, i.year)
        self.selected_date.set(today)

        tk.Label(self, textvariable=self.selected_date,width=12).pack(side=tk.LEFT)
        tk.Button(self, text="Choose a date", command=self.getdate).pack(side=tk.LEFT)

    def register_date_change_observer(self, observer):
        self.__observers.append(observer)
    
    def notify_date_change_observers(self,new_date, *args, **kwargs):
        for observer in self.__observers:
            observer.update(self,{'new_date':self.selected_date})
    

    def getdate(self):
        cd = calendar_custom.CalendarDialog(self)
        result = cd.result
        if result is not None:self.selected_date.set(result.strftime("%d/%m/%Y"))
        #print "abc"
        self.notify_date_change_observers(self,{'new_date':self.selected_date})


class treeListBox(Observer):
    """use a ttk.TreeView as a multicolumn ListBox"""
    def __init__(self,element_header):
        self.element_header = element_header
        self.tree = None
        self.salesman_menu=None
        self.salesman_dict={}
        
        cr.execute('select SALESMAN_SNAME,SALESMAN_SCODE from SALESMAN where salesman_nactiveflg !=1 or salesman_nactiveflg is null')
        for res in cr:
        	#print res
        	self.salesman_dict[res[0]]=res[1]
        self.salesman_list=[i for i in self.salesman_dict]
        #print self.salesman_list,self.salesman_dict
        self.date=None
        self.salesman_default_value=self.salesman_list[1]

        self._setup_widgets()
        self._build_tree()
        self.get_salesman_lines()
    
    def _setup_widgets(self):
        s = """\

    SALESMAN COMMISSION
    """
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 6), text=s)
        msg.pack(fill='x')
        container = ttk.Frame()
        container.pack(fill='both', expand=True)

        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=self.element_header)
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        self.tree.tag_configure('child',background='light gray')
        #self.tree.bind("<<TreeviewSelect>>", self.selected)

        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        container_2=ttk.Frame(padding='0.5c 0.0c 0.5c 0.5c')
        container_2.grid(column=0,row=2,in_=container)

        labelframeCommission=ttk.LabelFrame(container_2)
        labelframeCommission.grid(column=3,row=0,in_=container_2,pady=(0,10),sticky="e")
        ttk.Label(labelframeCommission,text="Total Commission : ",background='#ffff99').pack(side=tk.LEFT)
        self.commission=tk.StringVar()
        self.commission.set("-------")
        ttk.Label(labelframeCommission,textvariable=self.commission,background='#ffff99').pack(side=tk.LEFT)
        
        ttk.Button(text="Previous",command=self.previous).grid(column=0,row=1,in_=container_2,padx=(50,10))

        self.salesman_value=tk.StringVar()
        self.salesman_menu=ttk.OptionMenu(container_2,self.salesman_value,self.salesman_default_value,*self.salesman_list)

        self.salesman_menu.grid(column=1,row=1,in_=container_2,sticky='ew')
        self.salesman_menu.config(width=13)
        
        ttk.Button(text="Next",command=self.next).grid(column=2,row=1,in_=container_2)
        
        self.calendarapp=CalendarFrameCustom(container_2)
        self.calendarapp.register_date_change_observer(self)
        self.calendarapp.grid(column=3,row=1,in_=container_2,padx=(10,10))

        self.salesman_value.trace("w",self.onchange_option)



    def next(self):
        #print "ok",self.salesman_value.get()
        #print self.salesman_list.index(self.salesman_value.get())
        #print len(self.salesman_list)
        next_val=self.salesman_list.index(self.salesman_value.get())+1
        if next_val==len(self.salesman_list):next_val=0
        self.salesman_value.set(self.salesman_list[next_val])
        

    def previous(self):
        pre_val=self.salesman_list.index(self.salesman_value.get())-1
        if pre_val==-1:pre_val=len(self.salesman_list)-1
        self.salesman_value.set(self.salesman_list[pre_val])
        

    def onchange_option(self,a=None,b=None,c=None):
        #print a,b,c,'ook'
        self.get_salesman_lines()

    def update(self,*args,**kwargs):
    	self.get_salesman_lines()
    	# this method is getting called from calendar app


    def _build_tree(self):
        for col in self.element_header:
            #print col
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col, width=tkFont.Font().measure(col.title()))
        
        self.tree.column('#0', width=20,minwidth=5)
        self.tree.column(' sub total ', anchor="e")
        self.tree.column('net amount', anchor="e")
        self.tree.column('commission', anchor="e")

        '''for item in self.element_list:
            i=self.tree.insert('', 'end', values=item)
            self.tree.insert(i, 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.element_header[ix], width=None) < col_w:
                    self.tree.column(self.element_header[ix], width=col_w)
        '''

    def get_salesman_lines(self):

    	for i in self.tree.get_children():
    	    self.tree.delete(i)


    	salesman = self.salesman_dict[self.salesman_value.get()]
    	selected_date = self.calendarapp.selected_date.get()
    	selected_date = int(datetime.datetime.strptime(selected_date,'%d/%m/%Y').strftime('%Y%m%d'))
    	#print selected_date
    	#selected_date=20161231

    	cr.execute('''
    		select 
    		GELO_NID,
    		GELO_NDOCNO, 
    		GELO_NDATE, 
    		GELO_NSALEQTY, 
    		GELO_NSALERETQTY, 
    		GELO_NSALEAMT, 
    		GELO_NSALERETAMT, 
    		GELO_NITEMDISC, 
    		GELO_NBILLAMT, 
    		GELODET_NBECHDAAM, 
    		GELODET_NQTY, 
    		GELODET_NDISCPER, 
    		GELODET_NTOTROWDISC, 
    		GELODET_SSMANCODE, 
    		GELODET_NRETFLG, 
    		GELODET_NDATE, 
    		GELODET_NAMTAFTDISC, 
    		GELODET_SLAMCCODEPRF 
    		from gelodet gl inner join gelo g on g.gelo_nid=gl.gelodet_smaincode where gl.gelodet_ndate = %s and gl.gelodet_ssmancode = '%s' order by gelo_nbillno'''%(selected_date,salesman))

    	result=cr.fetchall()
    	
    	tree_main=''
    	check=''
    	total_commission=0.0
    	for res in result:
    	    #print "---res[1]---",res[1]
    	    if check != res[1]:
    	    	check=res[1]
    	    	total_of_bill=0
    	    	bill_commission=0
    	    	for res_1 in result:
    	    		if res_1[1]==check:
    	    			total_of_bill+=res_1[9]
    	    			bill_commission+=self.calculate_commission(res_1)
    	    			#print "-----comm calculate--",self.calculate_commission(res_1)
			
    	        total_commission+=round(bill_commission,0)
    	        #print "--bill comm--",round(bill_commission,0)
    	        #print "total ",total_commission
    	        tree_main=self.tree.insert("",'end',values=[res[1],("%.2f"%total_of_bill),("    %.2f" % res[7])+" (Rs)",("%.2f" % res[8]),("%.2f"%round(bill_commission,0))])

    	    val1="  # "+str(res[17])	# barcode
    	    val21_space = (13-len(("%.2f (Rs)" % res[12])))*"_"
    	    #print "---len--",len(("%.2f (Rs)" % res[12])),len(val21_space)
    	    val2=("%.2f" % round(res[9],0))	# item price
    	    val3=("    %.2f (Rs) " % round(res[12],0)+val21_space+" [%.2f" % res[11])+" (%)]" 
    	    # discount amt and percent
    	    val4=("%.2f" % round(res[16],0))	#net amt after discount
    	    #print "from res"
    	    val5=self.calculate_commission(res)
    	    #print val5
    	    values=[val1,val2,val3,val4,val5]
    	    
    	    # to set column widths
    	    '''for i in range(len(values)):
    	        col_w = tkFont.Font().measure(values[i])
    	        print self.tree.column(self.element_header[i], width=None),col_w,self.element_header[i]'''
    	        #if self.tree.column(self.element_header[i], width=None) < col_w:
    	        #    self.tree.column(self.element_header[i], width=col_w) 
    	    
    	    self.tree.insert(tree_main,'end',values=values,tags=('child',))
    	    
    	    
    	self.commission.set(str(total_commission))
    	print salesman,self.salesman_value.get()
       
    def calculate_commission(self,line_data):
    	comm=0.0
    	if os.environ['COMPUTERNAME']=='MININT-EJF4EA9':
	    	if line_data[11]>=10.0:
	    		comm=0.01*round(line_data[16],0)
	    	elif line_data[11]==0.00:
	    		comm=0.02*round(line_data[16],0)
	    	else:
	    		comm=(0.02*round(line_data[9],0))-(0.1*round(line_data[12],0))
	    		print "----comm---",comm

    	#if comm>0:print "-------comm--",line_data,comm
    	return comm


def isnumeric(s):
    """test if a string is numeric"""
    for c in s:
        if c in "1234567890-.":
            numeric = True
        else:
            return False
    return numeric
def change_numeric(data):
    """if the data to be sorted is numeric change to float"""
    new_data = []
    if isnumeric(data[0][0]):
        # change child to a float
        for child, col in data:
            new_data.append((float(child), col))
        return new_data
    return data
def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    data = change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
        command=lambda col=col: sortby(tree, col, int(not descending)))


element_header = ['bill no / (barcode)',' sub total ','    discount (Rs / %)    ','net amount','commission','    ']

element_listbox = treeListBox(element_header)

#print(element_list)
root.mainloop()

print "conn close"
cr.close()
connection.close()
