from inspect import isclass
from fnmatch import filter
try:
    import Image
    import ImageColor
    import ImageFile
    import ImageFilter
    import ImageEnhance
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageColor
        from PIL import ImageFile
        from PIL import ImageFilter
        from PIL import ImageEnhance
    except ImportError:
        raise ImportError("The Python Imaging Library was not found.")

#filters = [] #hack for compatibility
filters_by_identifier = {}

class FilterRegistry(object):
    def __init__(self):
        self.builtin_filters = {}
        self.application_filters = {}
        self.project_filters = {}
        self.db_filters = {}
        self.registry_priority = [self.db_filters, self.project_filters,
                                  self.application_filters, self.builtin_filters]
    
    def _register(self, filter, library):
        library[filter.identifier] = filter
        filters_by_identifier[filter.identifier] = filter #hack for compatibility
        
    def register_builtin_filter(self, filter):
        self._register(filter, self.builtin_filters)
    def register_application_filter(self, filter):
        self._register(filter, self.application_filters)
    def register_project_filter(self, filter):
        self._register(filter, self.project_filters)
    def register_db_filter(self, filter):
        self._register(filter, self.db_filters)
    def register(self, filter):
        self.register_project_filter(filter)
    
    def get(self, identifier):
        for reg in self.registry_priority:
            if reg.has_key(identifier):
                return reg[identifier]
        return None
        
library = FilterRegistry()


class BaseFilter(object):
    identifier = "base_filter"

class ResizeFilter(BaseFilter):
    name = "Resize to specified dimensions"
    identifier = "resize_simple"
    def render(self, im, size_x=48, size_y=48, crop=True, crop_from='top', upscale=True):
        cur_width, cur_height = im.size
        new_width, new_height = (size_x, size_y)
        if crop:
            ratio = max(float(new_width)/cur_width,float(new_height)/cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)
            if crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff+new_width), new_height)
            elif crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff+new_height))
            elif crop_from == 'bottom':
                box = (int(x_diff), int(yd), int(x_diff+new_width), int(y)) # y - yd = new_height
            elif crop_from == 'right':
                box = (int(xd), int(y_diff), int(x), int(y_diff+new_height)) # x - xd = new_width
            else:
                box = (int(x_diff), int(y_diff), int(x_diff+new_width), int(y_diff+new_height))
            im = im.resize((int(x), int(y)), Image.ANTIALIAS).crop(box)
        else:
            if not new_width == 0 and not new_height == 0:
                ratio = min(float(new_width)/cur_width,
                            float(new_height)/cur_height)
            else:
                if new_width == 0:
                    ratio = float(new_height)/cur_height
                else:
                    ratio = float(new_width)/cur_width
            new_dimensions = (int(round(cur_width*ratio)),
                              int(round(cur_height*ratio)))
            print new_dimensions
            if new_dimensions[0] > cur_width or \
               new_dimensions[1] > cur_height:
                if not upscale:
                    return im
            im = im.resize(new_dimensions, Image.ANTIALIAS)
        return im
library.register_builtin_filter(ResizeFilter)

class ReflectionFilter(BaseFilter):
    name = "Sexy Web 2.0 reflection filter"
    identifier = "reflection"
    def render(self, im, bgcolor="#FFFFFF", amount=0.4, opacity=0.6):
        """ Returns the supplied PIL Image (im) with a reflection effect
    
        bgcolor  The background color of the reflection gradient
        amount   The height of the reflection as a percentage of the orignal image
        opacity  The initial opacity of the reflection gradient
    
        Originally written for the Photologue image management system for Django
        and Based on the original concept by Bernd Schlapsi
    
        """
        print "reflection filter"
        # convert bgcolor string to rgb value
        background_color = ImageColor.getrgb(bgcolor)
    
        # copy orignial image and flip the orientation
        reflection = im.copy().transpose(Image.FLIP_TOP_BOTTOM)
    
        # create a new image filled with the bgcolor the same size
        background = Image.new("RGB", im.size, background_color)
    
        # calculate our alpha mask
        start = int(255 - (255 * opacity)) # The start of our gradient
        steps = int(255 * amount) # the number of intermedite values
        increment = (255 - start) / float(steps)
        mask = Image.new('L', (1, 255))
        for y in range(255):
            if y < steps:
                val = int(y * increment + start)
            else:
                val = 255
            mask.putpixel((0, y), val)
        alpha_mask = mask.resize(im.size)
    
        # merge the reflection onto our background color using the alpha mask
        reflection = Image.composite(background, reflection, alpha_mask)
    
        # crop the reflection
        reflection_height = int(im.size[1] * amount)
        reflection = reflection.crop((0, 0, im.size[0], reflection_height))
    
        # create new image sized to hold both the original image and the reflection
        composite = Image.new("RGB", (im.size[0], im.size[1]+reflection_height), background_color)
    
        # paste the orignal image and the reflection into the composite image
        composite.paste(im, (0, 0))
        composite.paste(reflection, (0, im.size[1]))
    
        # return the image complete with reflection effect
        return composite
library.register_builtin_filter(ReflectionFilter)
"""
Create image filter objects for all the built in PIL filters
"""
for n in dir(ImageFilter):
    klass = getattr(ImageFilter, n)
    if isclass(klass) and issubclass(klass, ImageFilter.BuiltinFilter) and \
            hasattr(klass, 'name'):
        class NewSubclass(BaseFilter):
            _pil_filter = klass
            name = klass.name
            identifier = klass.name.replace(' ', '').lower()
            def render(self, im):
                return im.filter(self._pil_filter)
        NewSubclass.__name__ = "%s%s" % (klass.name, "Filter")
        library.register_builtin_filter(NewSubclass)
