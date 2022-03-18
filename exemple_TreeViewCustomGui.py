#More information http://www.plugincafe.com/forum/forum_posts.asp?TID=14102&PID=56287#56287
import c4d

# Be sure to use a unique ID obtained from http://www.plugincafe.com/.
PLUGIN_ID = 1000050 # TEST ID ONLY

# TreeView Column IDs.
ID_CHECKBOX = 1
ID_NAME = 2
ID_OTHER = 3

class TextureObject(object):
    """
    Class which represent a texture, aka an Item in our list
    """
    texturePath = "TexPath"
    otherData = "OtherData"
    _selected = False

    def __init__(self, texturePath):
        self.texturePath = texturePath
        self.otherData += texturePath

    @property
    def IsSelected(self):
        return self._selected

    def Select(self):
        self._selected = True

    def Deselect(self):
        self._selected = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.texturePath


class ListView(c4d.gui.TreeViewFunctions):

    def __init__(self):
        self.listOfTexture = list() # Store all objects we need to display in this list

        # Add some defaults values 
        t1 = TextureObject("T1")
        t2 = TextureObject("T2")
        t3 = TextureObject("T3")
        t4 = TextureObject("T4")

        self.listOfTexture.extend([t1, t2, t3, t4])


    def IsResizeColAllowed(self, root, userdata, lColID):
        return True

    def IsTristate(self, root, userdata):
        return False

    def GetColumnWidth(self, root, userdata, obj, col, area):
        return 80  # All have the same initial width

    def IsMoveColAllowed(self, root, userdata, lColID):
        # The user is allowed to move all columns.
        # TREEVIEW_MOVE_COLUMN must be set in the container of AddCustomGui.
        return True

    def GetFirst(self, root, userdata):
        """
        Return the first element in the hierarchy, or None if there is no element.
        """
        rValue = None if not self.listOfTexture else self.listOfTexture[0]
        return rValue

    def GetDown(self, root, userdata, obj):
        """
        Return a child of a node, since we only want a list, we return None everytime
        """
        return None

    def GetNext(self, root, userdata, obj):
        """
        Returns the next Object to display after arg:'obj'
        """
        rValue = None
        currentObjIndex = self.listOfTexture.index(obj)
        nextIndex = currentObjIndex + 1
        if nextIndex < len(self.listOfTexture):
            rValue = self.listOfTexture[nextIndex]

        return rValue

    def GetPred(self, root, userdata, obj):
        """
        Returns the previous Object to display before arg:'obj'
        """
        rValue = None
        currentObjIndex = self.listOfTexture.index(obj)
        predIndex = currentObjIndex - 1
        if 0 <= predIndex < len(self.listOfTexture):
            rValue = self.listOfTexture[predIndex]

        return rValue

    def GetId(self, root, userdata, obj):
        """
        Return a unique ID for the element in the TreeView.
        """
        return hash(obj)

    def Select(self, root, userdata, obj, mode):
        """
        Called when the user selects an element.
        """
        if mode == c4d.SELECTION_NEW:
            for tex in self.listOfTexture:
                tex.Deselect()
            obj.Select()
        elif mode == c4d.SELECTION_ADD:
            obj.Select()
        elif mode == c4d.SELECTION_SUB:
            obj.Deselect()

    def IsSelected(self, root, userdata, obj):
        """
        Returns: True if *obj* is selected, False if not.
        """
        return obj.IsSelected

    def SetCheck(self, root, userdata, obj, column, checked, msg):
        """
        Called when the user clicks on a checkbox for an object in a
        `c4d.LV_CHECKBOX` column.
        """
        if checked:
            obj.Select()
        else:
            obj.Deselect()

    def IsChecked(self, root, userdata, obj, column):
        """
        Returns: (int): Status of the checkbox in the specified *column* for *obj*.
        """
        if obj.IsSelected:
            return c4d.LV_CHECKBOX_CHECKED | c4d.LV_CHECKBOX_ENABLED
        else:
            return c4d.LV_CHECKBOX_ENABLED

    def GetName(self, root, userdata, obj):
        """
        Returns the name to display for arg:'obj', only called for column of type LV_TREE
        """
        return '' # Or obj.texturePath

    def DrawCell(self, root, userdata, obj, col, drawinfo, bgColor):
        """
        Draw into a Cell, only called for column of type LV_USER
        """
        rgbSelectedColor = c4d.gui.GeUserArea().GetColorRGB(c4d.COLOR_TEXT_SELECTED)
        selectedColor = c4d.Vector(rgbSelectedColor["r"], rgbSelectedColor["g"], rgbSelectedColor["b"]) / 255.0
        txtColor = selectedColor if obj.IsSelected else c4d.Vector(0.2, 0.4, 0.8)
        drawinfo["frame"].DrawSetTextCol(txtColor, drawinfo["bgCol"])

        if col == ID_NAME:
            name = str(obj)
            geUserArea = drawinfo["frame"]
            w = geUserArea.DrawGetTextWidth(name)
            h = geUserArea.DrawGetFontHeight()
            xpos = drawinfo["xpos"]
            ypos = drawinfo["ypos"] + drawinfo["height"]
            drawinfo["frame"].DrawText(name, xpos, int(ypos - h * 1.1))
            xpos = drawinfo["xpos"]
            ypos = drawinfo["ypos"] + drawinfo["height"]

        if col == ID_OTHER:
            name = obj.otherData
            geUserArea = drawinfo["frame"]
            w = geUserArea.DrawGetTextWidth(name)
            h = geUserArea.DrawGetFontHeight()
            xpos = drawinfo["xpos"]
            ypos = drawinfo["ypos"] + drawinfo["height"]
            drawinfo["frame"].DrawText(name, xpos, ypos - h * 1.1)

    def DoubleClick(self, root, userdata, obj, col, mouseinfo):
        """
        Called when the user double-clicks on an entry in the TreeView.

        Returns:
          (bool): True if the double-click was handled, False if the
            default action should kick in. The default action will invoke
            the rename procedure for the object, causing `SetName()` to be
            called.
        """
        c4d.gui.MessageDialog("You clicked on " + str(obj))
        return True

    def DeletePressed(self, root, userdata):
        "Called when a delete event is received."
        for tex in reversed(self.listOfTexture):
            if tex.IsSelected:
                self.listOfTexture.remove(tex)

