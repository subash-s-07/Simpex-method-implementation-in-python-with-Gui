from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout,QLabel,QComboBox,QPushButton,QHBoxLayout,QSizePolicy
import sympy
import numpy as np
import simply
M = sympy.Symbol('M', positive=True)
HEADER_SPACE=11

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Simplex Solver")
        self.CONSTRAINT_EQUALITY_SIGNS = [u"\u2264", u"\u2265", "="]#you can choose either <=,>=,= for constraint
        self.new_widgets = []#list to keep track of all new widgets created(like those to show iteration so that they can easily be deleted
        #when a new problem is given

        self.create_ui()
        self.set_ui_layout()

        self.setFixedWidth(self.sizeHint().width()+100)
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMinimizeButtonHint)

    def create_ui(self):
        self.objective_function_label = QLabel("Objective function", self)
        self.objective_function_label.setFixedHeight(self.objective_function_label.sizeHint().height())
        self.objective_fxn_table = self.create_table(1, 4, ["="], self.create_header_labels(2))

        z_item = QTableWidgetItem("Z")
        self.objective_fxn_table.setItem(0, 3, z_item)
        z_item.setFlags(Qt.ItemIsEnabled)

        #make the objective fxn table's size fit perfectly with the rows
        self.objective_fxn_table.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.objective_fxn_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.objective_fxn_table.resizeColumnsToContents()
        self.objective_fxn_table.setFixedHeight(self.objective_fxn_table.verticalHeader().length()+self.objective_fxn_table.horizontalHeader().height())

        self.constraints_label = QLabel("Constraints Matrix", self)
        self.constraints_label.setFixedHeight(self.constraints_label.sizeHint().height())
        self.constraint_table = self.create_table(2, 4, self.CONSTRAINT_EQUALITY_SIGNS, self.create_header_labels(2))
        self.constraint_table.setFixedHeight(self.constraint_table.sizeHint().height())

        self.answers_label = QLabel()

        self.add_row_btn = QPushButton('Add Row', self)
        self.add_row_btn.clicked.connect(self.add_row_event)
        self.add_col_btn = QPushButton('Add Column', self)
        self.add_col_btn.clicked.connect(self.add_column_event)
        self.del_row_btn = QPushButton("Delete Row", self)
        self.del_row_btn.clicked.connect(self.del_row_event)
        self.del_col_btn = QPushButton("Delete Column", self)
        self.del_col_btn.clicked.connect(self.del_col_event)
        self.solve_btn = QPushButton('Solve', self)
        self.solve_btn.clicked.connect(self.solve_event)

        self.operation_combo = QComboBox()
        for item in ["Maximize", "Minimize"]:
            self.operation_combo.addItem(item)

    def set_ui_layout(self):
        vbox_layout1 = QHBoxLayout(self)
        self.vbox_layout2 = QVBoxLayout(self)

        vbox_layout1.addWidget(self.add_row_btn)
        vbox_layout1.addWidget(self.add_col_btn)
        vbox_layout1.addWidget(self.del_row_btn)
        vbox_layout1.addWidget(self.del_col_btn)
        vbox_layout1.addWidget(self.operation_combo)
        vbox_layout1.addWidget(self.solve_btn)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_v_layout = QVBoxLayout(self)
        central_widget.setLayout(main_v_layout)

        self.vbox_layout2.addWidget(self.objective_function_label)
        self.vbox_layout2.addWidget(self.objective_fxn_table)
        self.vbox_layout2.addWidget(self.constraints_label)
        self.vbox_layout2.addWidget(self.constraint_table)
        self.vbox_layout2.addWidget(self.answers_label)

        main_v_layout.addLayout(vbox_layout1)
        main_v_layout.addLayout(self.vbox_layout2)

    def create_table(self, rows, cols,equality_signs=None, horizontal_headers=None,vertical_headers=None):
        table = QTableWidget(self)
        table.setColumnCount(cols)
        table.setRowCount(rows)

        # Set the table headers
        if horizontal_headers:
            table.setHorizontalHeaderLabels(horizontal_headers)

        if vertical_headers:
            table.setVerticalHeaderLabels(vertical_headers)

        #add <=,>=,= signs so that person can select the whether that constraint is <=,>= or =
        #its also used for the objective fxn but in the objective fxn we just use = Z so an [=] sign is passed
        #for equality signs in the creation of the objective fxn table in the create_ui function
        if equality_signs:
            numofrows = table.rowCount()
            numofcols = table.columnCount()
            # add combo items to self.constraint_table
            for index in range(numofrows):
                equality_signs_combo = QComboBox()
                for item in equality_signs:
                    equality_signs_combo.addItem(item)
                table.setCellWidget(index, numofcols - 2, equality_signs_combo)

        # Do the resize of the columns by content
        table.resizeColumnsToContents()
        table.resizeRowsToContents()        
        return table

    def create_header_labels(self,num_of_variables):
        """Name the columns for the tables x1,x2,.... give a space and then add bi"""
        header_labels = [" "*HEADER_SPACE +"x" + str(i + 1) + " " * HEADER_SPACE for i in range(num_of_variables)]
        header_labels.extend([" " * HEADER_SPACE, " " * HEADER_SPACE + "bi" + " " * HEADER_SPACE])
        return header_labels

    def del_row_event(self):
        #allow a maximum of one constraint
        if self.constraint_table.rowCount()>1:
            self.constraint_table.removeRow(self.constraint_table.rowCount()-1)

    def del_col_event(self):
        #if we have x1,x2 and the signs and bi column don't allow deletion of column, else delete
        if self.constraint_table.columnCount()>4:
            self.constraint_table.removeColumn(self.constraint_table.columnCount()-3)
            self.objective_fxn_table.removeColumn(self.objective_fxn_table.columnCount()-3)

    def add_column_event(self):
        self.constraint_table.insertColumn(self.constraint_table.columnCount()-2)
        self.objective_fxn_table.insertColumn(self.objective_fxn_table.columnCount()-2)
        self.constraint_table.setHorizontalHeaderLabels(self.create_header_labels(self.constraint_table.columnCount()-2))
        self.objective_fxn_table.setHorizontalHeaderLabels(self.create_header_labels(self.constraint_table.columnCount()-2))

        # make the objective fxn table's size fit perfectly with the rows and columns
        self.objective_fxn_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.objective_fxn_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.objective_fxn_table.setFixedHeight(self.objective_fxn_table.verticalHeader().length() + self.objective_fxn_table.horizontalHeader().height())

    def add_row_event(self):
        self.constraint_table.insertRow(self.constraint_table.rowCount())
        equality_signs_combo = QComboBox()
        for item in self.CONSTRAINT_EQUALITY_SIGNS:
            equality_signs_combo.addItem(item)
        self.constraint_table.setCellWidget(self.constraint_table.rowCount()-1,self.constraint_table.columnCount() - 2, equality_signs_combo)
        self.constraint_table.resizeRowsToContents()


    def solve_event(self):
        tablee = self.form_unaugmented_matrix()
       
       
        tab = np.flip(tablee)
        tab = tab.tolist()
        #print(tab)
       
        rowc = len(tab)
       
        l = []
        soln = []
       
        for i in  tab:
            soln.append(i[-1])
            l.append(i[:-1])
        #print("List",l)

        artifical = np.identity(rowc-1)
        artifical = artifical.tolist()
        artifical = artifical[::-1]
        print(artifical)

        weird = []
        zeros = np.zeros(rowc-1).tolist()
        for i in range(rowc):
            if (i==rowc-1):
                temp = l[i][::-1] + zeros + [0]
            else:
                temp = l[i][::-1] + artifical[i] + [soln[i]]
            weird.append(temp)
        weird = weird[::-1]
        #zvalue make  -ve
        for i in range(len(weird[0])):
            weird[0][i] = -1*weird[0][i]
        opr = self.operation_combo.currentText()
        dic1 = {}

        xivalues = ['x1','x2','x3','x4','x5','x6']
        sivalues = ['s1','s2','s3','s4','s5','s6']
        zopt = 'z'

        intialtab = [zopt]+sivalues[:rowc-1]
        for i in range(len(intialtab)):
            dic1[intialtab[i]] = weird[i]
        print("dic1",dic1)


        l4 = xivalues[:rowc-1] + sivalues[:rowc-1]
        l1 = weird
        if(opr == 'Minimize'):
            print("hi")
            def irration1(l,dic,l4):
                minimum=max(l[0][:-1])
                z=l[0].index(minimum)
                length=len(l[0])
                ratio=[]
                for i in l:
                    if(i[z]!=0 and i[z]>0):
                        ratio.append(i[length-1]/i[z])
                    else:
                        ratio.append(10000)
                #print(ratio[1:])
                z1=min(ratio[1:])
                #print(z1)
                pivot_column_index=z
                pivot_row_index=ratio.index(z1)
                pivot_row=l[ pivot_row_index]
                #print(pivot_row)
                pivot=l[pivot_row_index][pivot_column_index]
                new_pivot_row=[]
                for i in pivot_row:
                    new_pivot_row.append(i/pivot)
                #print(new_pivot_row)
                new_table=[]
                #print(l)
                for i in range(len(l)):
                    temp=[]
                    for j in range(len(l[0])):
                        if(i!=pivot_row_index):
                            temp.append(l[i][j]-l[i][pivot_column_index]*new_pivot_row[j])
                        else:
                            temp.append(new_pivot_row[j])
                    new_table.append(temp)
                d={}
                d1=list(dic)
                for i in range(len(new_table)):
                    if i==pivot_row_index:
                        d[l4[z]]=new_table[i]
                    else:
                        d[d1[i]]=new_table[i]
                print(d)
                return d
            m=max(l1[0])
            print("Iteration 1 :")
            print(l1)
            print(m)
            c=1
            d=[dic1]
            while((m>0) and (m!=0)):
                    print("Iteration ",c,":")
                    d2=irration1(l1,dic1,l4)
                    d.append(d2)
                    l2=list(d2.values())
                    for i in l2:
                        print(i)
                    m=max(l2[0])
                    dic1=d2
                    l1=l2
                    c=c+1
            l5=l4
            l5.append('Solution')
            simply.display(d,l5)
        else:
            def irration(l,dic,l4):
                minimum=min(l[0][:-1])
                z=l[0].index(minimum)
                length=len(l[0])
                ratio=[]
                for i in l:
                    if(i[z]!=0 and i[z]>0):
                        ratio.append(i[length-1]/i[z])
                    else:
                        ratio.append(10000)
                #print(ratio)
                z1=min(ratio[1:])
                #print(z1)
                pivot_column_index=z
                pivot_row_index=ratio.index(z1)
                pivot_row=l[pivot_row_index]
                #print(pivot_row)
                pivot=l[pivot_row_index][pivot_column_index]
                new_pivot_row=[]
                for i in pivot_row:
                    new_pivot_row.append(i/pivot)
                #print(new_pivot_row)
                new_table=[]
                #print(l)
                for i in range(len(l)):
                    temp=[]
                    for j in range(len(l[0])):
                        if(i!=pivot_row_index):
                            temp.append(l[i][j]-l[i][pivot_column_index]*new_pivot_row[j])
                        else:
                            temp.append(new_pivot_row[j])
                    new_table.append(temp)
                d={}
                d1=list(dic)
                for i in range(len(new_table)):
                    if i==pivot_row_index:
                        d[l4[z]]=new_table[i]   
                    else:
                        d[d1[i]]=new_table[i]
                print(d)
                return d
                    
            

            #l2=[-2,-3,0,0,0]       #z
            #l1=[[-2,-3,0,0,0],[2,1,1,0,4],[1,2,0,1,5]]          #z along with basic variables
            #dic1={'z':[-2,-3,0,0,0],'s1':[2,1,1,0,4],'s2':[1,2,0,1,5]}
            
            #l4=['x1','x2','s1','s2']
            #print(dic1.values)
            m=min(l1[0])
            print("Iteration 1 :")
            print(l1)
            print(m)
            c=1
            d=[dic1]
            while((m<0) and (m!=0)):
                print("Iteration ",c,":")
                d2=irration(l1,dic1,l4)
                d.append(d2)
                l2=list(d2.values())
                for i in l2:
                    print(i)
                m=min(l2[0])
                dic1=d2
                l1=l2
                c=c+1
            l5=l4
            l5.append('Solution')
            simply.display(d,l5)
        






        #----------------------------------------------------------------------------------------------------------------------
        #delete any new widgets created when a problem was being solved such as the iteration's table
        """waring
                w = QWidget()
                QMessageBox.warning(w, "Warning","Problem is unbounded. Check problem formulation. Showing only iterations.")
                self.answers_label.setText(" ")
                break"""

    def form_unaugmented_matrix(self):
        obj_fxn = self.get_obj_fxn()
        table = self.constraint_table
        split1_of_constraints = self.read_table_items(self.constraint_table, 0, self.constraint_table.rowCount(), 0,
                                                      self.constraint_table.columnCount() - 2)
        split2_of_constraints = self.read_table_items(self.constraint_table, 0, self.constraint_table.rowCount(),
                                                      self.constraint_table.columnCount() - 1,
                                                      self.constraint_table.columnCount())
        unaugmented_matrix_without_obj_fxn = np.concatenate((np.array(split2_of_constraints), split1_of_constraints),
                                                            axis=1)
        unaugmented_matrix = np.vstack((obj_fxn, unaugmented_matrix_without_obj_fxn))
        return unaugmented_matrix

    def read_table_items(self,table,start_row,end_row,start_col, end_col):
        read_table = np.zeros((end_row-start_row, end_col-start_col),dtype=sympy.Symbol)
        for i in range(start_row,end_row):
            for j in range(start_col,end_col):
                read_table[i-end_row][j-end_col] = float(table.item(i, j).text())

        return read_table
   
   
   
   
   
   

    def read_equality_signs(self,equality_signs_column,table):
        equality_signs=[]
        for i in range(table.rowCount()):
            equality_signs.append(table.cellWidget(i, equality_signs_column).currentText())
        return equality_signs

    def populatetable(self,table, mylist, start_row, end_row, start_col, end_col):
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                table.setItem(i, j, QTableWidgetItem(str(mylist[i - end_row][j - end_col])))
        table.resizeColumnsToContents()

    def get_obj_fxn(self):
        obj_fxn_coeff=self.read_table_items(self.objective_fxn_table, 0,self.objective_fxn_table.rowCount(), 0, self.objective_fxn_table.columnCount()-2)
        obj_fxn = np.insert(obj_fxn_coeff,0,0)
        return obj_fxn

    def create_gui_for_tableau(self,tableau,all_variables,vertical_headers):
        rows,cols=tableau.shape
        gui_tableau=self.create_table(rows, cols, equality_signs=None,horizontal_headers=all_variables,vertical_headers=vertical_headers)
        self.populatetable(gui_tableau, tableau, 0,rows, 0, cols)
        return gui_tableau

    def update_gui_tableau(self,tableau,gui_tableau,current_row,vertical_headers):
        #create new rows and cols
        rows, cols = tableau.shape
        for i in range(rows):
            gui_tableau.insertRow(gui_tableau.rowCount())
        self.populatetable(gui_tableau, tableau, current_row, current_row+rows, 0,cols)
        gui_tableau.setVerticalHeaderLabels(vertical_headers)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())