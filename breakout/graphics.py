# graphics.py
# Walker M. White (wmw2)
# November 8, 2012
"""Generic graphics classes for Breakout.

Use these graphics classes as the building blocks for your game.  DO NOT
MODIFY THE CODE IN THIS FILE.  Instead, you should just instantiate these
classes (or subclass them) to make your game.  See the online documentation
for more guidance; it includes information not displayed in this module."""
from kivy.properties import ListProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock

# Non-Kivy Imports
import pygame.mixer
import colormodel
import os.path

# Import Kivy language file with visual interface information
from kivy.lang import Builder 
Builder.load_file(str(os.path.join(os.path.dirname(__file__), 'graphics.kv')))

# User-defined resources
FONT_PATH  = str(os.path.join(os.path.dirname(__file__), 'Fonts'))
SOUND_PATH = str(os.path.join(os.path.dirname(__file__), 'Sounds'))
IMAGE_PATH = str(os.path.join(os.path.dirname(__file__), 'Images'))

import kivy.resources
kivy.resources.resource_add_path(FONT_PATH)
kivy.resources.resource_add_path(SOUND_PATH)
kivy.resources.resource_add_path(IMAGE_PATH)

# Initialize the sound engine.
FREQUENCY=44100
BITSIZE=-16
CHANNELS=2
BUFFER=1024
pygame.mixer.init(FREQUENCY,BITSIZE,CHANNELS,BUFFER)

def Sound(filename):
    """Creates a new Sound object for the given file.
    
    This function is a proxy for the pygame.mixer.Sound class.  That class requires
    some finicky initialization in order to work properly.  In order to hide that from
    you, we have given you this function to use instead.  Treat this function just
    like a constructor (except that the object type is pygame.mixer.Sound, not Sound).
    
        :param filename: string providing the name of a sound file
    
    See the online documentation for more information."""
    absname = filename if os.path.isabs(filename) else str(os.path.join(SOUND_PATH, filename))
    return pygame.mixer.Sound(absname)


class GObject(Widget):
    """Base graphics object for a `GameView` class.
    
    You should never make a GObject directly.  Instead, you should use one of the
    subclasses: GRectangle, GEllipse, GLine, GImage, and GLabel."""
    # Fields.  See the associated property.
    _fillcolor = colormodel.RGB(0,0,0,1)  # fill color field
    _linecolor = colormodel.RGB(0,0,0,1)  # line color field

    # Kivy properties.  For integration with graphics.kv
    _kivy_fill_color = ListProperty([0,0,0,1]) # Kivy representation of fill color
    _kivy_line_color = ListProperty([0,0,0,1]) # Kivy representation of line color
    
    @property
    def fillcolor(self):
        """The object fill color.
        
        Used to color the backgrounds or, in the case of solid shapes, the shape
        interior.
        
        **Invariant**: Must be an RGB or HSV object from module `colormodel`."""
        return self._fillcolor
    
    @fillcolor.setter
    def fillcolor(self,value):
        assert type(value) in (colormodel.RGB, colormodel.HSV), `value`+' is not a valid color'
        self._fillcolor = value
        self._kivy_fill_color = value.glColor()
        
    @property
    def linecolor(self):
        """The object line color.
        
        Used to color the foreground, text, or, in the case of solid shapes, the
        shape border.
        
        **Invariant**: Must be an RGB or HSV object from module `colormodel`."""
        return self._linecolor
    
    @linecolor.setter
    def linecolor(self,value):
        assert type(value) in (colormodel.RGB, colormodel.HSV), `value`+' is not a valid color'
        self._linecolor = value
        self._kivy_line_color = value.glColor()

    def __init__(self,**keywords):
        """**Constructor**: creates a new graphics object.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes.  For example, to initialize the x position and
        the fill color, use the constructor call
        
            GObject(x=2,fillcolor=colormodel.RED)
        
        You do not need to provide the keywords as a dictionary.
        The ** in the parameter `keywords` does that automatically.
        
        Any attribute of this class may be used as a keyword.  The
        argument must satisfy the invariants of that attribute.  See
        the list of attributes of this class for more information."""
        super(GObject,self).__init__(**keywords)
        if 'fillcolor' in keywords:
            self.fillcolor = keywords['fillcolor']
        if 'linecolor' in keywords:
            self.linecolor = keywords['linecolor']
        self.size_hint = (None,None)
    

    def collide_widget(w):
        # Prevent students from using this built-in method
        pass


