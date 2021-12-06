import c4d


class DlgList(c4d.gui.GeDialog):
    ID_BTON_SELECT_ALL = 1000
    ID_BTON_DESELECT_ALL = 1001
    
    ID_START_CHECK = 2000
    
    ID_BTON_OK = 3000
    ID_BTON_CANCEL = 3001
    
    TXT_SELECT_ALL = 'Tout séléctionner'
    TXT_DESELECT_ALL = 'Tout déséléctionner'
    
    TXT_OK = 'OK'
    TXT_CANCEL = 'Annuler'
    
    MARGIN = 20
    
    def __init__(self,lst, title = ''):
        self.title = title
        self.lst = lst
        self.len_lst = len(lst)
        
    def CreateLayout(self):
        
        self.SetTitle(self.title)
        
        
        
        #self.GroupBegin(300, flags=c4d.BFH_LEFT | c4d.BFV_TOP, cols=1, rows=3, title='', groupflags=0)
        
        #BOUTONS DE SELECTION
        self.GroupBegin(500,flags=c4d.BFH_SCALE, cols=2, rows=1, title='', groupflags=0, initw=0, inith=0)
        self.GroupBorderSpace(self.MARGIN,self.MARGIN,self.MARGIN,self.MARGIN)
        self.AddButton(self.ID_BTON_SELECT_ALL, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_SELECT_ALL)
        self.AddButton(self.ID_BTON_DESELECT_ALL, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_DESELECT_ALL)
        self.GroupEnd()
        
        #CHECKBOXES depuis la liste
        self.ScrollGroupBegin(400, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, scrollflags =c4d.SCROLLGROUP_VERT, initw=80, inith=100)
        self.GroupBegin(600, flags=c4d.BFH_SCALE, cols=1, rows=len(self.lst), title='', groupflags=0, initw=0, inith=0)
        for i,el in enumerate(self.lst):
            self.AddCheckbox(self.ID_START_CHECK+i,c4d.BFH_SCALE, 100, 10, el)
        self.GroupEnd()
        self.GroupEnd()
        
        #OK/CANCEL buttons
        self.GroupBegin(700, flags=c4d.BFH_SCALE, cols=2, rows=1, title='', groupflags=0, initw=0, inith=0)
        self.GroupBorderSpace(self.MARGIN,self.MARGIN,self.MARGIN,self.MARGIN)
        self.AddButton(self.ID_BTON_OK, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_OK)
        self.AddButton(self.ID_BTON_CANCEL, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_CANCEL)        
        self.GroupEnd()
        
        
        #self.GroupEnd()
        
    def Command(self, id, msg):
        
        if id == self.ID_BTON_SELECT_ALL:
            for i in range(self.len_lst):
                self.SetBool(self.ID_START_CHECK+i, True)
        
        if id == self.ID_BTON_DESELECT_ALL:
            for i in range(self.len_lst):
                self.SetBool(self.ID_START_CHECK+i, False)
                
        if id == self.ID_BTON_OK:
            res = []
            for i,el in enumerate(self.lst):
                if self.GetBool(self.ID_START_CHECK+i):
                    res.append(el)
            
            self.lst.clear()
            self.lst+=res
            self.Close()
        
        if id == self.ID_BTON_CANCEL:
            self.lst.clear()
            self.Close()
        
        
            

# Main function
def main():
    lst = [str(i).zfill(3) for i in range(10)]
    
    dlg = DlgList(lst, 'Prout, prout')
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE)
    print(lst)
    

# Execute main()
if __name__=='__main__':
    main()