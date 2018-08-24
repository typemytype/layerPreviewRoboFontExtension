from vanilla import *
from AppKit import NSColor

from defconAppKit.windows.baseWindow import BaseWindowController

from glyphLayerPreview import GlyphLayerPreview
from mojo.events import addObserver, removeObserver

from mojo.roboFont import *


class LayerWindow(BaseWindowController):

    def __init__(self):

        self.w = Window((420, 400), "Layer Preview", minSize=(420, 300))

        self.w.preview = GlyphLayerPreview((0, 0, -0, -30))
        self.currentGlyphChanged()

        self.w.useColor = CheckBox((10, -30, 100, 22), "Use Color:", callback=self.useColorCallback)

        self.w.color = ColorWell((100, -35, 40, 30), color=NSColor.blackColor(), callback=self.colorCallback)

        self.w.splitLayers = Button((-260, -30, -160, 22), "Split Layers", callback=self.splitLayerCallback)
        self.w.testInstall = Button((-150, -30, -10, 22), "Test Install Layers", callback=self.testInstallCallback)

        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")

        self.setUpBaseWindowBehavior()
        self.w.open()

    def currentGlyphChanged(self, notification=None):
        self.w.preview.setGlyph(CurrentGlyph())

    def windowCloseCallback(self, sender):
        removeObserver(self, "currentGlyphChanged")
        super(LayerWindow, self).windowCloseCallback(sender)

    def useColorCallback(self, sender):
        value = sender.get()
        self.w.color.enable(value)
        if value:
            color = self.w.color.get()
        else:
            color = None
        self.w.preview.setColor(color)

    def colorCallback(self, sender):
        self.useColorCallback(self.w.useColor)

    def _getLayerFonts(self, font):
        familyName = font.info.familyName
        styleName = font.info.styleName
        if familyName is None or styleName is None:
            self.showMessage("Font needs a family name and style name.", "Please name it correctly")
            return []

        layerFonts = []
        for layerName in font.layerOrder:
            layerFont = NewFont(showInterface=False)
            layerFont.info.update(font.info)
            layerFont.info.styleName = "%s %s" % (font.info.styleName, layerName)

            layerFont.kerning.update(font.kerning)
            layerFont.groups.update(font.groups)

            for glyph in font:
                layerGlyph = glyph.getLayer(layerName)
                layerFont[glyph.name] = layerGlyph.copy()
            layerFonts.append(layerFont)

        return layerFonts

    def splitLayerCallback(self, sender):
        font = CurrentFont()
        layerFonts = self._getLayerFonts(font)
        for layerFont in layerFonts:
            layerFont.openInterface()

    def testInstallCallback(self, sender):
        font = CurrentFont()
        layerFonts = self._getLayerFonts(font)
        if layerFonts:
            font.testInstall()
            for layerFont in layerFonts:
                layerFont.testInstall()


LayerWindow()
