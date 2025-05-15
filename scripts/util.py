from tkinter import filedialog

def dist(a, b): # basic distance function
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**(1/2)

def choose_file(save=False): # use tkinter filedialog to get files
        filetypes = [('All files', '*.*'), ('PNG files', '*.png'), ('JPEG files', '*.jpg')]
        if save: return filedialog.asksaveasfile(filetypes=filetypes)
        return filedialog.askopenfilename(filetypes=filetypes)