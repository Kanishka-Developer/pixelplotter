# ----------------------------
#! --- Pixel Plotter  1.0 --- !
#?--- Kanishka Chakraborty ---?

# import dependencies

from PIL import Image  # pip3 install --upgrade pillow
import time, pyautogui # pip3 install --upgrade pyautogui

print("--- INITIATING ---\n") # mark beginning of execution.

#? --- MS Paint Default Palette ---
#?           Black        Grey 50%       Dark Red         Red          Orange          Yellow          Green        Turquoise        Indigo         Purple             White           Grey 25%         Brown            Rose             Gold        Light yellow         Lime       Light turquoise     Blue-grey         Lavender
colors = [[(0, 0, 0), (127, 127, 127), (136, 0, 21), (237, 28, 36), (255, 127, 39), (255, 242, 0), (34, 177, 76), (0, 162, 232), (63, 72, 204), (163, 73, 164)], [(255, 255, 255), (195, 195, 195), (185, 122, 87), (255, 174, 201), (255, 201, 14), (239, 228, 176), (181, 230, 29), (153, 217, 234), (112, 146, 190), (200, 191, 231)]]

color_buckets = [[[], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], []]] # required for buckets renderer

# coordinates valid for 1080p 125%
# assuming the toolbar is fully expanded and that the Paint window starts at (0, 0)
# the easiest way to ensure that is to maximise the Paint window.

#! if the above conditions don't apply to you, change the values below.

palx = 888        # x coordinate of centre of first box in palette
paly = 75         # y coordinate of centre of first box in palette
boff = 27         # shortest distance between centres of two palette boxes
canx = 17         # x coordinate marking beginning of canvas (leave some margin)
cany = 197        # y coordinate marking beginning of canvas (leave some margin)
brush_coords = (388, 86)    # coordinates of centre of BRUSH button
pencil_coords = (283, 86)   # coordinates of centre of PENCIL button
toolsize_coords = (738, 86) # coordinates of centre of SIZE button
size_opt0 = (794, 170)      # coordinates of centre of first SIZE option
size_ooff = 50    # vertical distance between centres of adjacent SIZE options

palette = [] # internal variable for colorspace conversion; do NOT change here

# build palette by unpacking color matrix:
for row in colors: 
	for color in row:
		palette.extend(color)

#? CHANGE THESE VALUES TO CUSTOMIZE OUTPUT:

count = 5            # time in seconds before plotting begins
width = 64	         # width of output image in px
tool = "brush"       # tool to use for plotting;       RECOMMENDED: brush      ALT: pencil
size = 3             # tool size to use for plotting   INTEGER, 1 - 4
poff = 4             # offset in px between successive render pixels
renderer = "buckets" # renderer to use;                RECOMMENDED: buckets    ALT: scanline

# override palette (OPTIONAL; make sure length is multiple of 3):
#palette = [0,0,0,127,127,127,195,195,195,255,255,255]

# ensure palette defines 256 colors:
while len(palette) < 768:
	palette.append(0)

# take reference image from user:
img_path = input("Drag and drop reference image and press ENTER:\n")

# resize and dither reference image:
img = Image.open(img_path)
scale = (width/float(img.size[0]))
height = int((float(img.size[1])*float(scale)))
img = img.resize((width,height), Image.LANCZOS)
p_img = Image.new('P', (16, 16))
p_img.putpalette(palette)
canvas = img.quantize(palette=p_img).convert('RGB')

# friendly reminder:
print("\nSwitch to maximized MS Paint NOW!\n")

# countdown before pixelplotting begins:
for i in range(count, 0, -1):
	print("\rT - ", i, "...", sep='', end='')
	time.sleep(1)

# erase countdown message:
print("\r", end='')

# configure pyautogui:
pyautogui.PAUSE = 0.005   # adjust for what works on your machine (?)
pyautogui.FAILSAFE = True # pls don't set to False

# return closest match in color matrix:
def closest_color(rgb):
	r, g, b = rgb
	color_diffs = []
	for color in colors[0] + colors[1]:
		cr, cg, cb = color
		color_diff = (abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)**0.5
		color_diffs.append((color_diff, color))
	return min(color_diffs)[1]

# return drawing progress given canvas size and number of pixels drawn:
def progress(pcount, csize):
	prg = '%.2f'%(pcount/(csize[0]*csize[1])*100)
	return '0'*(6-len(str(prg))) + str(prg) # formatting :)

# plot image like a CRT TV:
def paint_scanline():
	pcount = 0
	old_target = (0, 0, 0)
	pix = canvas.load()
	for h in range(canvas.size[1]):
		for w in range(canvas.size[0]):
			target = closest_color(pix[w, h])
			yoff = 0 if target in colors[0] else 1
			xoff = colors[yoff].index(target)
			if target != old_target:
				pyautogui.click(palx + xoff*boff, paly + yoff*boff, clicks=2)
				pyautogui.click(palx + xoff*boff, paly + yoff*boff, clicks=2)
				old_target = target
			pcount += 1
			print("\r", progress(pcount, canvas.size), "%", " drawn.", sep='', end='')
			pyautogui.click(canx + w*poff, cany + h*poff, clicks=2)

# plot image one color at a time:
def paint_buckets():
	pcount = 0
	pix = canvas.load()
	for h in range(canvas.size[1]):
		for w in range(canvas.size[0]):
			target = closest_color(pix[w, h])
			yoff = 0 if target in colors[0] else 1
			xoff = colors[yoff].index(target)
			color_buckets[yoff][xoff].append([w, h])
	for row in colors:
		for color in row:
			xoff = row.index(color)
			yoff = colors.index(row)
			bucket = color_buckets[yoff][xoff]
			if len(bucket):
				pyautogui.click(palx + xoff*boff, paly + yoff*boff, clicks=2)
				pyautogui.click(palx + xoff*boff, paly + yoff*boff, clicks=2)
				for pixel in bucket:
					pcount += 1
					print("\r", progress(pcount, canvas.size), "%", " drawn.", sep='', end='')
					pyautogui.click(canx + pixel[0]*poff, cany + pixel[1]*poff, clicks=2)

# select the brush tool in MS Paint
def select_brush():
	pyautogui.click(brush_coords, clicks=2)

# select the pencil tool in MS Paint
def select_pencil():
	pyautogui.click(pencil_coords, clicks=2)

# select the desired tool size:
pyautogui.click(toolsize_coords)
pyautogui.click(size_opt0[0], size_opt0[1]+size_ooff*(size-1))

# initialise progress display:
print("000.00%", " drawn.", sep='', end='')

# get time of start of plotting:
start = time.time()

# select tool as defined in configuration:
if tool == "brush":
	select_brush()
elif tool == "pencil": # "elif" allows skipping tool selection
	select_pencil()
# start selected renderer:
if renderer == "buckets":
	paint_buckets()
else:
	paint_scanline()

# get time of end of plotting:
end = time.time()

# print time taken to plot the image:
print("\n\nDrawing took %.2f seconds."%(end-start))

# reselect the first color in the palette:
pyautogui.click(palx, paly, clicks=2)
pyautogui.click(palx, paly, clicks=2)

print("\n--- TERMINATED ---") # mark end of execution. :)