class TestDialog(c4d.gui.GeDialog):
    _treegui = None # Our CustomGui TreeView
    _listView = ListView() # Our Instance of c4d.gui.TreeViewFunctions

    def CreateLayout(self):
        # Create the TreeView GUI.
        customgui = c4d.BaseContainer()
        customgui.SetBool(c4d.TREEVIEW_BORDER, c4d.BORDER_THIN_IN)
        customgui.SetBool(c4d.TREEVIEW_HAS_HEADER, True) # True if the tree view may have a header line.
        customgui.SetBool(c4d.TREEVIEW_HIDE_LINES, False) # True if no lines should be drawn.
        customgui.SetBool(c4d.TREEVIEW_MOVE_COLUMN, True) # True if the user can move the columns.
        customgui.SetBool(c4d.TREEVIEW_RESIZE_HEADER, True) # True if the column width can be changed by the user.
        customgui.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, True) # True if all lines have the same height.
        customgui.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True) # Alternate background per line.
        customgui.SetBool(c4d.TREEVIEW_CURSORKEYS, True) # True if cursor keys should be processed.
        customgui.SetBool(c4d.TREEVIEW_NOENTERRENAME, False) # Suppresses the rename popup when the user presses enter.

        self._treegui = self.AddCustomGui( 1000, c4d.CUSTOMGUI_TREEVIEW, "", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 300, 300, customgui)
        if not self._treegui:
            print ("[ERROR]: Could not create TreeView")
            return False

        self.AddButton(1001, c4d.BFH_CENTER, name="Add")
        return True

    def InitValues(self):
        # Initialize the column layout for the TreeView.
        layout = c4d.BaseContainer()
        layout.SetLong(ID_CHECKBOX, c4d.LV_TREE)
        layout.SetLong(ID_NAME, c4d.LV_USER)
        layout.SetLong(ID_OTHER, c4d.LV_USER)
        self._treegui.SetLayout(2, layout)

        # Set the header titles.
        self._treegui.SetHeaderText(ID_CHECKBOX, "")
        self._treegui.SetHeaderText(ID_NAME, "Name")
        self._treegui.SetHeaderText(ID_OTHER, "Other")
        self._treegui.Refresh()

        # Set TreeViewFunctions instance used by our CUSTOMGUI_TREEVIEW
        self._treegui.SetRoot(self._treegui, self._listView, None)
        return True

    def Command(self, id, msg):
        # Click on button
        if id == 1001:
            # Add data to our DataStructure (ListView)
            newID = len(self._listView.listOfTexture) + 1 
            tex = TextureObject("T{}".format(newID))
            self._listView.listOfTexture.append(tex)

            # Refresh the TreeView
            self._treegui.Refresh()

        return True


def main():
    global dlg
    dlg = TestDialog()
    dlg.Open(c4d.DLG_TYPE_ASYNC, PLUGIN_ID, defaulth=600, defaultw=600)

if __name__ == "__main__":
    main()