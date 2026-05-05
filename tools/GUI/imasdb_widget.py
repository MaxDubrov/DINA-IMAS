import os
import imasdb
import imas
import xml.etree.ElementTree as ET
from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QFileDialog


class IMASDB_Widget(QWidget):
  def __init__(self, title):
    super().__init__()
    self.ui = imasdb.Ui_IMASDB()
    self.ui.setupUi(self)
    self.ui.groupBox.setTitle(title)
    self.ui.pushButton_SelectPath.clicked.connect(self.SelectPath)
    self.databasePath = os.getenv('HOME')
  
  
  def GetDBEntry(self, opt = 'a'):
    
    uri = self.GetURI()
    if uri != '':
      return imas.DBEntry(uri, opt)
    
    return None
    
  
  def GetDBMetadata(self):
    ret = {}
    
    ret['uri'] = self.ui.lineEditURI.text()
    ret['user'] = self.ui.lineEditUser.text()
    ret['database'] = self.ui.lineEditDatabase.text()
    ret['shot'] = self.ui.lineEditShot.text()
    ret['run'] = self.ui.lineEditRun.text()
    ret['path'] = self.ui.lineEditPath.text()
    ret['data_version'] = self.ui.lineEditVersion.text()
    
    return ret
  
  
  def GetIDS(self, ids_names, occurrence:int = 0):
    imas_obj = self.GetDBEntry('r')
    
    if imas_obj:
      imas_obj.open()
      
      ids_list = [imas_obj.get(name, occurrence = occurrence) for name in ids_names]
      
      imas_obj.close()
      
      return ids_list
    
    return []
  
  
  def SelectPath(self):
      dirTmp = QtWidgets.QFileDialog.getExistingDirectory(self, "Select folder with IMAS database files...", self.databasePath)

      if dirTmp:
        self.databasePath = dirTmp
        self.ui.lineEditPath.setText(dirTmp)
    
    
  def PutIDS(self, ids_list, occurrence:int = 0):
    imas_obj = self.GetDBEntry('w')
    
    if imas_obj:
      imas_obj.open()
      
      for ids in ids_list:
        imas_obj.put(ids, occurrence = occurrence)
      
      imas_obj.close()
  

  def SetUITextFromXML(self, lineEdit, node, defaultText=""):
    if node != None:
      lineEdit.setText(node.text)
    else:
      lineEdit.setText(defaultText)


  def SetXML(self, root):
    if (root == None):
      return
    uri = ''
    
    n_uri = root.find('uri')
    if n_uri != None:
      uri = n_uri.text
      
    self.SetUITextFromXML(self.ui.lineEditUser, root.find('user'), "")
    self.SetUITextFromXML(self.ui.lineEditDatabase, root.find('database'), "")
    self.SetUITextFromXML(self.ui.lineEditShot, root.find('pulse'), "")
    self.SetUITextFromXML(self.ui.lineEditRun, root.find('run'), "")
    self.SetUITextFromXML(self.ui.lineEditPath, root.find('path'), "")
    self.SetUITextFromXML(self.ui.lineEditVersion, root.find('data_version'), "3")

    self.ui.lineEditURI.setText(self.GetURI())


  def GetURI(self):
    uri = self.ui.lineEditURI.text()
    if (uri == ''):
      m = self.GetDBMetadata()
      if m['path'] != '':
        backend_text = self.ui.comboBoxBackend_Path.currentText()
        backends_uri = {'MDS+':'mdsplus', 'HDF5':'hdf5', 'ASCII':'ascii'}
        uri = 'imas:' + backends_uri[backend_text] + '?path=' + m['path']
      elif m['shot'] != '' and m['database'] != '':
        backend_text = self.ui.comboBoxBackend_Legacy.currentText()
        backends_id = {'MDS+':imas.imasdef.MDSPLUS_BACKEND, 'HDF5':imas.imasdef.HDF5_BACKEND, 'ASCII':imas.imasdef.ASCII_BACKEND}
        uri = imas.DBEntry.build_uri_from_legacy_parameters(backend_id = backends_id[backend_text], 
                                 pulse = int(m['shot']), 
                                 run = int(m['run']), 
                                 db_name = m['database'], 
                                 user_name = m['user'], 
                                 data_version = m['data_version'])
    
    return uri


  def SetURI(self, uri):
    self.ui.lineEditURI.setText(uri)
  

  def GetXML(self):

    root = ET.Element("root")
    node = ET.SubElement(root, "uri")
    node.text = self.GetURI()

    return root


