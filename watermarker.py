import cv2
import numpy as np
import argparse
import os

# add an alpha channel
def bgr2bgra(I):
	b, g, r = cv2.split(I)
	a = np.ones(b.shape, dtype=b.dtype) * 255
	return cv2.merge((b, g, r, a))

# place the watermark in a black RGBA image for later weighting with main image
def construct_watermark_overlay(L, full_shape):
	border = 20
	# bottom right
	pos = (full_shape[0] - L.shape[0] - border, full_shape[1] - L.shape[1] - border)
	full = np.zeros((full_shape[0], full_shape[1], 4), dtype=np.uint8)
	full[pos[0]:pos[0] + L.shape[0],pos[0]:pos[1] + L.shape[1],:] = L
	return full

# add the positioned watermark to the main image, with a transparency of 1-alpha
def add_watermark(I, full, alpha = .25):
	I = bgr2bgra(I)
	marked = cv2.addWeighted(full, alpha, I, 1.0, 0)
	return marked

# apply watermark to all images in input_dir, writing to output_dir.  For now, require png inputs.
def add_watermark_dir(input_dir, output_dir, logo):
	L = cv2.imread(args["logo"])
	L = bgr2bgra(L)
	img_names = [f for f in os.listdir(input_dir) if os.path.splitext(os.path.join(input_dir,f))[1] == ".png"]
	overlay = []
	c = 1
	for img_name in img_names:
		print "Watermarking image %d/%d:" % (c, len(img_names)), img_name
		I = cv2.imread(os.path.join(input_dir, img_name))
		if not(len(overlay)) or not(I.shape == overlay.shape):
			overlay = construct_watermark_overlay(L, I.shape)
		marked = add_watermark(I, overlay, alpha = .25)
		basename, ext = os.path.splitext(img_name)
		cv2.imwrite(os.path.join(args["output"], basename + "_marked" + ext), marked)
		c += 1
	print "Complete.  See \"%s\" for watermarked images." % args["output"]

# example usage: python watermarker.py -l "logo.png" -i "imgs" -o "marked"
if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("-l", "--logo", required=True,
		help="path to logo image (RGB color with black for transparent part)")
	ap.add_argument("-i", "--input", required=True,
		help="path to the input directory of images (all RGB PNG)")
	ap.add_argument("-o", "--output", required=True,
		help="path to the output directory of watermarked (RGBA images) titled <image name>_marked.<image extension>")
	args = vars(ap.parse_args())

	add_watermark_dir(args["input"], args["logo"], args["output"])
