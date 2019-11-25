import re

import sqlite3
con = sqlite3.connect('main3.db') # db='test', user='user', passwd='Passw0rd', host='localhost', port=3306)
cur = con.cursor()
cur.execute("CREATE TABLE if not exists wishlist (name text, price integer, link text, comment text, id integer primary key autoincrement) ")

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QLabel, QMessageBox
import sys


class Ui(QtWidgets.QMainWindow):

    def add_item(self, name, price, link, comment):
        rowPosition = self.item_list.rowCount()
        self.item_list.insertRow(rowPosition)
        self.item_list.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(name))
        self.item_list.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(price))
        self.item_list.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(link))
        self.item_list.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(comment))

    @staticmethod
    def check_fields_and_notify(name, price, link):
        if name == '' or len(link) < 5 or re.match(r"\d+(.\d+)?$", price) == None:
            msg = QMessageBox()
            msg.setWindowTitle('Error!')
            msg.setText("Wrong data is enetered")
            msg.exec_()
            return False
        return True

    def add_click(self):
        name, price, link, comment = self.name_edit.text(), self.price_edit.text(), self.link_edit.text(), self.comment_edit.text()

        if not self.check_fields_and_notify(name, price, link):
            return

        cur.execute(f'''insert into wishlist (name, price, link, comment) values(
                    "%s",
                    %s,
                    "%s",
                    "%s")''' % (name, price, link, comment))
        self.add_item(name, price, link, comment)
        self.last_id+=1
        self.items.append((name, price, link, comment, self.last_id))
        self.last_id+=1
        con.commit()
        print(self.last_id)

    def delete_click(self):
        rows = [i.row() for i in self.item_list.selectedItems()]
        if(len(rows)==0):
            return
        rows = list(set(rows))
        print("rows: "+str(rows))
        ids = [i[-1] for i in self.items[rows[0]:rows[-1]+1]]
        print(self.items)
        print('ids: '+str(rows))
        row = ids[0]
        for i in rows:
            print('remove '+str(i))
            self.item_list.removeRow(i)
        # print('DELETE FROM wishlist WHERE id in (%s)'%str(ids)[1:-1])
        cur.execute('DELETE FROM wishlist WHERE id in (%s)'%str(ids)[1:-1])
        print(self.items)
        self.items = self.items[:ids[0]] + self.items[ids[-1]:]
        # self.item_list.delete_row()
        for i in self.items:
            print(i)
        con.commit()

    def edit_click(self):
        selected = self.item_list.selectedItems()
        if len(selected) >= 1:

            row = selected[0].row()
            for i in selected:
                if i.row() != row:
                    return

            item = self.items[row]
            item_id = item[4]

            d=QDialog()
            d.setWindowTitle('Edit')

            save_button=QPushButton('save', d)
            save_button.move(10,180)

            name_label = QLabel('name:', d)
            name_label.move(10,5)
            name_edit=QLineEdit(item[0],d)
            name_edit.move(0,20)

            price_label = QLabel('price:', d)
            price_label.move(10,45)
            price_edit=QLineEdit(str(item[1]),d)
            price_edit.move(0,60)

            link_label = QLabel('link:', d)
            link_label.move(10,85)
            link_edit=QLineEdit(item[2],d)
            link_edit.move(0,100)

            comment_label = QLabel('comment:', d)
            comment_label.move(10,125)
            comment_edit=QLineEdit(item[3],d)
            comment_edit.move(0,140)

            def save_f():
                name, price, link, comment = (name_edit.text(), price_edit.text(), link_edit.text(), comment_edit.text())
                if not self.check_fields_and_notify(name, price, link):
                    return
                cur.execute(f'UPDATE wishlist SET name="{name}", price={price}, link="{link}", comment="{comment}" WHERE id={item_id}')
                con.commit()
                self.item_list.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
                self.item_list.setItem(row, 1, QtWidgets.QTableWidgetItem(price))
                self.item_list.setItem(row, 2, QtWidgets.QTableWidgetItem(link))
                self.item_list.setItem(row, 3, QtWidgets.QTableWidgetItem(comment))
                d.close()

            save_button.clicked.connect(save_f)

            d.exec_()
        pass

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.items = []
        self.show()

        self.name_edit = self.findChild(QtWidgets.QLineEdit, "nameEdit")
        self.price_edit = self.findChild(QtWidgets.QLineEdit, "priceEdit")
        self.link_edit = self.findChild(QtWidgets.QLineEdit, "linkEdit")
        self.comment_edit = self.findChild(QtWidgets.QLineEdit, "commentEdit")
        self.add_button = self.findChild(QtWidgets.QPushButton, "addButton")
        self.delete_button = self.findChild(QtWidgets.QPushButton, "deleteButton")
        self.edit_button = self.findChild(QtWidgets.QPushButton, "editButton")
        self.item_list = self.findChild(QtWidgets.QTableWidget, "itemList")

        self.item_list.setColumnCount(4)
        self.item_list.setRowCount(0)
        self.item_list.setHorizontalHeaderLabels(['name', 'price', 'link', 'comment'])
        self.item_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.add_button.clicked.connect(self.add_click)
        self.delete_button.clicked.connect(self.delete_click)
        self.edit_button.clicked.connect(self.edit_click)

        cur.execute('SELECT * FROM wishlist')
        current = cur.fetchall()
        cur.execute('SELECT seq FROM main.sqlite_sequence WHERE name="wishlist"')
        t = cur.fetchall()
        if(len(t)==0):
            self.last_id=0
        else:
            self.last_id=t[0][0]
        # if len(current) == 0:
        #     self.last_id = 0
        # else:
        #     self.last_id = current[-1][-1]
        for i in current:
            print(i)
            self.items.append(i)
            self.add_item(i[0], str(i[1]), i[2], i[3])


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
