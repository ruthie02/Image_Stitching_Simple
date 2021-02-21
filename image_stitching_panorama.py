#how to use
# change the directory to where the source code and images are saved
# then type this in your command prompt 
# python image_stitching_panorama.py --input_images image_directory --output_image output_filename.png


# import all the packages needed to create a panorama

from imutils import paths
import numpy as np
import argparse
import imutils
import cv2

# now we need to construct the argument parser and parse the arguments
arguparsers = argparse.ArgumentParser()
arguparsers.add_argument("-i", "--input_images", type = str, required = True,
    help = "path to where the input images are saved to stitch")
arguparsers.add_argument("-o", "--output_image", type = str, required = True,
    help = "path to the output image after stitching")
arguparsers.add_argument("-c", "--crop_stitch", type = int, default = 0,
    help="option to crop out the largest rectangular region")
args = vars(arguparsers.parse_args())

# get the input images path and initialize the image list

print("[INFO] loading images....")
imagePaths = sorted(list(paths.list_images(args["input_images"])))
input_images = []

#iterate over the image paths, load all those, 
# and add them to the list of images to stitch
for imagePath in imagePaths:
    image = cv2.imread(imagePath)
    input_images.append(image)


# now we initialize the OpenCV's image stitcher object and perform stitching
stitcher = cv2.Stitcher_create() 
(status, stitched) = stitcher.stitch(input_images)

# if status == 0, then that means OpenCV successfully stitched the image

if status == 0:
    # check to see if we are supposed to crop out the largest rectangular
    #region from the stitched image to have a better looking panoramic image
    if args["crop_stitch"] > 0:
        # create a 10 pixel border surrounding the stitched image
        print("[INFO] cropping stitched image....")
        stitched = cv2.copyMakeBorder(stitched, 10, 10, 10, 10, 10,
            cv2.BORDER_CONSTANT, (0,0,0))

        #convert the stitched image to greyscale and create a threshold such that 
        # all pixels > 0 are set to 255 -- foreground, while 
        # others remain 0 --background

        grey = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

        #find all the external contours in the thresholad image then find
        # the largest contour which will be the outline of the stitched image
        conts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        conts = imutils.grab_contours(conts)
        c = max(conts, key.cv2.contourArea)

        #allocate memory for the mask which will contain
        # the bounding box of the stitched image region
        mask = np.zeros(thresh.shape, dtype = "uint8")
        (x, y, w, h) = cv2.boundingRect (c)
        cv2.rectangle(mask, (x,y), (x+ w, y+ h), 255, -1)

        #create two copies of the mask:
        # 1: to serve as the actual rectangular region
        # 2: to serve as the counter for how many pixels need to be removed to form the minimum rectangular region
        minRectangle = mask.copy()
        substitut = mask.copy()

        #kepp on iteratiing untol there are no non-zero pixels left in the subtracted imae
        while cv2.countNonZero(substitut) > 0:
            # erode the minimum rec mask and subtract the thresholded image from the min rec mask 
            # sp we can count if there are any non-zero pixels left
            minRectangle = cv2.erode(minRectangle, none)
            substitut = cv2.subtract(minRectangle, thresh)


        #find contours in the minimum rec mask
        # then extract the bounding box (x,y) coordinates

        conts = cv2.findContours(minRectangle.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        conts = imtuils.grab_contours(conts)
        c = max(conts, key = cv2.contourArea)
        (x, y, w, h) = cv2.boundingRect(c)

        # use the bounding box coords to extract our final stitched iamge
        stitched =  stitched[y:y + h, x:x + w]

    # write the output stitched image to the disk
    cv2.imwrite(args["output_image"], stitched)

     #display the output image to the screen
    cv2.imshow("Stitched_image", stitched)
    cv2.waitKey(0)

# if stitching failed
else:
    print("[INFO] image stitching failed ({})".format(status))










