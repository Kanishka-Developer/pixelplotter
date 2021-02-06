# ----------------------------
#! ---  PixelPlotter 2.0  --- !
#?--- Kanishka Chakraborty ---?

#? CHANGE THESE VALUES TO CUSTOMIZE OUTPUT:

count = 3            # time in seconds before plotting begins
timeout = 0          # rendering timeout (0 to disable)
width = 128	     # width of output image in px
tool = "pencil"      # tool to use for plotting;       NOTE: brush is exclusive to MS Paint
size = 1             # tool size to use for plotting   INTEGER, 1 - 4
poff = 4             # offset in px between successive render pixels
renderer = "buckets" # renderer to use;                RECOMMENDED: buckets   ALT: scanline

#? Google Custom Search API config:

cse_enabled = True   # turn Custom Search Engine on or off
api_key = ''
cx = ''
try_count = 3        # number of times to try fetching an image from the API

# below coordinates are valid for 1080p 125%
# assuming that skribbl.io occupies the full screen
# the easiest way to ensure that is to press F11.

#! if the above conditions don't apply to you, change the values below.

palx = 492           # x coordinate of centre of first box in palette
paly = 993           # y coordinate of centre of first box in palette
boff = 30            # shortest distance between centres of two palette boxes
canx = 365 + 20      # x coordinate marking beginning of canvas (leave some margin)
cany = 200 + 20      # y coordinate marking beginning of canvas (leave some margin)
pencil_coords = (845, 1008) # coordinates of centre of PENCIL button
size_opt0 = (1050, 1008)    # coordinates of centre of first SIZE option
size_ooff = 65       # horizontal distance between centres of adjacent SIZE options

# ---------------------------------------------------------------------------------------

# import dependencies

from PIL import Image
from pynput import keyboard
import io, sys, time, requests, urllib.request, pyautogui

print("--- INITIATING ---\n") # mark beginning of execution.

#? --- skribbl.io Palette ---
#?              White          Light Gray        Red          Orange        Yellow         Green       Turquoise       Violet      Dark Purple         Pink            Tan           Black     Dark Gray      Dark Red     More Red        Gold       Dark Green    Dark Blue    Dark Violet    Dark Purple    Darker Pink        Brown
colors = [[(255, 255, 255), (193, 193, 193), (255, 0, 14), (255, 97, 0), (253, 239, 0), (0, 223, 0), (0, 170, 255), (80, 0, 212), (188, 0, 187), (229, 103, 170), (172, 75, 45)], [(0, 0, 0), (76, 76, 76), (128, 0, 8), (212, 12, 1), (241, 165, 0), (0, 93, 14), (6, 73, 158), (36, 0, 101), (100, 0, 105), (182, 66, 116), (107, 44, 13)]]

color_buckets = [[[], [], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], [], []]] # required for buckets renderer

palette = [] # internal variable for colorspace conversion; do NOT change


#! - MS Paint Compatibility -
#! comment out whole section for skribbl.io!
'''
# below coordinates are valid for 1080p 125%
# assuming the toolbar is fully expanded and that the Paint window starts at (0, 0)
# the easiest way to ensure that is to maximise the Paint window.

#! if the above conditions don't apply to you, change the values below.

palx = 888        # x coordinate of centre of first box in palette
paly = 75         # y coordinate of centre of first box in palette
boff = 27         # shortest distance between centres of two palette boxes
canx = 17 + 20    # x coordinate marking beginning of canvas (leave some margin)
cany = 197 + 20   # y coordinate marking beginning of canvas (leave some margin)
brush_coords = (388, 86)    # coordinates of centre of BRUSH button
pencil_coords = (283, 86)   # coordinates of centre of PENCIL button
toolsize_coords = (738, 86) # coordinates of centre of SIZE button
size_opt0 = (794, 170)      # coordinates of centre of first SIZE option
size_ooff = 50    # vertical distance between centres of adjacent SIZE options

#? --- MS Paint Default Palette ---
#?           Black        Grey 50%       Dark Red         Red          Orange          Yellow          Green        Turquoise        Indigo         Purple             White           Grey 25%         Brown            Rose             Gold        Light yellow         Lime       Light turquoise     Blue-grey         Lavender
colors = [[(0, 0, 0), (127, 127, 127), (136, 0, 21), (237, 28, 36), (255, 127, 39), (255, 242, 0), (34, 177, 76), (0, 162, 232), (63, 72, 204), (163, 73, 164)], [(255, 255, 255), (195, 195, 195), (185, 122, 87), (255, 174, 201), (255, 201, 14), (239, 228, 176), (181, 230, 29), (153, 217, 234), (112, 146, 190), (200, 191, 231)]]

color_buckets = [[[], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], []]] # required for buckets renderer

# select the brush tool in MS Paint
def select_brush():
	pyautogui.click(brush_coords, clicks=2)
'''
#! - - - - - - - - - - - - - !

