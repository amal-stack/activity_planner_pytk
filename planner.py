import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmb
import tkinter.font as tkfont
import tkinter.filedialog
import ttkthemes as ttkt
import sys
import pickle
import PIL
class Activity:
    """
    Represents a single activity.

    Attributes:
        name(str): Activity Name
        iid(str): Activity ID, uniquely identifies the activity
        start(str): Start Time
        end(str): End Time
        parent()

    """
    def __init__(self, name, start, end, priority, parent=None):
        self.name = name
        self.iid = id(name)
        self.start = start
        self.end = end
        self.parent = parent #parent iid
        self.checked = False
        self.priority = priority
        
    def has_parent(self):
        return True if self.parent is not None else False
   
   #TODO: 
    def has_completed(self):
        self.checked = True

    #TODO:
    def notify(self):
        pass 

    def __str__(self):
        return str((self.name, self.iid, self.start, self.end, self.parent, self.priority))

    def __repr__(self):
        return self.__str__()


class ActivityTreeviewHandler:
    """
    Handles the treeview to which the activity objects are added
    """
    def __init__(self, tree_label_frame, on_item_select_callback=None, *cols):
        self.activity_tree = ttk.Treeview(tree_label_frame, columns=list(cols))
        self.activity_tree.heading('#0', text="Name")
        
        self.activities = [] #Activity maintainer list for serialization and deserialization
        for col in cols:
            self.activity_tree.heading(col, text=col)
        
        self.activity_tree.bind('<<TreeviewSelect>>', on_item_select_callback)
        self.activity_tree.pack(padx=50, pady=50)
        

    def add_activity(self, activity):
        """ If activity has a parent, adds it a sub activity else adds at the top level. 
        
            The iid attribute of activity is used as the item id in the tree."""
        self.activities.append(activity)
        if activity.has_parent():
                self.activity_tree.insert(activity.parent, 'end', activity.iid, text=activity.name, values=(activity.start, activity.end, activity.priority))
        else:            
                self.activity_tree.insert('', 'end', activity.iid, text=activity.name, values=(activity.start, activity.end, activity.priority))
        
    
    def remove_activity(self, activity_iid):
        """ Removes an activity from the list and not from the treeview"""
        #Prepare list of activities to be removed
        removed_activites = [activity for activity in self.activities if activity.iid in activity_iid]
        #Remove them 1 by 1
        for activity in removed_activites:
            self.activities.remove(activity)


    def remove_selected_activity(self):
        """ Removes the currently selected activity from the treeview and then calls remove_activity()"""
        sel = self.activity_tree.selection()
        if(not sel):
            tkmb.showerror("Error", "Nothing selected to delete")
            return
        self.activity_tree.delete(sel)
        self.remove_activity(sel)
        
    def save_state(self):
        """ Serializer; writes all activites in the current treeview to a file using pickle 
            and returns the destination file name.  Returns an empty string if fails.

            Return: 
                str (Returns the destination file name) 
          """
        try:
            with open(tkinter.filedialog.asksaveasfilename( title="Enter File Name"), 'wb') as dest_file:
                #Serialize
                pickle.dump(self.activities, dest_file, pickle.HIGHEST_PROTOCOL)
                return dest_file.name
        except Exception as e:
            tkmb.showerror("Failed", "Couldn't save list")
            return ""
        
    
    def clear_treeview(self):
        """ Empties the treeview """
        self.activity_tree.delete(*self.activity_tree.get_children())
        
    #Loads a list state from file after clearing the tree
    def load_state(self):
        """ Deserializer; Clears the tree, asks the user to open a saved file, and adds the activities to the tree
            and returns the file name. Returns an empty string if fails.

            Return: 
                str (Returns the destination file name) 
         """
        try:
             self.clear_treeview()
             with open(tkinter.filedialog.askopenfilename( title="Select File"), 'rb') as dest_file:
                 #Deserialize
                 self.activities = pickle.load(dest_file)
                
                 for activity in self.activities:
                     if activity.has_parent():
                        self.activity_tree.insert(activity.parent, 'end', activity.iid, text=activity.name, values=(activity.start, activity.end, activity.priority))
                     else:            
                        self.activity_tree.insert('', 'end', activity.iid, text=activity.name, values=(activity.start, activity.end, activity.priority))

                 return dest_file.name
            
        except Exception as e:
            tkmb.showerror("Failed", "Couldn't load list")
            return ""
        