class GLine(GObject):
    """Instance represents a sequence of line segments in the `GameView`
    
    The line is defined by the `points` attribute which is an (even) sequence
    of alternating x and y values. When added to the graphics view, the view
    draws a sequence of line segments, starting from one x-y pair in `points`
    and going to the next x-y pair.  If `points` has length 2n, then the result
    is n-1 line segments.
    
    The object uses the attribute `linecolor` to determine the color of the
    line.  The attribute `fillcolor` is unused (even though it is inherited
    from `GObject`)."""
    # Kivy property.  Requires manual documentation due to no docstring
    # List of floats of length 2n representing a sequence of x-y pairs.
    points = ListProperty([])
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new sequence of line segments.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create a line from (0,0) to
        (2,3), use the constructor call
        
            GLine(points=[0,0,2,3])
        
        This class supports the same keywords as `GObject`.  In
        addition, it supports the keyword `points` for the attribute
        of the same name.
        
        The attributes size and pos are redundant in objects for
        this class.  They are computed automatically from `points`."""
        super(GLine,self).__init__(**keywords)
        if 'points' in keywords:
            self.points = keywords['points']
        else:
            self.points = []
        self.bind(points=self._resize)
        self._resize()
        
    # Compute the size and pos from the list of points
    # Also does invariant checking on the point list.
    def _resize(self,instance=None,value=None):
        mxx = None
        mxy = None
        mnx = None
        mny = None
        
        xpos = True
        assert len(self.points) % 2 == 0, `p`+' does not have even length'
        for p in self.points:
            assert type(p) in (int,float), `p`+' is not a number'
            if xpos:
                if mxx is None or mxx < p:
                    mxx = p
                if mnx is None or mnx > p:
                    mnx = p
            else:
                if mxy is None or mxy < p:
                    mxy = p
                if mny is None or mny > p:
                    mny = p
            xpos = not xpos
        
        self.size = (mxx-mnx,mxy-mny)
        self.pos = (mnx,mny)


class GTriangle(GObject):
    """Instance represents a triangle in the `GameView`
    
    The triangle is defined by the attribute `points` which is a list of 6 floats.
    It stores the three x-y pairs that define the triangle.  The object
    uses `fillcolor` for the interior of the triangle and `linecolor` for
    its border."""
    # Kivy property.  Requires manual documentation due to no docstring
    # List of floats of length 6 representing a sequence of x-y pairs.
    points = ListProperty([0]*6)
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new triangle.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create a triangle with the
        points (0,0), (0,2), and (1,1), use the constructor call
        
            GTriangle(points=[0,0,0,2,1,1])
        
        This class supports the same keywords as `GObject`.  In
        addition, it supports the keyword `points` for the attribute
        of the same name.
        
        The attributes size and pos are redundant in objects for
        this class.  They are computed automatically from `points`."""
        # Now ready to initialize
        super(GTriangle,self).__init__(**keywords)
        if 'points' in keywords:
            self.points = keywords['points']
        else:
            self.points = []
        self.bind(points=self._resize)
        self._resize()
    
    # Compute the size and pos from the list of points
    # Also does invariant checking on the point list.
    def _resize(self,instance=None,value=None):
        mxx = None
        mxy = None
        mnx = None
        mny = None
        
        xpos = True
        assert len(self.points) == 6, `p`+' does not exactly 3 coordinates'
        for p in self.points:
            assert type(p) in (int,float), `p`+' is not a number'
            if xpos:
                if mxx is None or mxx < p:
                    mxx = p
                if mnx is None or mnx > p:
                    mnx = p
            else:
                if mxy is None or mxy < p:
                    mxy = p
                if mny is None or mny > p:
                    mny = p
            xpos = not xpos
        
        self.size = (mxx-mnx,mxy-mny)
        self.pos = (mnx,mny)