# build palette by unpacking color matrix:
for row in colors: 
	for color in row:
		palette.extend(color)

# ensure palette defines 256 colors:
while len(palette) < 768:
	palette.append(0)

# flag to allow continued plotting:
contd = True

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
	global contd
	pcount = 0
	old_target = (0, 0, 0)
	pix = canvas.load()
	# select tool as defined in configuration:
	if tool == "pencil":
		select_pencil()
	elif tool == 'brush':
		select_brush()
	# select the desired tool size:
	if len(colors[0]) == 11:
		pyautogui.click(size_opt0[0]+size_ooff*(size-1), size_opt0[1])
	else:
		pyautogui.click(toolsize_coords)
		pyautogui.click(size_opt0[0], size_opt0[1]+size_ooff*(size-1))
	for h in range(canvas.size[1]):
		for w in range(canvas.size[0]):
			if contd:
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
	global contd
	pcount = 0
	dom_col = colors[0][0]
	dom_bsize = 0
	dom_xoff = 0
	dom_yoff = 0
	pix = canvas.load()
	# sort buckets:
	for h in range(canvas.size[1]):
		for w in range(canvas.size[0]):
			target = closest_color(pix[w, h])
			yoff = 0 if target in colors[0] else 1
			xoff = colors[yoff].index(target)
			color_buckets[yoff][xoff].append([w, h])
	# find dominant color:
	for row in colors:
		for color in row:
			xoff = row.index(color)
			yoff = colors.index(row)
			bucket = color_buckets[yoff][xoff]
			if len(bucket) > dom_bsize:
				dom_col = colors[yoff][xoff]
				dom_xoff = xoff
				dom_yoff = yoff
				dom_bsize = len(bucket)
	# fill canvas with dominant color:
	bucket = color_buckets[dom_yoff][dom_xoff]
	pyautogui.click(palx + dom_xoff*boff, paly + dom_yoff*boff, clicks=2)
	pyautogui.click(palx + dom_xoff*boff, paly + dom_yoff*boff, clicks=2)
	pyautogui.click(pencil_coords[0]+ ((2 * size_ooff) if len(colors[0]) == 11 else boff), pencil_coords[1], clicks=2)
	pyautogui.click(canx-20, cany-20)
	time.sleep(0.25)
	pcount += len(bucket)
	print("\r", progress(pcount, canvas.size), "%", " drawn.", sep='', end='')
	# select tool as defined in configuration:
	if tool == "pencil":
		select_pencil()
	elif tool == 'brush':
		select_brush()
	# select the desired tool size:
	if len(colors[0]) == 11:
		pyautogui.click(size_opt0[0]+size_ooff*(size-1), size_opt0[1])
	else:
		pyautogui.click(toolsize_coords)
		pyautogui.click(size_opt0[0], size_opt0[1]+size_ooff*(size-1))
	# iterate over individual colors:
	for row in colors:
		for color in row:
			xoff = row.index(color)
			yoff = colors.index(row)
			bucket = color_buckets[yoff][xoff]
			if color == dom_col: # set as canvas color; no need to plot
				continue
			if len(bucket):
				pyautogui.click(palx + xoff*boff, paly + yoff*boff, clicks=2)
				pyautogui.click(palx + xoff*boff, paly + yoff*boff, clicks=2)
				for pixel in bucket:
					if contd: # skip plotting if 'esc' was pressed
						if time.time() - start > timeout and timeout: # break out if time is up
							break                                     # and timeout is enabled
						pcount += 1
						print("\r", progress(pcount, canvas.size), "%", " drawn.", sep='', end='')
						pyautogui.click(canx + pixel[0]*poff, cany + pixel[1]*poff, clicks=2)

# select the pencil tool
def select_pencil():
	pyautogui.click(pencil_coords, clicks=2)