class InputWindow:
    """ Represents the input window that 
        * Takes in the details of a new activity
        * Constructs an activity object from the details
        * Passes the constructed object to the ActivityTreeviewHandler object's add_activity()
        
         """
    def __init__(self, w_title, treeview_handler: ActivityTreeviewHandler, has_parent=False):
        #Create Toplevel
        self.container = tk.Toplevel()
        self.container.title(w_title)
        self.has_parent = has_parent
        self.adder_pane = ttk.Frame(self.container)
        self.adder_pane.pack(expand=True, fill=tk.BOTH, ipadx=50, ipady=100)
        
        self.treeview_handler = treeview_handler
        #Create input fields
        self.activity_input = {}
        self.activity_input['name'] = ttk.Entry(self.adder_pane), ttk.Label(self.adder_pane, text="Activity name:")
        self.activity_input['start'] = ttk.Entry(self.adder_pane), ttk.Label(self.adder_pane, text="From :")
        self.activity_input['end'] = ttk.Entry(self.adder_pane), ttk.Label(self.adder_pane, text="To :")
        self.activity_input['priority'] = ttk.Entry(self.adder_pane), ttk.Label(self.adder_pane, text="Priority:")

        #Add to parent container
        self.activity_input['name'][1].grid(row=0, column=0, padx=10, pady=10)
        self.activity_input['name'][0].grid(row=0, column=1, padx=10, pady=10)
        self.activity_input['start'][1].grid(row=1, column=0,  padx=10, pady=10)
        self.activity_input['start'][0].grid(row=1, column=1,  padx=10, pady=10)
        self.activity_input['end'][1].grid(row=2, column=0, padx=10, pady=10)
        self.activity_input['end'][0].grid(row=2, column=1, padx=10, pady=10)
        self.activity_input['priority'][1].grid(row=3, column=0,  padx=10, pady=10)
        self.activity_input['priority'][0].grid(row=3, column=1,  padx=10, pady=10)
    
        ttk.Button(self.adder_pane, text="Add", command=self.construct_activity_from_input).grid(row=4,column=1)
        self.container.focus_force()
        self.container.mainloop()

    
    def construct_activity_from_input(self):
        for field in self.activity_input:
                    if self.activity_input[field][0].get() == "":
                        tkmb.showerror("Empty field "+field, "Please enter a valid "+field)
                        return
        if self.has_parent:
            parent = self.treeview_handler.activity_tree.selection()
            if not parent:
                tkmb.showerror('Error', 'Select an activity to add subactivities')
        activity = Activity(
                self.activity_input['name'][0].get(),
                self.activity_input['start'][0].get(),
                self.activity_input['end'][0].get(),
                self.activity_input['priority'][0].get(),
                parent if self.has_parent else None
            )
        self.treeview_handler.add_activity(activity)
        self.container.destroy()
    
class HelpWindow:
    def __init__(self, event=None):
        self.container = tk.Toplevel()
        self.master = ttk.Frame(self.container)
        self.master.pack(fill=tk.BOTH, expand=True)
        self.help = 'Welcome to Activity Planner\n\n\n'
        self.help += 'Activity Planner helps you schedule a list of activites and sub-activities which you plan to get done.\n'
        self.help += 'It also supports saving your activity list to a file and then loading it later.\n'
        
        
    
        self.message = ttk.Label(self.master, text=self.help)
        self.message.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        



