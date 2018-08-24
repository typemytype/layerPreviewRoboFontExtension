import AppKit

from mojo.glyphPreview import GlyphPreview

from mojo.roboFont import version

inRF3 = version >= "3.0"

if inRF3:
    from mojo.glyphPreview import RFGlyphPreviewView
else:
    from mojo.glyphPreview import GlyphPreviewView as RFGlyphPreviewView


class GlyphLayerPreviewView(RFGlyphPreviewView):

    def init(self):
        super(GlyphLayerPreviewView, self).init()
        self._color = None
        return self

    def setColor_(self, color):
        self._color = color
        self.refresh()

    def drawRect_(self, rect):
        if self.inLiveResize():
            self.calculateScale()

        if self._glyph is None:
            return

        transform = AppKit.NSAffineTransform.transform()
        transform.translateXBy_yBy_(0, self._buffer)
        transform.concat()

        transform = AppKit.NSAffineTransform.transform()
        transform.scaleBy_(self._scale)
        transform.translateXBy_yBy_(0, self._descender)
        transform.concat()

        flipTransform = AppKit.NSAffineTransform.transform()
        flipTransform.translateXBy_yBy_(self._shift, self._upm)
        flipTransform.scaleXBy_yBy_(1.0, -1.0)
        flipTransform.concat()

        glyph = self._glyph
        if not inRF3:
            if glyph.isLayer():
                glyph = glyph.getBaseGlyph()

        if inRF3:
            layer = glyph.layer
        else:
            layer = glyph.getParent()

        if self._color is not None:
            self._color.set()

        if inRF3:
            layerNames = layer.layerSet.layerOrder
        else:
            layerNames = ["foreground"] + layer.layerOrder

        for layerName in reversed(layerNames):
            if inRF3:
                layerGlyph = glyph.getLayerGlyph(layerName)
                layerColor = layerGlyph.layer.color
                if layerColor:
                    color = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(layerColor.r, layerColor.g, layerColor.b, layerColor.a)
                else:
                    color = AppKit.NSColor.blackColor()
            else:
                layerGlyph = glyph.getLayer(layerName)
                color = layer.getLayerColor(layerName)

            if self._color is None:
                color.set()

            path = layerGlyph.getRepresentation("defconAppKit.NSBezierPath")

            path.fill()

        if self._selection:
            selectionPath = AppKit.NSBezierPath.bezierPath()
            radius = 3 / self._scale
            for x, y in self._selection:
                selectionPath.appendBezierPathWithOvalInRect_(AppKit.NSMakeRect(x - radius, y - radius, radius * 2, radius * 2))

            AppKit.NSColor.redColor().set()
            selectionPath.fill()


class GlyphLayerPreview(GlyphPreview):

    nsViewClass = GlyphLayerPreviewView

    def setColor(self, color):
        self.getNSView().setColor_(color)