# configure pyautogui:
pyautogui.PAUSE = 0.005   # adjust for what works on your machine (?)
pyautogui.FAILSAFE = True # pls don't set to False

# handle 'esc' to prematurely terminate plotting:
def on_release(key):
	global contd
	if key == keyboard.Key.esc:
		contd = False

# keyboard listener to enable 'esc' handler:
listener = keyboard.Listener(
    on_release=on_release)
listener.start()

# keep accepting new references till user presses 'Cancel'
# or sends a KeyboardInterrupt:
while True:
	start_n = 1
	if cse_enabled:
		# pop-up input window for reference phrase and save query:
		query = pyautogui.prompt(text='--- Enter cue phrase ---', title='PixelPlotter 2.0')
		# handle 'Cancel':
		if query == None:
			break
		# log provided query:
		print("Reference: ", query)
		while True:
			try:
				# API call to Google Custom Image Search:
				# https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list#request
				response = requests.get(
											'https://www.googleapis.com/customsearch/v1?key=' + api_key + 
											'&cx=' + cx + 
											'&searchType=image' +
											'&num=1' +
											'&start=' + str(start_n) +
											'&safe=active' +
											#'&imgSize=medium' +
											'&fileType=jpeg' +
											'&imgColorType=color' +
											#'&imgType=clipart' +
											'&q=' + query.replace(" ", "+")
										)
				# extract json response:
				js0n = response.json()
				# extract image link from json:
				img_link = js0n['items'][0]['link']
				# log extracted link:
				print("Fetched image:", img_link)
				# save URL data:
				dat = urllib.request.urlopen(img_link)
				# read data bytes into image file:
				img_file = io.BytesIO(dat.read())
				img = Image.open(img_file)
				scale = (width/float(img.size[0]))
				height = int((float(img.size[1])*float(scale)))
				img = img.resize((width,height), Image.LANCZOS)
				p_img = Image.new('P', (16, 16))
				p_img.putpalette(palette)
				canvas = img.quantize(palette=p_img).convert('RGB')
				break
			except:
				print("Something went wrong. Retrying... ", start_n, " of ", try_count, ".", sep='')
				start_n += 1
				if start_n >= (try_count + 1):
					pyautogui.alert(text='Fetching image from CSE API failed. Falling back to manual input.', title='PixelPlotter 2.0')
					print("Fetching image from CSE API failed. Falling back to manual input.")
					break
	else:
		start_n = try_count + 1    # trigger drag and drop
	while True:
		if start_n >= (try_count + 1): # fetching from API failed
			try:
				# take reference image from user:
				img_file = input("Drag and drop reference image and press ENTER:\n")
				# resize and dither reference image:
				#img = Image.open(img_file)
				img = Image.open(img_file)
				scale = (width/float(img.size[0]))
				height = int((float(img.size[1])*float(scale)))
				img = img.resize((width,height), Image.LANCZOS)
				p_img = Image.new('P', (16, 16))
				p_img.putpalette(palette)
				canvas = img.quantize(palette=p_img).convert('RGB')
				break
			except KeyboardInterrupt:
				print("\n--- TERMINATED ---")
				sys.exit()
			except:
				print("\nThat didn't work. Please provide a different image.")
		else:
			break

	# friendly reminder:
	print("\nSwitch to fullscreen target window NOW!\n")

	# countdown before pixelplotting begins:
	for i in range(count, 0, -1):
		print("\rT - ", i, "...", sep='', end='')
		time.sleep(1)

	# erase countdown message:
	print("\r", end='')

	# initialise progress display:
	print("000.00%", " drawn.", sep='', end='')

	# get time of start of plotting:
	start = time.time()

	# start selected renderer:
	if renderer == "buckets":
		paint_buckets()
	else:
		paint_scanline()

	# get time of end of plotting:
	end = time.time()

	# print time taken to plot the image:
	print("\n\nDrawing took %.2f seconds."%(end-start))

	# reselect black in the palette:
	if len(colors[0]) == 11:
		pyautogui.click(palx, paly+boff, clicks=2)
		pyautogui.click(palx, paly+boff, clicks=2)
	else:
		pyautogui.click(palx, paly, clicks=2)
		pyautogui.click(palx, paly, clicks=2)

	# rinse, repeat for next reference.
	del query, response, js0n, img_link, dat, img_file, img, canvas
	color_buckets = [[[], [], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], [], []]]

print("\n--- TERMINATED ---") # mark end of execution. :)
