""" A text editor that automatically adjusts its height to the height of the text
    in its document when managed by a layout. """

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class AutoResizingTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(AutoResizingTextEdit, self).__init__(parent)

        # This seems to have no effect. I have expected that it will cause self.hasHeightForWidth()
        # to start returning True, but it hasn't - that's why I hardcoded it to True there anyway.
        # I still set it to True in size policy just in case - for consistency.
        size_policy = self.sizePolicy()
        size_policy.setHeightForWidth(True)
        size_policy.setVerticalPolicy(QSizePolicy.Preferred)
        self.setSizePolicy(size_policy)

        self.textChanged.connect(lambda: self.updateGeometry())

    def setMinimumLines(self, num_lines):
        """ Sets minimum widget height to a value corresponding to specified number of lines
            in the default font. """

        self.setMinimumSize(self.minimumSize().width(), self.lineCountToWidgetHeight(num_lines))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        margins = self.contentsMargins()

        if width >= margins.left() + margins.right():
            document_width = width - margins.left() - margins.right()
        else:
            # If specified width can't even fit the margin, there's no space left for the document
            document_width = 0

        # Cloning the whole document only to check its size at different width seems wasteful
        # but apparently it's the only and preferred way to do this in Qt >= 4. QTextDocument does not
        # provide any means to get height for specified width (as some QWidget subclasses do).
        # Neither does QTextEdit. In Qt3 Q3TextEdit had working implementation of heightForWidth()
        # but it was allegedly just a hack and was removed.
        #
        # The performance probably won't be a problem here because the application is meant to
        # work with a lot of small notes rather than few big ones. And there's usually only one
        # editor that needs to be dynamically resized - the one having focus.
        document = self.document().clone()
        document.setTextWidth(document_width)

        return margins.top() + document.size().height() + margins.bottom()

    def sizeHint(self):
        original_hint = super(AutoResizingTextEdit, self).sizeHint()
        return QSize(original_hint.width(), self.heightForWidth(original_hint.width()))

    def lineCountToWidgetHeight(self, num_lines):
        """ Returns the number of pixels corresponding to the height of specified number of lines
            in the default font. """

        # ASSUMPTION: The document uses only the default font

        assert num_lines >= 0

        widget_margins = self.contentsMargins()
        document_margin = self.document().documentMargin()
        font_metrics = QFontMetrics(self.document().defaultFont())

        # font_metrics.lineSpacing() is ignored because it seems to be already included in font_metrics.height()
        return (
                widget_margins.top() +
                document_margin +
                max(num_lines, 1) * font_metrics.height() +
                self.document().documentMargin() +
                widget_margins.bottom()
        )

        return QSize(original_hint.width(), minimum_height_hint)
