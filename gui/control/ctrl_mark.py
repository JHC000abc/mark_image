# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@contact: JHC000abc@gmail.com
@file: ctrl_mark.py
@time: 2023/2/4 13:02 $
@desc:

"""
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from PyQt5.QtGui import QPixmap, QTransform

from gui.ui import mark
from util.util_mark import MarkImage
from threading import Thread


class Mark(QtWidgets.QWidget):
    single = QtCore.pyqtSignal()
    single_label_pic_info = QtCore.pyqtSignal(dict)
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = mark.Ui_Form()
        self.ui.setupUi(self)

        self.IMG_TAIL_LIST = ["png", "jpg"]
        self.IMG_LIST = []
        self.IMG_NUM = 0
        self.wait_mark_list = []
        self.wait_mark = 0
        self._init_ui()
        self._init_slot()
        self._init_status()

    def _init_ui(self):
        self.ui.groupBox_whirl_choice.hide()
        self.ui.groupBox_choice_mark_path.hide()
        self.ui.groupBox_date_from.hide()
        self.ui.label_pic_info.hide()
        self.ui.groupBox_mark_functions.hide()
        self.ui.pushButton_mark_next.hide()
        self.ui.pushButton_mark_all.hide()

        self.ui.pushButton_save.show()
        self.ui.pushButton_next.show()
        self.ui.pushButton_last.show()

        # 自适应
        self.ui.label_path_show.adjustSize()
        # 换行
        self.ui.label_path_show.setWordWrap(True)

        self.setWindowTitle("图像标注软件")
        self.ui.label_img_review.setScaledContents(True)

    def _init_slot(self):
        self.ui.radioButton_img_whirl.clicked.connect(self.slot_img_whirl)
        self.ui.radioButton_mark_one.clicked.connect(self.slot_mark_one)

        self.ui.radioButton_txt.clicked.connect(self.slot_txt)
        self.ui.radioButton_excel.clicked.connect(self.slot_excel)

        self.ui.pushButton_choice_mark_path.clicked.connect(
            self.slot_choice_mark_path)

        self.ui.pushButton_zoom_increase.clicked.connect(
            self.slot_zoom_increase)
        self.ui.pushButton_zoom_reduce.clicked.connect(self.slot_zoom_reduce)

        self.ui.pushButton_next.clicked.connect(self.slot_next)
        self.ui.pushButton_last.clicked.connect(self.slot_last)
        self.ui.pushButton_save.clicked.connect(self.slot_save)

        self.ui.pushButton_mark_all.clicked.connect(self.mark_all)
        self.ui.pushButton_mark_next.clicked.connect(self.mark_next)
        self.ui.pushButton_config_finish.clicked.connect(self.config_finish)

        self.single.connect(self.next_eable)
        self.single_label_pic_info.connect(self.sing_label_pic_info)

    def slot_img_whirl(self):
        if self.ui.radioButton_img_whirl.isChecked():
            self.status_whirl = True
            self.status_mark = False
            self.change_groupBox_whirl_choice_status()

    def slot_mark_one(self):
        if self.ui.radioButton_mark_one.isChecked():
            self.status_mark = True
            self.status_whirl = False
            self.change_groupBox_whirl_choice_status()

    def change_groupBox_whirl_choice_status(self):
        if self.status_whirl:
            self.status_mark = False
            self.ui.label_path_show.clear()
            # self.ui.groupBox_date_from.hide()
            self.hide_all()
            self.ui.groupBox_choice_mark_path.show()
            self.ui.pushButton_save.show()
            self.ui.pushButton_next.show()
            self.ui.pushButton_last.show()
            self.ui.pushButton_mark_next.hide()
            self.ui.pushButton_mark_all.hide()
            self.ui.pushButton_config_finish.setDisabled(False)

        if self.status_mark:
            self.status_whirl = False
            # self.ui.groupBox_choice_mark_path.hide()
            self.hide_all()
            self.ui.groupBox_date_from.show()
            self.ui.pushButton_save.hide()
            self.ui.pushButton_next.hide()
            self.ui.pushButton_last.hide()
            self.ui.pushButton_mark_next.show()
            self.ui.pushButton_mark_all.show()

    def hide_all(self):
        """

        :return:
        """
        self.ui.groupBox_choice_mark_path.hide()
        self.ui.groupBox_date_from.hide()
        self.ui.groupBox_whirl_choice.hide()
        self.ui.groupBox_mark_functions.hide()
        self.IMG_LIST.clear()
        self.IMG_NUM = 0
        self.img = ""
        self.ui.label_pic_info.clear()
        self.ui.label_img_review.clear()
        self.ui.label_img_review.setText("    图像预览")
        self.ui.pushButton_mark_next.hide()
        self.ui.pushButton_mark_all.hide()
        self.ui.pushButton_config_finish.hide()

    def _init_status(self):
        """
        最初界面状态，默认选择图像旋转功能
        :return:
        """
        self.ui.radioButton_img_whirl.click()
        self.status_whirl = True
        self.status_mark = False
        self.slot_img_whirl()
        self.slot_mark_one()

    def slot_choice_mark_path(self):
        """

        :return:
        """
        folder_path = self.selectPath()
        self.folder_path = folder_path
        text_label_path_show = self.ui.label_path_show.text()
        if folder_path == "" and text_label_path_show == "":
            self.show_message("未选择路径，请重新选择")
        else:
            if folder_path != "":
                self.ui.label_path_show.setText(folder_path)
            else:
                self.ui.label_path_show.setText(text_label_path_show)

            if self.status_mark:
                print("选择数据源")
                self.ui.groupBox_choice_mark_path.hide()
                self.ui.groupBox_mark_functions.show()
                self.ui.pushButton_config_finish.show()
                print("folder_path",folder_path)

            if self.status_whirl:
                self.ui.pushButton_config_finish.hide()
                self.__whirl_pic(folder_path)

    def select_mark_function(self):
        """

        :return:
        """
        if self.ui.checkBox_box.isChecked():
            self.box = True
        else:
            self.box = False

        if self.ui.checkBox_num.isChecked():
            self.index_num = True
        else:
            self.index_num = False

        if self.ui.checkBox_text.isChecked():
            self.text = True
        else:
            self.text = False

        if self.ui.checkBox__text_opt.isChecked():
            self.text_opt = True
        else:
            self.text_opt = False

    def init_mi(self):
        self.mi.TEXT = self.text
        self.mi.BOX = self.box
        self.mi.INDEX = self.index_num
        self.mi.num_opt = self.text_opt
        return self.mi

    def mark_next(self):
        """

        :return:
        """
        print("self.wait_mark",self.wait_mark+1,len(self.wait_mark_list))
        if self.wait_mark+1 > len(self.wait_mark_list):
            self.show_message("标注完成")
        else:
            self.ui.pushButton_mark_next.setDisabled(True)
            file, map_lis, save_file = self.wait_mark_list[self.wait_mark]
            mark_info = self.mi.process(file, map_lis, save_file)
            Thread(target=self.show_mark_result,args=(mark_info,)).start()
            self.wait_mark += 1

    def next_eable(self):
        self.ui.pushButton_mark_next.setDisabled(False)

    def sing_label_pic_info(self,mark_info):
        self.ui.label_pic_info.show()
        self.ui.label_pic_info.setText(mark_info["origin_file"])
        self.img = QPixmap(mark_info["up_file"])
        # 图像适用label大小
        self.img = self.img.scaled(600, 580, aspectRatioMode=Qt.KeepAspectRatio)
        self.load_img()
        self.single.emit()

    def show_mark_result(self,mark_info):
        self.single_label_pic_info.emit(mark_info)



    def mark_all(self):
        """

        :return:
        """
        for index,value in enumerate(self.wait_mark_list):
            if index >= self.wait_mark:
                file, map_lis, save_file = value
                mark_info = self.mi.process(file, map_lis, save_file)
                Thread(target=self.show_mark_result, args=(mark_info,)).start()
            else:
                pass
            self.wait_mark += 1
        self.show_message("标注完成")


    def __mark_pic(self,_path):
        origin_path = os.path.join(_path,"origin")
        result_path = os.path.join(_path, "result")
        mark_path = os.path.join(_path,"mark")
        os.makedirs(mark_path,exist_ok=True)
        for file_name in os.listdir(origin_path):
            name = file_name.split(".")[0]
            # self.IMG_LIST.insert(0,[os.path.join(origin_path,file_name),name])
            map_lis = self.mi.process_input_answer(file=os.path.join(result_path,name+".txt"))
            save_file = os.path.join(mark_path,name+".jpg")
            self.wait_mark_list.insert(0,[os.path.join(origin_path,name+".jpg"),map_lis,save_file])

            #
            # print("mark_info",mark_info)
        # return mark_info


    def config_finish(self):
        """

        :return:
        """
        try:
            self.ui.pushButton_config_finish.setDisabled(True)
            self.mi = MarkImage()
            self.select_mark_function()
            self.init_mi()
            self.__mark_pic(self.folder_path)
        except:
            pass

    def __whirl_pic(self, _path):
        """

        :param _path:
        :return:
        """
        for name in os.listdir(_path):
            file_tail = name.lower().split(".")[-1]
            if file_tail in self.IMG_TAIL_LIST:
                img_file = os.path.join(_path, name)

                self.IMG_LIST.insert(0, [img_file, name])

        if len(self.IMG_LIST) > 0:
            self.ui.groupBox_choice_mark_path.hide()
            self.ui.groupBox_whirl_choice.show()
            self.get_show_img()
        else:
            self.show_message("选择的路径下不存在图片，请重新选择")
            self.ui.label_path_show.clear()
            self.ui.label_path_show.clear()

    def get_show_img(self):
        """

        :return:
        """
        img_show_file = self.IMG_LIST[self.IMG_NUM][0]
        self.ui.label_pic_info.setText(
            self.IMG_LIST[self.IMG_NUM][-1] + "({}/{})".format(self.IMG_NUM + 1, len(self.IMG_LIST)))
        self.ui.label_pic_info.show()
        self.img = QPixmap(img_show_file)
        self.load_img()

    def load_img(self):
        """

        :return:
        """
        self.ui.label_img_review.clear()
        self.ui.label_img_review.setPixmap(self.img)
        self.ui.label_img_review.setScaledContents(False)

    def selectPath(self):
        """

        :return:
        """
        str_path = QFileDialog.getExistingDirectory(None, "选取文件夹", "")
        return str_path

    def slot_txt(self):
        """

        :return:
        """
        print("txt")
        self.__init_groupBox_date_from()

    def slot_excel(self):
        """

        :return:
        """
        print("excel")
        self.__init_groupBox_date_from()

    def rotate_img(self, route):
        """

        :param route:
        :return:
        """
        transform = QTransform()
        transform.rotate(route)
        self.img = self.img.transformed(transform)
        self.load_img()

    def slot_zoom_reduce(self):
        """

        :return:
        """
        self.rotate_img(270)

    def slot_zoom_increase(self):
        """

        :return:
        """
        self.rotate_img(90)

    def slot_next(self):
        """

        :return:
        """
        if self.IMG_NUM >= len(self.IMG_LIST) - 1:
            self.show_message("已经是最后一张了")
        else:
            self.IMG_NUM += 1
            self.__change_view_after_change_pic()

    def slot_last(self):
        """

        :return:
        """
        if self.IMG_NUM <= 0:
            self.show_message("已经是第一张了")
        else:
            self.IMG_NUM -= 1
            self.__change_view_after_change_pic()

    def __change_view_after_change_pic(self):
        self.ui.label_img_review.clear()
        self.ui.label_pic_info.clear()
        self.get_show_img()
        self.ui.label_pic_info.show()

    def slot_save(self):
        """

        :return:
        """
        save_img_name = self.ui.label_pic_info.text()
        save_path = R"./Image_rotation"
        os.makedirs(save_path, exist_ok=True)
        save_img_file = os.path.join(save_path, save_img_name)
        try:
            self.img.save("{}.jpg".format(save_img_file))
            self.show_message("图像导出成功,保存位置:{}".format(save_img_file))
        except Exception as e:
            self.show_message("{} 导出失败,原因:{}".format(save_img_name, e))
            # print("{} 导出失败,原因:{}".format(save_img_name,e))

    def __init_groupBox_date_from(self):
        self.ui.groupBox_date_from.hide()
        self.ui.label_path_show.clear()
        self.ui.groupBox_choice_mark_path.show()

    def show_message(self, msg, title="提示"):
        QMessageBox.information(self, title, msg, QMessageBox.Yes)
