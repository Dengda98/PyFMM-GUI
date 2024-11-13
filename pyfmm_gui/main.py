"""
    :file:     main.py  
    :author:   Zhu Dengda (zhudengda@mail.iggcas.ac.cn)  
    :date:     2024-11

    PyFMM二维模型下的交互界面，基于PyQt5开发 

"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import os, sys
from scipy.ndimage import gaussian_filter

from .subwidget import MatplotlibWidget
from .utils import try_except_decorator, read_version


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "main.ui"), self)  # 加载 UI 文件

        # 设置标题 
        self.version = read_version()
        self.setWindowTitle(f"PyFMM-GUI   v{self.version}")
        
        self.mplwidget = MatplotlibWidget(self)

        self.mplwidget.canvas.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mplwidget.canvas.setMouseTracking(True)
        # 将 Canvas 嵌入到 layout 中
        self.verticalLayout_mpl.addWidget(self.mplwidget.canvas)
        
        # 绑定更新按钮
        self.updateSrcLocButton.clicked.connect(self.update_plot)
        self.clearRcvButton.clicked.connect(self.clear_rcv)
        self.updateVelButton.clicked.connect(self.update_velocity)
        self.redoButton.clicked.connect(self.redo_rcv)
        self.checkBox_chooseSrc.stateChanged.connect(self.choose_source_state)

        # 成员变量，确定此时的鼠标是选择震源状态还是选择接收点状态
        self.mouse_choose_source:bool = False

        # 定义参数
        self.plot_param = {}
        self.update_srcloc()
        self.clear_rcv()

        self.update_velocity()

    def write_lineEdit_src(self, x, y):
        self.lineEdit_srcX.setText(f"{x:.4f}")
        self.lineEdit_srcY.setText(f"{y:.4f}")

    def update_srcloc(self):
        self.plot_param['srcloc'] = [float(self.lineEdit_srcX.text()), float(self.lineEdit_srcY.text())]

    def clear_rcv(self):
        self.textBrowser_rcv.clear()
        self.textBrowser_rcv.append(f"{'X':>8s} {'Y':>8s} {'T':>6s}")
        for _ in range(len(self.mplwidget.plot_handle['rays'])):
            h = self.mplwidget.plot_handle['rays'].pop()
            h.remove()
            h = self.mplwidget.plot_handle['rcvdots'].pop()
            h.remove()

        self.mplwidget.canvas_redraw()

    def redo_rcv(self):
        self.delete_textBrowser_rcv_last_line()
        if len(self.mplwidget.plot_handle['rays']) == 0:
            return

        h = self.mplwidget.plot_handle['rays'].pop()
        h.remove()
        h = self.mplwidget.plot_handle['rcvdots'].pop()
        h.remove()
        self.mplwidget.canvas_redraw()

    def delete_textBrowser_rcv_last_line(self):
        # 获取当前文本内容
        content = self.textBrowser_rcv.toPlainText()
        
        # 按行分割文本
        lines = content.split('\n')
        
        # 删除最后一行，保留X，Y，T，如果有内容的话
        if len(lines) > 1:
            lines.pop()
        
        # 更新 QTextBrowser 内容
        # self.textBrowser_rcv.setPlainText('\n'.join(lines))
        self.textBrowser_rcv.setPlainText("")
        for line in lines:
            self.textBrowser_rcv.append(line)

    def choose_source_state(self, state):
        if state == 2:  # 选中
            self.mouse_choose_source = True 
        else:
            self.mouse_choose_source = False

    @try_except_decorator("statusBar")
    def update_velocity(self, *args):
        namespace = {"np":np}
        exec(self.textEdit_vel.toPlainText(), namespace)
        
        # self.plot_param['xarr'] = np.linspace(0, namespace['xmax'], namespace['nx']).copy()
        # self.plot_param['yarr'] = np.linspace(0, namespace['ymax'], namespace['ny']).copy()
        # vel2d = namespace['vel2d'].copy()
        self.plot_param['xarr'] = namespace['xarr'].copy()
        self.plot_param['yarr'] = namespace['yarr'].copy()
        vel2d = namespace['vel2d'].copy()
        vel2d[vel2d < 0.0] = 0.1
        self.plot_param['vel2d'] = vel2d

        self.clear_rcv()
        self.mplwidget.plot_velocity(self.plot_param['xarr'], self.plot_param['yarr'], self.plot_param['vel2d'])
        self.update_plot()

    def update_plot(self):
        # 读入参数
        self.update_srcloc()

        self.clear_rcv()

        # 衡量范围
        if self.plot_param['srcloc'][0] > self.plot_param['xarr'][-1] or \
           self.plot_param['srcloc'][0] < self.plot_param['xarr'][0] or \
           self.plot_param['srcloc'][1] > self.plot_param['yarr'][-1] or \
           self.plot_param['srcloc'][1] < self.plot_param['yarr'][0]:
            
           self.statusBar().showMessage(f"source location out of bound!", 3000)
           return

        self.statusBar().showMessage(f"Fast Marcing ......")
        QApplication.processEvents()  # 强制刷新事件循环
        # 调用 canvas 的 plot 方法刷新绘图
        self.mplwidget.plot(
            self.plot_param['srcloc'],
            self.plot_param['xarr'], self.plot_param['yarr'], self.plot_param['vel2d'])
        self.statusBar().showMessage(f"Done.", 1000)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