class GImage(GObject):
    """Instance represents a rectangular image in the `GameView`
    
    The image is given by a JPEG, PNG, or GIF file whose name is stored
    in the attribute `source`.  Image files should be stored in the
    **Images** directory so that Kivy can find them without the complete
    path name.
    
    In this graphics object, the `linecolor` and `fillcolor` attributes
    are ignored.  The image is displayed as a rectangle whose bottom
    left corner is defined by attribute `pos` and whose width and height
    are defined by the attribute `size`.  If the `size` attribute does
    not agree with the actual size of the image, the image is scaled
    to fit."""
    source = StringProperty('')
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new image.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create an image from the file
        "gollum.png", use the constructor call
        
            GImage(source='gollum.png')
        
        This class supports the same keywords as `GObject`.  In
        addition, it supports the keyword `source` for the attribute
        of the same name."""
        super(GImage,self).__init__(**keywords)
        if 'source' in keywords:
            self.source = keywords['source']


class GLabel(GObject):
    """Instance represents an (uneditable) text label in `GameView`
    
    The attribute `text` defines the content of this image.  Uses of
    the escape character '\\n' will result in a label that spans multiple
    lines.  The label includes both the text, and a rectangular backdrop
    with bottom left corner at `pos` and width and height `size`.  The
    background color of this rectangle is `fillcolor`, while `linecolor`
    is the color of the text.
    
    The text itself is aligned within this rectangle according to the
    attributes `halign` and `valign`.  See the documentation of these
    attributes for how alignment works.  There are also attributes
    to change the point size, font style, and font name of the text.
    The `size` attribute of this label will grow to ensure that the
    text will fit in the rectangle, no matter the font or point size.
    
    To change the font, you need a .ttf (TrueType Font) file in the
    Fonts folder; refer to the font by filename, including the .ttf.
    If you give no name, it will use the default Kivy font.  The
    `bold` attribute only works for the default Kivy font; for other
    fonts you will need the .ttf file for the bold version of that
    font.  See `ComicSans.ttf` and `ComicSansBold.ttf` for an example."""
    # Fields.  See the associated property.
    _valign = 'bottom'
    _halign = 'left'
    
    # Override the fill color
    _fillcolor = colormodel.RGB(0,0,0,0)  # fill color field
    _kivy_fill_color = ListProperty([0,0,0,0]) # Kivy representation of fill color

    # Interior Kivy label.  Hidden field with no property.
    _label = None

    @property
    def font_size(self):
        """Size of the text font in points.
        
        **Invariant**: A positive number (int or float)"""
        return self._label.font_size

    @font_size.setter
    def font_size(self,value):
        assert type(value) in (int,float), `value`+' is not a number'
        self._label.font_size = value
        self._label.texture_update()

    @property
    def font_name(self):
        """File name for the .ttf file to use as a font
        
        **Invariant**: string referring to a .ttf file in folder Fonts"""
        return self._label.font_name

    @font_name.setter
    def font_name(self,value):
        assert type(value) == str, `value`+' is not a string'
        self._label.font_name = value
        self._label.texture_update()

    @property
    def bold(self):
        """Boolean indicating whether or not the text should be bold.
        
        Only works on the default Kivy font.  Does not work on custom
        .ttf files.  In that case, you need the bold version of the
        .ttf file.  See `ComicSans.ttf` and `ComicSansBold.ttf` for
        an example.
        
        **Invariant**: boolean"""
        return self._label.bold

    @bold.setter
    def bold(self,value):
        assert type(value) == bool, `value`+' is not a bool'
        self._label.bold = value
        self._label.texture_update()

    @property
    def text(self):
        """Text for this label.
        
        The text in the label is displayed as a single line, or broken
        up into multiple lines in the presence of the escape character
        '\\n'. The `size` attribute of this label grows to make sure
        that the entire text fits inside of the rectangle.
        
        **Invariant**: string"""
        return self._label.text
    
    @text.setter
    def text(self,value):
        assert type(value) == str, `value`+' is not a string'
        self._label.text = value
        self._label.texture_update()

    @property
    def halign(self):
        """Horizontal alignment for this label.
        
        The text is anchored inside of the label rectangle on either the
        left, the right or the center.  This means that as the size of
        the label increases, the text will still stay rooted at that
        anchor.
        
        **Invariant**: one of 'left', 'right', or 'center'"""
        return self._halign
    
    @halign.setter
    def halign(self,value):
        assert value in ('left','right','center'), `value`+' is not a valid horizontal alignment'
        self._halign = value
        if not self._label is None:
            self._label.halign = value

    @property
    def valign(self):
        """Vertical alignment for this label.
        
        The text is anchored inside of the label rectangle at either the
        top, the bottom or the middle.  This means that as the size of
        the label increases, the text will still stay rooted at that
        anchor.
        
        **Invariant**: one of 'top', 'bottom', or 'middle'"""
        return self._valign
    
    @valign.setter
    def valign(self,value):
        assert value in ('top','middle','bottom'), `value`+' is not a valid vertical alignment'
        self._valign = value
        if not self._label is None:
            self._label.valign = value

    @property
    def linecolor(self):
        """The text color for this label.
        
        Overrides `linecolor` property in `GObject`
            
        **Invariant**: Must be a RGB or HSV object from module `colormodel`."""
        return self._linecolor
    
    @linecolor.setter
    def linecolor(self,value):
        assert type(value) in (colormodel.RGB, colormodel.HSV), `value`+' is not a valid color'
        self._linecolor = value
        if not self._label is None:
            self._label.color = value.glColor()
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new text label.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create a label containing the
        word 'Hello', use the constructor call
        
            GLabel(text='Hello')
        
        This class supports the same keywords as `GObject`, as well
        as additional attributes for the text properties (e.g. font
        size and name)."""
        self._label = Label(**keywords)
        self._label.size_hint = (None,None)
        super(GLabel,self).__init__(**keywords)
        self.add_widget(self._label)
        self.size = self._label.size

        if 'halign' in keywords:
            self.halign = keywords['halign']

        if 'valign' in keywords:
            self.valign = keywords['valign']

        if not 'linecolor' in keywords:
            self.linecolor = colormodel.BLACK
            
        self._label.bind(texture_size=self._resize)
        self.bind(pos=self._resize)
        self._resize()
    
    # Compute the size and pos from the text texture.
    # Also align the internal label in the rectangle.
    def _resize(self,instance=None,value=None):
        self._label.size = self._label.texture_size
        
        # Resize the outside if necessary
        width = max(self.width,self._label.width)
        height = max(self.height,self._label.height)
        
        # Reset to horizontal anchor position.
        if self._halign == 'left':
            self.width = width
        elif self._halign == 'center':
            cx = self.center_x
            self.width = width
            self.center_x = cx
        else:
            right = self.right
            self.width = width
            self.right = right            

        # Reset to vertical anchor position.
        if self._valign == 'top':
            top = self.top
            self.height = height
            self.top = top
        elif self._valign == 'middle':
            cy = self.center_y
            self.height = height
            self.center_y = cy
        else:
            self.height = height
        
        # Internal Horizontal placement
        if self._halign == 'left':
            self._label.x = self.x
        elif self._halign == 'center':
            self._label.center_x = self.center_x
        else: # 'ightr'
            self._label.right = self.right
        
        # Internal Vertical placement
        if self._valign == 'top':
            self._label.top = self.top
        elif self._valign == 'middle':
            self._label.center_y = self.center_y
        else: # 'bottom'
            self._label.y = self.y


