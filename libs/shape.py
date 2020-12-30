#!/usr/bin/python
# -*- coding: utf-8 -*-


try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.utils import distance
import sys
from math import sqrt

DEFAULT_LINE_COLOR = QColor(0, 255, 0, 128)
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 128)
DEFAULT_SELECT_LINE_COLOR = QColor(255, 255, 255)
EDIT_SELECT_LINE_COLOR = QColor(255, 0, 0)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)
DEFAULT_VERTEX_FILL_COLOR = QColor(0, 255, 0, 255)
DEFAULT_HVERTEX_FILL_COLOR = QColor(255, 0, 0)
MIN_Y_LABEL = 10


class Shape(object):
    P_SQUARE, P_ROUND = range(2)

    MOVE_VERTEX, NEAR_VERTEX = range(2)

    # The following class variables influence the drawing
    # of _all_ shape objects.
    line_color = DEFAULT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_line_color = DEFAULT_SELECT_LINE_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    hvertex_fill_color = DEFAULT_HVERTEX_FILL_COLOR
    point_type = P_ROUND
    point_size = 8
    scale = 1.0

    warning_set = ['DAHATSU', 'DAHATSUMOTORCO.,LTD.''DAHATSU MOTOR CO.,LTD.', 'オゴションコード', 'オブションコード', 'TRANS./AMLE', 'TRANS./ANLE'
                   'アブライドモデル', 'アクセル', 'BULT', 'FUJ1', 'FRME', 'FRANE', 'トリムCOLORGUARNICION', 'FAMENo.', '車号番号',
                   'MODEL0', 'cc', 'モテル', 'NO.DE CHASIS', 'DE CHASIS', 'CO.,LTD. JAPAN', 'LTD', 'WO9', 'WO1', 'TYO',\
                   'CO.LTD.JAPAN', 'MTSUBISHI','MITSUBISH', '']
    Okeys = ['TIPO', 'NO','CHASSIS NO','CHASSIS NO.','NO.', 'NO.DE', 'NO.DECHASIS',  'MODEL', 'MODEL:', 'MODELO', 'COLOR.', 'COLOR,', 'NO.:MS903081', 'NO.:MS903080', 'OCCUPANTS', 'COMM.-NO.',  'CHASSIS.-NO.',
             'COLOR', 'CORPORATION','COLOR,GUARNICION', 'COLOR,TRIM', 'カラーCOLOR,TRIM', 'GUARNICION', 'CODE', 'Option', 'トリムCOLOR,GUARNICION','PAYLOAD', 'ID.NO.:',
             'MOTOR','MOTORS', 'TOYOTA', 'CO.,LTD.', 'CO.,LTD.JAPAN', 'DAIHATSUMOTORCO.,LTD.', 'OPコード', 'OPTION', 'OPT', 'COLOR,INT',  'COLOR.INT', 'ジンMOTOR']

    # def __init__(self, label=None, subLabels=[], line_color=None, difficult=False, paintLabel=False):
    def __init__(self, label=None, subLabels=[], line_color=None, paintLabel=False, warning=False):
        self.warning = warning
        self.label = label
        self.subLabels = subLabels
        self.points = []
        self.fill = False
        self.selected = False
        self.paintLabel = paintLabel

        self._highlightIndex = None
        self._highlightMode = self.NEAR_VERTEX
        self._highlightSettings = {
            self.NEAR_VERTEX: (4, self.P_ROUND),
            self.MOVE_VERTEX: (1.5, self.P_SQUARE),
        }

        self._closed = False

        if line_color is not None:
            # Override the class line_color attribute
            # with an object attribute. Currently this
            # is used for drawing the pending line a different color.
            self.line_color = line_color

    def close(self):
        self._closed = True

    def reachMaxPoints(self):
        if len(self.points) >= 4:
            return True
        return False

    def addPoint(self, point):
        if not self.reachMaxPoints():
            self.points.append(point)

    def popPoint(self):
        if self.points:
            return self.points.pop()
        return None

    def isClosed(self):
        return self._closed

    def setOpen(self):
        self._closed = False

    def paint(self, painter):
        if self.points:
            color = self.select_line_color if self.selected else self.line_color
            if self.label in Shape.warning_set or(self.label and ( ' ' in self.label or 'ブ' in self.label)):
                color = EDIT_SELECT_LINE_COLOR
            pen = QPen(color)

            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            #self.drawVertex(vrtx_path, 0)

            for i, p in enumerate(self.points):
                if self.reachMaxPoints():
                    line_path.lineTo(p)
                self.drawVertex(vrtx_path, i)
            if self.isClosed():
                line_path.lineTo(self.points[0])

            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)

            # Draw text at the top-left
            if self.paintLabel or self.fill:
                if self.fill:
                    color = EDIT_SELECT_LINE_COLOR
                    pen = QPen(color)
                    # Try using integer sizes for smoother drawing(?)
                    pen.setWidth(max(1, int(round(2.0 / self.scale))))
                    painter.setPen(pen)
                    painter.setBackground(QColor(0,0,0))
                    painter.setBackgroundMode( Qt.OpaqueMode)

                h_box = distance(self.points[3] - self.points[0])
                min_x = sys.maxsize
                min_y = sys.maxsize
                for point in self.points:
                    min_x = min(min_x, point.x()) - h_box*0
                    min_y = min(min_y, point.y()) - h_box*0
                if min_x != sys.maxsize and min_y != sys.maxsize:
                    font = QFont()
                    size = h_box*0.7
                    size = max(20, min(size, 50))
                    font.setPointSize(size)
                    font.setBold(True)
                    painter.setFont(font)
                    if(self.label == None):
                        self.label = ""
                    if(min_y < MIN_Y_LABEL):
                        min_y += MIN_Y_LABEL
                    # painter.drawText(min_x, min_y, self.label)
                    painter.drawText(min_x, min_y, '|'.join([self.label] + self.subLabels))

            if self.fill:
                color = self.select_fill_color if self.selected else self.fill_color
                # print(color)
                # print(color.name())
                painter.fillPath(line_path, color)

    def paintNoLabel(self, painter):
        if self.points:
            color = self.select_line_color if self.selected else self.line_color
            if self.warning:
                if self.label in Shape.warning_set or(self.label and ( ' ' in self.label or 'ブ' in self.label or 'マ' in self.label)):
                    color = EDIT_SELECT_LINE_COLOR
                if self.label and 'O' in self.label and self.label not in Shape.Okeys:
                    color = EDIT_SELECT_LINE_COLOR
            pen = QPen(color)

            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)
            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            #self.drawVertex(vrtx_path, 0)

            for i, p in enumerate(self.points):
                if self.reachMaxPoints():
                    line_path.lineTo(p)
                self.drawVertex(vrtx_path, i)
            if self.isClosed():
                line_path.lineTo(self.points[0])

            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)

            if self.fill:
                color = self.select_fill_color if self.selected else self.fill_color
                # print(color)
                # print(color.name())
                painter.fillPath(line_path, color)

    def paintOnlylabel(self, painter):
        if self.points:
            color = self.select_line_color if self.selected else self.line_color
            if self.warning:
                if self.label in Shape.warning_set or(self.label and ( ' ' in self.label or 'ブ' in self.label)):
                    color = EDIT_SELECT_LINE_COLOR
            pen = QPen(color)

            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            #self.drawVertex(vrtx_path, 0)

            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)

            # Draw text at the top-left
            if self.paintLabel or self.fill:
                if self.fill:
                    color = EDIT_SELECT_LINE_COLOR
                    pen = QPen(color)
                    # Try using integer sizes for smoother drawing(?)
                    pen.setWidth(max(1, int(round(2.0 / self.scale))))
                    painter.setPen(pen)
                    painter.setBackground(QColor(0,0,0))
                    painter.setBackgroundMode( Qt.OpaqueMode)

                h_box = distance(self.points[3] - self.points[0])
                size = h_box * 0.5
                size = max(20, min(size, 50))

                # w_box = distance(self.points[1] - self.points[0])
                min_x = sys.maxsize
                min_y = sys.maxsize

                for point in self.points:
                    min_x = min(min_x, point.x())
                    min_y = min(min_y, point.y()  - size * 0.5)

                # min_x = min(min_x, self.points[0].x())  # - w_box
                # min_y = min(min_y, self.points[0].y() - size * 0.5)
                min_x = max(min_x, 0)
                min_y = max(min_y, 0)
                if min_x != sys.maxsize and min_y != sys.maxsize:
                    font = QFont()
                    font.setPointSize(size)
                    font.setBold(True)
                    painter.setFont(font)
                    if(self.label == None):
                        self.label = ""
                    if(min_y < MIN_Y_LABEL):
                        min_y += MIN_Y_LABEL
                    # painter.drawText(min_x, min_y, self.label)
                    painter.drawText(min_x, min_y, '|'.join([self.label] + self.subLabels))


    def paintForEdit(self, painter):
        # print('paintForEdit')
        if self.points:
            self.sortPoints()
            color = EDIT_SELECT_LINE_COLOR
            pen = QPen(color)
            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            draw_points = self.span_box( self.points)

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            #self.drawVertex(vrtx_path, 0)


            for i, p in enumerate(draw_points):
                line_path.lineTo(p)
                self.drawVertex(vrtx_path, i)
            if self.isClosed():
                line_path.lineTo(draw_points[0])

            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)

            # Draw text at the top-left
            if self.paintLabel:
                min_x = sys.maxsize
                min_y = sys.maxsize
                for point in self.points:
                    min_x = min(min_x, point.x())
                    min_y = min(min_y, point.y())
                if min_x != sys.maxsize and min_y != sys.maxsize:
                    font = QFont()
                    size = (self.points[3].y() - self.points[0].y())*0.5
                    font.setPointSize(size)
                    font.setBold(True)
                    painter.setFont(font)
                    if(self.label == None):
                        self.label = ""
                    if(min_y < MIN_Y_LABEL):
                        min_y += MIN_Y_LABEL
                    # painter.drawText(min_x, min_y, self.label)
                    painter.drawText(min_x, min_y, '|'.join([self.label] + self.subLabels))

            # if self.fill:
            #     color = self.select_fill_color if self.selected else self.fill_color
            #     painter.fillPath(line_path, color)\

    def convert_points_list(self, points1):
        xi1, yi1 = int(points1[0].x()), int(points1[0].y())
        xi2, yi2 = int(points1[1].x()), int(points1[1].y())
        xi3, yi3 = int(points1[2].x()), int(points1[2].y())
        xi4, yi4 = int(points1[3].x()), int(points1[3].y())

        plist = [(xi1, yi1), (xi2, yi2), (xi3, yi3), (xi4, yi4)]
        return plist

    def span_box(self, boxorgQT):
        boxorg = self.convert_points_list(boxorgQT)

        (tl, tr, br, bl) = boxorg
        spany = 3
        spanx = 3

        tl = tl[0] - spanx, tl[1] - spany

        tr = tr[0] + spanx,tr[1] - spany,

        br =br[0] + spanx, br[1] + spany

        bl = bl[0] - spanx, bl[1] + spany
        spanbox = [tl, tr, br, bl]

        points = []
        for x, y in spanbox:
            # Ensure the labels are within the bounds of the image. If not, fix them.
            # x, y, snapped = self.canvas.snapPointToCanvas(x, y)
            points.append(QPointF(x, y))

        return points

    def drawVertex(self, path, i):
        d = self.point_size / self.scale
        shape = self.point_type
        point = self.points[i]
        if i == self._highlightIndex:
            size, shape = self._highlightSettings[self._highlightMode]
            d *= size
        if self._highlightIndex is not None:
            self.vertex_fill_color = self.hvertex_fill_color
        else:
            self.vertex_fill_color = Shape.vertex_fill_color
        if shape == self.P_SQUARE:
            path.addRect(point.x() - d / 2, point.y() - d / 2, d, d)
        elif shape == self.P_ROUND:
            path.addEllipse(point, d / 2.0, d / 2.0)
        else:
            assert False, "unsupported vertex shape"

    def nearestVertex(self, point, epsilon):
        min_index = None
        min_d = None
        for i, p in enumerate(self.points):
            d = distance(p - point)
            if d <= epsilon:
                if min_d is None or d < min_d:
                    min_d = d
                    min_index = i
        return min_index

    def containsPoint(self, point):
        return self.makePath().contains(point)

    # def distance(p):
    #     return sqrt(p.x() * p.x() + p.y() * p.y())

    def minDistance(self, point):
        d0 = distance(self.points[0] - point)
        d1 = distance((self.points[1] - point))
        d2 = distance((self.points[2] - point))
        d3 = distance((self.points[3] - point))

        return min(d0, d1, d2, d3)

    def makePath(self):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        return path

    def boundingRect(self):
        return self.makePath().boundingRect()

    def moveBy(self, offset):
        self.points = [p + offset for p in self.points]

    def moveVertexBy(self, i, offset):
        self.points[i] = self.points[i] + offset

    def sortPoints(self):
        boxorg = self.convert_points_list(self.points)

        (tl, tr, br, bl) = boxorg
        if tl[1] > bl[1]:
            # print('tl[1] < bl[1]')
            spanbox = [bl, br, tr, tl]
            points = []
            for x, y in spanbox:
                points.append(QPointF(x, y))

            self.points = points
    def sortPoints_OLD2(self):
        boxorg = self.convert_points_list(self.points)

        boxorg = sorted(boxorg, key=lambda x: x[0]*x[1])
        tl = boxorg[0]
        boxorg.remove(boxorg[0])
        print('boxorg:',boxorg)
        br = boxorg[-1]
        boxorg.remove(boxorg[-1])

        boxorg = sorted(boxorg, key=lambda x: x[0])
        print('boxorg:',boxorg)
        bl = boxorg[0]
        boxorg.remove(boxorg[0])
        tr = boxorg[-1]
        boxorg.remove(boxorg[-1])

        tmp_box = [tl, tr, br, bl]
        print('tmp_box:',tmp_box)
        points = []
        for x, y in tmp_box:
            points.append(QPointF(x, y))
            self.points = points
    def sortPoints_old(self):
        boxorg = self.convert_points_list(self.points)

        boxorg = sorted(boxorg, key=lambda x: x[0]*x[1])
        tl = boxorg[0]
        boxorg.remove(boxorg[0])
        print('boxorg:',boxorg)
        br = boxorg[-1]
        boxorg.remove(boxorg[-1])

        boxorg = sorted(boxorg, key=lambda x: x[0])
        print('boxorg:',boxorg)
        bl = boxorg[0]
        boxorg.remove(boxorg[0])
        tr = boxorg[-1]
        boxorg.remove(boxorg[-1])

        tmp_box = [tl, tr, br, bl]
        print('tmp_box:',tmp_box)
        points = []
        for x, y in tmp_box:
            points.append(QPointF(x, y))
            self.points = points

    def highlightVertex(self, i, action):
        self._highlightIndex = i
        self._highlightMode = action

    def highlightClear(self):
        self._highlightIndex = None

    def copy(self):
        shape = Shape("%s" % self.label, subLabels=self.subLabels)
        shape.points = [p for p in self.points]
        shape.fill = self.fill
        shape.selected = self.selected
        shape._closed = self._closed
        if self.line_color != Shape.line_color:
            shape.line_color = self.line_color
        if self.fill_color != Shape.fill_color:
            shape.fill_color = self.fill_color
        return shape

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        self.points[key] = value
