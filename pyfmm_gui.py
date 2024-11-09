"""
    :file:     pyfmm_gui.py  
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
import sys
from scipy.ndimage import gaussian_filter
from scipy import interpolate
import pyfmm


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建 Figure 和 Canvas
        self.figure, self.axes = plt.subplots(1,1, constrained_layout=True)
        self.axes.set_aspect('equal')
        self.canvas = FigureCanvas(self.figure)

        # 绑定鼠标移动事件
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        # 绑定鼠标点击事件
        self.canvas.mpl_connect("button_press_event", self.on_mouse_click)

        # 绘图元素保留
        self.plot_handle = {}
        self.plot_handle['rays'] = []
        self.plot_handle['rcvdots'] = []

    def canvas_redraw(self):
        self.canvas.draw()

    def on_mouse_move(self, event):
        # 检查鼠标是否在坐标轴区域内
        if event.inaxes:
            x, y = event.xdata, event.ydata
            # 在状态栏或其他地方显示坐标
            self.parent().statusBar().showMessage(f"X: {x:.2f}, Y: {y:.2f}")
        else:
            self.parent().statusBar().showMessage("")

    def on_mouse_click(self, event):
        # 检查鼠标是否在坐标轴区域内
        if event.inaxes and self.TT is not None:
            x, y = event.xdata, event.ydata
            
            # 射线追踪
            rcvloc = [x, y, 0]

            travt, rays = pyfmm.raytracing(
                self.TT, [*self.srcloc, 0.0], rcvloc, self.xarr, self.yarr, self.zarr, 0.1)
            rays_hdl, = self.axes.plot(rays[:,0], rays[:,1], c='b', lw=1, ls='--')

            # 在图形上标记点击点
            dots_hdl, = self.axes.plot(x, y, 'ro', markersize=3.0)
            self.axes.set_xlim([self.xarr[0], self.xarr[-1]])
            self.axes.set_ylim([self.yarr[0], self.yarr[-1]])

            self.canvas.draw()

            self.plot_handle['rays'].append(rays_hdl)
            self.plot_handle['rcvdots'].append(dots_hdl)

            self.parent().textBrowser_rcv.append(f"{x:8.4f} {y:8.4f} {travt:6.2f}")

    def plot_velocity(self, xarr, yarr, vel2d):
        self.TT = None

        # 移除旧的 contour 和 clabel
        if hasattr(self, "contour_set"):
            self.contour_set.remove()
            del self.contour_set


        pcm = self.axes.pcolorfast(xarr, yarr, vel2d.T, cmap='jet_r')
        self.axes.set_xlim([xarr[0], xarr[-1]])
        self.axes.set_ylim([yarr[0], yarr[-1]])
        if hasattr(self, "colorbar"):
            self.colorbar.remove()
            del self.colorbar

        self.colorbar = self.figure.colorbar(pcm, shrink=0.5, pad=0.05)

        self.canvas.draw()


    def plot(self, srcloc, xarr, yarr, vel2d):
        self.srcloc = srcloc
        self.xarr = xarr
        self.yarr = yarr
        self.zarr = np.array([0.0])  # 二维情况
        self.vel2d = vel2d

        # 慢度场
        slw  = 1.0/vel2d[:,:,None]

        srcloc = [*srcloc, 0.0]

        # FMM解
        self.TT = pyfmm.travel_time_source(
            srcloc,
            self.xarr, self.yarr, self.zarr, slw)
        

        # 移除旧的 contour 和 clabel
        if hasattr(self, "contour_set"):
            self.contour_set.remove()
            del self.contour_set
        if hasattr(self, "src_dots_hdl"):
            self.src_dots_hdl.remove()
            del self.src_dots_hdl

        # 在图形上标记点击点
        self.src_dots_hdl, = self.axes.plot(srcloc[0], srcloc[1], 'ko', markersize=3.0)
        self.contour_set = self.axes.contour(self.xarr, self.yarr, self.TT[:, :, 0].T, levels=20, linewidths=0.5, colors='k')
        self.clabel_set = self.axes.clabel(self.contour_set)
        self.axes.set_xlim([self.xarr[0], self.xarr[-1]])
        self.axes.set_ylim([self.yarr[0], self.yarr[-1]])

        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)  # 加载 UI 文件

        
        self.mplwidget = MatplotlibWidget(self)

        self.mplwidget.canvas.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mplwidget.canvas.setMouseTracking(True)
        # 将 Canvas 嵌入到 layout 中
        self.verticalLayout_mpl.addWidget(self.mplwidget.canvas)
        
        # 绑定更新按钮
        self.updateSrcLocButton.clicked.connect(self.update_plot)
        self.clearRcvButton.clicked.connect(self.clear_rcv)
        self.updateVelButton.clicked.connect(self.update_velocity)

        # 定义参数
        self.plot_param = {}
        self.update_srcloc()
        self.clear_rcv()

        self.update_velocity()

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

    def delete_textBrowser_rcv_last_line(self):
        # 获取当前文本内容
        content = self.textBrowser_rcv.toPlainText()
        
        # 按行分割文本
        lines = content.split('\n')
        
        # 删除最后一行，如果有内容的话
        if lines:
            lines.pop()
        
        # 更新 QTextBrowser 内容
        self.textBrowser_rcv.setPlainText('\n'.join(lines))

    def update_velocity(self):
        namespace = {"np":np}
        exec(self.textEdit_vel.toPlainText(), namespace)
        
        self.plot_param['xarr'] = np.linspace(0, namespace['xmax'], namespace['nx']).copy()
        self.plot_param['yarr'] = np.linspace(0, namespace['ymax'], namespace['ny']).copy()
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

        # 调用 canvas 的 plot 方法刷新绘图
        self.mplwidget.plot(
            self.plot_param['srcloc'],
            self.plot_param['xarr'], self.plot_param['yarr'], self.plot_param['vel2d'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