class App:       
    """ The main Activity Planner App
    
        Attributes
        themes(list) - helps implementing change_theme()
        saved(bool) - monitors save state 
    """
    def __init__(self):

        self.container = ttkt.ThemedTk()
        self.master = ttk.Frame(self.container)
        self.master.pack(fill=tk.BOTH, expand=True)

        self.themes = self.container.get_themes()

        self.tree_label_frame = ttk.LabelFrame(self.master, text="Your Activities")
        self.button_label_frame = ttk.LabelFrame(self.master, text="Modify")

        self.treeview_handler = ActivityTreeviewHandler(self.tree_label_frame, self.on_select, 'From', 'To', 'Priority') 

        self.add_button =  ttk.Button(self.button_label_frame, text="Add Activity...", command=self.on_add_activity)
        self.add_button.pack(anchor=tk.CENTER, pady=10)

        self.remove_button = ttk.Button(self.button_label_frame, text="Delete Activity", state='disabled', command=self.on_delete_activity)
        self.remove_button.pack(anchor=tk.CENTER, pady=10)

        self.add_sub_button = ttk.Button(self.button_label_frame, text="Add Sub Activity...", state='disabled', command=self.on_add_sub_activity)
        self.add_sub_button.pack(anchor=tk.CENTER, pady=10)
        self.theme_changer = self.change_theme()
        ttk.Button(self.button_label_frame, text="Change Theme", command= lambda: next(self.theme_changer)).pack(pady=10,  anchor=tk.CENTER)



        self.tree_label_frame.pack(padx=50, pady=25)
        self.button_label_frame.pack(padx=50, pady=25, fill=tk.X, expand=True)
        self.container.wm_state('zoomed')

        
        self.saved = True

        #Menu
        self.menubar = tk.Menu(self.container)
        
        self.menus = {}

        self.menus['file'] = tk.Menu(self.menubar, tearoff=0)
        self.menus['file'].add_command(label="New     Ctrl+N", command=self.new_instance)
        self.menus['file'].add_command(label="New Child Window      Ctrl+Shift+N", command=self.new_child_instance)
        self.menus['file'].add_separator()

        self.menus['file'].add_command(label="Save...     Ctrl+S", command=self.on_save)
        self.menus['file'].add_command(label="Load...     Ctrl+L", command=self.on_load)
        self.menus['file'].add_separator()

        self.menus['file'].add_command(label="Quit", command=self.quit)

        self.menus['edit'] = tk.Menu(self.menubar, tearoff=0)
        self.menus['edit'].add_command(label="Add Activity...     Ins / Ctrl+I", command=self.on_add_activity)
        self.menus['edit'].add_command(label="Add Sub Activity...     Ctrl+Shift+I", command=self.on_add_sub_activity, state='disabled')
        self.menus['edit'].add_command(label="Delete Activity Del / Ctrl+D", command=self.on_delete_activity, state='disabled')

        self.menus['help'] = tk.Menu(self.menubar, tearoff=0)
        self.menus['help'].add_command(label="Help     Ctrl+H", command= lambda: HelpWindow())
        
        self.menubar.add_cascade(label="File", menu=self.menus['file'])
        self.menubar.add_cascade(label="Edit", menu=self.menus['edit'])
        self.menubar.add_cascade(label="Help", menu=self.menus['help'])                      
        self.container.config(menu=self.menubar)

        #Keyboard Shortcuts
        self.container.bind("<Control-n>", self.new_instance)
        self.container.bind("<Control-N>", self.new_child_instance)
        self.container.bind("<Control-s>", self.on_save)
        self.container.bind("<Control-l>", self.on_load)
        self.container.protocol("WM_DELETE_WINDOW", self.quit)

        self.container.bind("<Control-i>", self.on_add_activity)
        self.container.bind("<Control-I>", self.on_add_sub_activity)
        self.container.bind("<Insert>", self.on_add_activity)
        self.container.bind("<Delete>", self.on_delete_activity)
        self.container.bind("<Control-d>", self.on_delete_activity)
        self.container.bind("<Control-h>", HelpWindow)
        self.container.title("Activity Planner")
        self.container.iconphoto(True,tk.PhotoImage(file='img.png'))
        self.container.set_theme('scidmint')
        self.container.mainloop()


    def change_theme(self):
        """ Cycles through the available themes provided by ttkthemes"""
        while True:
            for thm in self.themes:
                self.container.set_theme(thm)
                yield


    def on_add_activity(self, event=None):
        self.saved = False
        InputWindow("Add a New Activity", self.treeview_handler)
        

    def on_add_sub_activity(self, event=None):
        InputWindow("Add a New Sub Activity", self.treeview_handler, has_parent=True)
        self.saved = False
        
    def on_delete_activity(self, event=None):
        self.saved = False
        self.treeview_handler.remove_selected_activity()
        self.add_sub_button['state'] = 'disabled'
        self.remove_button['state'] = 'disabled'
        
    def on_select(self, event=None):
         self.add_sub_button['state'] = 'normal'
         self.remove_button['state'] = 'normal'
         self.menus["edit"].entryconfig("Add Sub Activity...     Ctrl+Shift+I", state='normal')
         self.menus["edit"].entryconfig("Delete Activity Del / Ctrl+D", state='normal')
    def quit(self):
        choice = self.ask_save_state()
        
        if choice is None:
            return
        if choice:
            if not self.on_save():
                return
            
        
        self.container.destroy()
        sys.exit(0)
        
    def new_instance(self, event=None):
        choice = self.ask_save_state()
        if choice is None:
            return
        if choice:
            if not self.on_save():
                return
        self.container.destroy()
        App()

    def new_child_instance(self, event=None):
        App()

    def ask_save_state(self):
        if self.saved:
            return False
        return tkmb.askyesnocancel("Save List", "Do you want to save the list?")
            
                

    def on_save(self, event=None):
        name = self.treeview_handler.save_state()
        if not name:
            return False
        self.container.title(name+ " - Activity Planner")
        self.saved = True
        return True

    def on_load(self, event=None):
        choice = self.ask_save_state()
        if choice is None:
            return
        if choice:
            if not self.on_save():
                return
        name = self.treeview_handler.load_state()
        self.container.title(name+ " - Activity Planner")

App()
