class GRectangle(GObject):
    """Instance represents a solid rectangle in `GameView`
    
    The bottom left corner of the rectangle is given by `pos` and
    the width and height are given by `size`.  The interior (fill)
    color of this rectangle is `fillcolor`, while `linecolor`
    is the color of the border.
    
    For more fine-grained rectangle placement, you should make
    use of the attributes `center`, `center_x`, `center_y`, `right`,
    and `top`, all inherited from `GObject`.  See that class
    for more."""
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new rectangle.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create a rectangle with corners
        points (0,0), (0,2), (1,2), and (1,0), use the constructor call
        
            GRectangle(pos=(0,0),size=(1,2))
        
        This class supports the same keywords as `GObject`."""
        super(GRectangle,self).__init__(**keywords)
        
        
class GEllipse(GObject):
    """Instance represents a solid ellipse in `GameView`
    
    The ellipse is the largest one that can be drawn inside of a
    rectangle whose bottom left corner is given by `pos` and
    whose width and height are given by `size`.  The interior (fill)
    color of this rectangle is `fillcolor`, while `linecolor`
    is the color of the border.
    
    For more fine-grained rectangle placement, you should make
    use of the attributes `center`, `center_x`, `center_y`, `right`,
    and `top`, all inherited from `GObject`.  See that class
    for more."""

    def __init__(self,**keywords):
        """**Constructor**: creates a new ellipse.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create an circle centered at
        (0,0) with radius 10, use the constructor call
        
            GEllipse(center=(0,0),size=(20,20))
        
        Note that we specify ellipse size by diameter, not radius
        This class supports the same keywords as `GObject`."""
        super(GEllipse,self).__init__(**keywords)
        

class _ClockEvent(object):
    """Instances represent delayed graphics events.
    
    Internal class to make animation and pauses simpler."""
    # Hidden Fields
    _parent = None    # The view to update when the event occurs
    _widget = None    # The widget to remove when the event occurs
    _callback = None  # The function to call when the event occurs.
    
    def __init__(self,parent=None,widget=None,callback=None):
        """**Constructor**: Creates a new clock delay event.
        
            :param parent: The parent object
            **Precondition**: A `GameView` or `GameController`
            
            :param widget: The widget to remove when the even occurs
            **Precondition**: A `GObject` or None if parent is a `GameController`

            :param callback: The function to call when the event occurs.
            **Precondition**: A function with no (additional) arguments
        
        The delay interval is set by the parent object."""
        self._parent = parent
        self._widget = widget
        self._callback = callback
    
    def awaken(self,dt):
        """Respond to the delayed event.
        
        Delete the widget if it is there. Call the callback if it exists."""
        if not self._parent is None:
            if not self._widget is None:
                self._parent.remove(self._widget)
            self._parent._events.remove(self)
            
        if not self._callback is None:
            if self._widget is None:
                self._callback()
            else:
                self._callback(self._widget)


class GameView(FloatLayout):
    """The view class for a `GameController` application.
    
    You may need to access an instance of this class to add and/or remove
    `GObject` instances.  However, you will never need to construct one.
    You should only use the one provided in the `view` attribute of
    `GameController`.  See `GameController` for more information."""
    # Hidden Field.  Necessary to maintain strong references to delayed events.    
    _events = []
    
    def add(self,widget,timeout=0,callback=None):
        """Add a new `GObject` to this view.
        
            :param widget: widget to add
            **Precondition**: an *instance of* `GObject`

            :param timeout: time to remove widget in seconds; never if 0
            **Precondition**: a non-negative number (int or float)
            
            :param callback: function called after delay; ignored if `timeout` is 0.
            **Precondition**: a function reference; must be a function that takes the widget as an argument
        
        Objects are drawn 'bottom-up', with later objects drawn on top of
        objects added earlier.  If you wish for an object to be in the
        background, it must be added first.
        
        The `timeout` attribute is a simple way to provide a widget that quickly
        flashes up on screen, though the `delay` method in `GameController` has 
        the same effect."""
        assert isinstance(widget,GObject)
        self.add_widget(widget)
        if timeout > 0:
            timer = _ClockEvent(self,widget,callback)
            self._events.append(timer)
            Clock.schedule_once(timer.awaken, timeout)
    
    def remove(self,widget):
        """Removes the widget from this view.
            
            :param widget: widget to remove
            **Precondition**: a `GObject` stored in this view
        
        Manually removes a `GObject` widget from this view. You
        should call this method if the graphics object was added
        with timeout 0; otherwise the application will automatically
        remove the widget for you.
        
        This method does nothing if widget is not in this view."""
        self.remove_widget(widget)


class GameController(object):
    """Primary controller class for a simple game application.
    
    To create a game application, subclass this class. Make sure
    to add a call to super to your constructor (should you choose
    to override the constructor at all). To provide game functionality
    you only need to override the following five methods:
    
        `initialize`: Called at the start of the game to initialize your
        program.  It is preferable to put start-up code here rather than
        in your constructor.
        
        `update`: Called every animation frame (60x a second). This is
        where you add any game animation code.
        
        `on_touch_down`: Called whenever the user presses the mouse or
        a finger (for a touch screen device).  

        `on_touch_up`: Called whenever the user releases the mouse or
        a finger (for a touch screen device).  Every touch_down event
        has a corresponding touch_up event.
        
        `on_touch_move`: Called whenever the user moves the mouse or
        a finger while it is still help down.  touch_move events are
        optional for each press, while touch_down and touch_up are not.
    
    These are the only methods that you *must* implement.  In addition,
    you should add whatever fields and/or helper methods are necessary
    for your game.
    
    Except in very few instances you should never need to add properties
    to a `GameController`.  As the controller, it manages all of the
    objects in the game, and none of the other objects need to access
    its fields."""
    # Field for the view.  See associated property
    _view = None
    # Hidden Field.  Necessary to maintain strong references to delayed events.    
    _events = []
    
    @property
    def view(self):
        """The Game view.
        
        This attribute is *immutable* in that you cannot delete it or
        replace it by another view.  However, the view itself is not
        immutable.  You are free to use the `add` and `remove` methods
        in this attribute to add and remove graphics objects."""
        return self._view
    
    # VISIBLE METHODS
    
    def __init__(self):
        """**Constructor**: Creates a game with this controller"""
        self._view = GameView()
        self._view.bind(on_touch_down=self.on_touch_down)
        self._view.bind(on_touch_move=self.on_touch_move)
        self._view.bind(on_touch_up=self.on_touch_up)
        Clock.schedule_once(self._start_up,-1)

    def delay(self,callback,time):
        """Delay the execution of callback for time seconds.
        
            :param callback: function called after delay
            **Precondition**: a function reference; must be a function with no additional arguments

            :param time: time to wait in seconds before calling the function.
            **Precondition**: a positive number (int or float)
        
        You may have multiple callbacks delayed at any given time.  However,
        you be careful about called `delay` inside of callback functions already
        delayed.  The result is similar to recursion in that it can run out
        of memory if you do it too much."""
        timer = _ClockEvent(self,None,callback)
        self._events.append(timer)
        Clock.schedule_once(timer.awaken,time)

    def initialize(self):
        """Called to initialize the game features.
        
        This method is the preferred way to initialize the elements in your
        game, rather than overriding your constructor.  Because of the way
        graphical applications work, you cannot guarantee that the view window
        is sized properly when you are still inside of the constructor.  This
        method is called later, when we can guarantee that the window and
        other graphics elements have the right size.
        
        *Override this method to provide code specific to your game.*"""
        pass

    def update(self,dt):
        """Called every animation frame.
        
            :param dt: time in seconds since last update
            **Precondition**: a number (int or float)
        
        This method is called 60x a second to provide on-screen animation.
        Think of it as the body of the loop.  It is best to have fields
        that represent the current animation state so that you know where
        you are in the animation.
        
        *Override this method to provide code specific to your game.*"""        
        pass
    
    def on_touch_down(self,view,touch):
        """Called when the user presses the mouse or a finger (on touch screens)
        
            :param view: view receiving touch event
            **Precondition**: the `GameView` of this `GameController`
            
            :param touch: touch event information
            **Precondition**: a Kivy `MotionEvent`_ object
            
        This method responds to a touch_down event.  If you want the user to
        'click to continue', or if you want to control a paddle on screen,
        this is the primary method for responding to those controls.  Every
        touch_down event is followed by a touch_up event.

        *Override this method to provide code specific to your game.*"""        
        pass
    
    def on_touch_move(self,view,touch):
        """Called when the user moves the mouse or a finger (on touch screens)
        
            :param view: view receiving touch event
            **Precondition**: the `GameView` of this `GameController`
            
            :param touch: touch event information
            **Precondition**: a Kivy `MotionEvent`_ object

        This method responds to a touch_move event. Touch moves are optional
        events and do not always need to be processed.  However, they are important
        if you want the touch to move a graphics object on screen, such as a paddle.

        *Override this method to provide code specific to your game.*"""        
        pass

    def on_touch_up(self,view,touch):
        """Called when the user releases the mouse or a finger (on touch screens)
        
            :param view: view receiving touch event
            **Precondition**: the `GameView` of this `GameController`
            
            :param touch: touch event information
            **Precondition**: a Kivy `MotionEvent`_ object
        
        This method responds to a touch_up event. As every touch_down event has
        a corresponding touch_up event, this lets you know when the mouse or finger
        has been released. At this point you should reset whatever state fields
        you had following the touch, as appropriate.

        *Override this method to provide code specific to your game.*"""        
        pass


    # Hidden helper methods
    def _start_up(self,dt):
        """Initialize the game and start up the animation frame.
        
        Calls `initiatlize` as a helper, which does all the work.
        Necessary as much of the size and position information in
        the application is not available until the constructor is
        finished."""
        Clock.schedule_interval(self.update,1.0/60.0)
        self.initialize()    
