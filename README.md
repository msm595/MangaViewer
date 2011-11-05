MangaViewer
===========
*A simple, fast, and standalone Python (v2.7+) manga and image viewer.*

*MangaViewer was designed to be convenient and easy to control. It is entirely possible to select and navigate several manga using only the arrow keys.*

*MangaViewer is currently available in a Window binary (check the downloads) and as python source code.*

## Requirements
If you are using the source code, the following is required:
    
    Python v2.7+
    PIL - The Python Imaging Library

# Controls
## Main Window
The following keys can be used to do the described action. The mousewheel can also be used to scroll. When the viewer reaches the end (or the beginning) of the images, it will display the folder selection dialog.

    <Up>     - Scroll up (if available)
    <Down>   - Scroll down (if available)
    <Left>   - Go to previous image
    <Right>  - Go to next image
    <d>      - Select a new directory
    <f>      - Toggle fullscreen mode
    <Escape> - Closes the viewer

## Folder Dialog
The following keys can be used to do the described actions. The mouse may also be used to make any of the selections: double-clicking will go into the clicked folder, single-clicking will select it, and the buttons do as they are labeled.

    <Left>  - Go up into parent folder
    <Right> - Go into selected folder
    <Enter> - Use selected folder
    <Up>    - Move selection up
    <Down>  - Move selection down

#Settings
The settings file will be created in the same directory as the applicate on the first run as `settings.json`. To modify the settings, simply change the value in quotes to the left of the colons. Make sure the application is not open when you modify the settings file, otherwise your settings will be overwritten.

## Example settings file 
    {
        "rgbResize": "bicubic", 
        "fit": "both", 
        "currentDir": "E:\\Users\\Alex\\Media\\manga\\Mirai Nikki\\Mirai Nikki c59 [Hox][End]", 
        "grayResize": "antialias"
    }

## Settings and Options
**rgbResize** - The method of resizing to be used for color images. While some resize methods may look better that others, the cost will be that it is more processor intensive (and take longer). Possible values in order of quality (best -> worst):

    antialias
    bicubic
    bilinear
    nearest

**grayResize** - The method of resize to be used for grayScale and black-and-white images. This has the same options as rgbResize, but you will find the methods are faster than their color counterparts. Because of this, you may want to select a better quality method here than for rgbResize.

**fit** - The way to scale the images down on the screen (Images are never scaled to larger than they need to be. (Notice that at this time you cannot scroll horizontally, so you may want to make sure that images are never larger width-wise than the screen).

    x - Scale the image so that the width is no larger than the width of the application.
    y - Scale the image so that the height is no larger than the height of the application.
    both - Scale the image in both the x and y direction.
    neither - Don't scale the image.

**currentDir** - This is simply the last directory the MangaViewer was looking at. When manually setting it, change all `\`'s to `\\`, otherwise it won't be parsed correctly. Example: `E:\Users\Alex\Media\manga\Mirai Nikki\Mirai Nikki c59 [Hox][End]` -> `E:\\Users\\Alex\\Media\\manga\\Mirai Nikki\\Mirai Nikki c59 [Hox][End]`