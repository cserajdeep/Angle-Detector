!pip install pygame

import math
import cv2
import numpy as np
import pygame


###############################################################
def create_blank(width, height, rgb_color=(0, 0, 0)):

    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


# Method to find the mid point
def midpoint(ptA, ptB):

    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def convert_arc(pt1, pt2, sagitta):

    # extract point coordinates
    x1, y1 = pt1
    x2, y2 = pt2

    # find normal from midpoint, follow by length sagitta
    n = np.array([y2 - y1, x1 - x2])
    n_dist = np.sqrt(np.sum(n**2))

    if np.isclose(n_dist, 0):
        # catch error here, d(pt1, pt2) ~ 0
        print('Error: The distance between pt1 and pt2 is too small.')

    n = n/n_dist
    x3, y3 = (np.array(pt1) + np.array(pt2))/2 + sagitta * n

    # calculate the circle from three points
    # see https://math.stackexchange.com/a/1460096/246399
    A = np.array([
        [x1**2 + y1**2, x1, y1, 1],
        [x2**2 + y2**2, x2, y2, 1],
        [x3**2 + y3**2, x3, y3, 1]])
    M11 = np.linalg.det(A[:, (1, 2, 3)])
    M12 = np.linalg.det(A[:, (0, 2, 3)])
    M13 = np.linalg.det(A[:, (0, 1, 3)])
    M14 = np.linalg.det(A[:, (0, 1, 2)])

    if np.isclose(M11, 0):
        # catch error here, the points are collinear (sagitta ~ 0)
        print('Error: The third point is collinear.')

    cx = 0.5 * M12/M11
    cy = -0.5 * M13/M11
    radius = np.sqrt(cx**2 + cy**2 + M14/M11)

    # calculate angles of pt1 and pt2 from center of circle
    pt1_angle = 180*np.arctan2(y1 - cy, x1 - cx)/np.pi
    pt2_angle = 180*np.arctan2(y2 - cy, x2 - cx)/np.pi

    return (cx, cy), radius, pt1_angle, pt2_angle


def draw_ellipse(
        img, center, axes, angle,
        startAngle, endAngle, color,
        thickness=1, lineType=cv2.LINE_AA, shift=10):

    center = (
        int(round(center[0] * 2**shift)),
        int(round(center[1] * 2**shift))
    )
    axes = (
        int(round(axes[0] * 2**shift)),
        int(round(axes[1] * 2**shift))
    )

    dellip = cv2.ellipse(img, center, axes, angle, startAngle, endAngle, color, thickness, lineType, shift)
    
    return dellip


def draw_grid(img, line_color=(0, 255, 0), thickness=1, type_=cv2.LINE_AA, pxstep=50):

    x = pxstep
    y = pxstep
    while x < img.shape[1]:
        cv2.line(img, (x, 0), (x, img.shape[0]), color=line_color, lineType=type_, thickness=thickness)
        x += pxstep

    while y < img.shape[0]:
        cv2.line(img, (0, y), (img.shape[1], y), color=line_color, lineType=type_, thickness=thickness)
        y += pxstep


def draw_text(img, text,
          font=cv2.FONT_HERSHEY_PLAIN,
          pos=(0, 0),
          font_scale=2,
          font_thickness=2,
          text_color=(0, 255, 0),
          text_color_bg=(0, 0, 0)
          ):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

    return text_size


def getAngle(x, y, z):
    
    ang = math.degrees(math.atan2(z[1]-y[1], z[0]-y[0]) - math.atan2(x[1]-y[1], x[0]-y[0]))
    
    return ang #ang + 360 if ang < 0 else ang


def angle_detector(x1, y1, x2, y2, x3, y3):

    image = create_blank(width, height, rgb_color=bgcolor)

    # Angle calculate
    angle = getAngle((x1, y1), (x2, y2), (x3, y3))
    radian = np.deg2rad(angle)
    
    midY = height // 2
    midX = width // 2

    # Draw center line
    cv2.line(image, (0, midY), (width, midY), color=orange, thickness=2)
    cv2.line(image, (midX, 0), (midX, height), color=orange, thickness=2)

    midY = y2
    midX = x2
    # Draw center line
    cv2.line(image, (0, midY), (width, midY), color=pink, thickness=2)
    cv2.line(image, (midX, 0), (midX, height), color=pink, thickness=2)
    draw_grid(image, line_color=green, thickness=1, type_=cv2.LINE_AA, pxstep=20)

    pt1 = midpoint((x1, y1), (x2, y2))
    pt2 = midpoint((x2, y2), (x3, y3))
    sagitta = 150
    
    if angle > 0:
        center, radius, start_angle, end_angle = convert_arc(pt2, pt1, sagitta)
    else:
        center, radius, start_angle, end_angle = convert_arc(pt1, pt2, sagitta)
        
    axes = (radius, radius)
    draw_ellipse(image, center, axes, 0, start_angle, end_angle, 255)

    # Line thickness of 3 px
    thickness = 3

    start_point = (x1, y1)
    end_point = (x2, y2)
    # Using cv2.line() method
    image = cv2.line(image, start_point, end_point, lcolor, thickness)

    start_point = (x2, y2)
    end_point = (x3, y3)
    # Using cv2.line() method
    image = cv2.line(image, start_point, end_point, lcolor, thickness)

    print('Angle (in degrees): {:.4f}\N{DEGREE SIGN}'.format(angle))
    angdeg = 'deg: {:.4f}, rad: {:.4f}'.format(angle, radian) 
    draw_text(image, angdeg, font_scale=1, pos=(10, 10), text_color=red, text_color_bg=bgcolor)

    # Window name in which image is displayed
    window_name = 'Angle Detector'
    cv2.imwrite(window_name+'.jpg', image)
    
    # Displaying the image
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


###############################################################
# Create new blank 500x500 red image
width, height = 500, 500

bgcolor = (255, 255, 255)
lcolor = (0, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)
orange = (18, 255, 255)
pink = (255, 153, 255)
green = (0, 255, 0)
red = (0, 0, 255)

###############################################################
print('\nCalculate the angle (in degrees) for given three data points (window size 500x500):')
###############################################################

# Call the main function
x1 = int(input('The value of x (the first endpoint) '))
y1 = int(input('The value of y (the first endpoint) '))
if (x1 >= 0 and x1<= 500) and (y1 >= 0 and y1<= 500):
    x2 = int(input('The value of x (the first endpoint) '))
    y2 = int(input('The value of y (the first endpoint) '))

    if (x2 >= 0 and x2<= 500) and (y2 >= 0 and y2<= 500):
        x3 = int(input('The value of x (the first endpoint) '))
        y3 = int(input('The value of y (the first endpoint) '))
        
        if (x3 >= 0 and x3<= 500) and (y3 >= 0 and y3<= 500):
            angle_detector(x1, y1, x2, y2, x3, y3)
        else:
            print('Please!! input third data points with in 0 to 500 range')
    
    else:
        print('Please!! input second data points with in 0 to 500 range')
            
else:
     print('Please!! input first data points with in 0 to 500 range')