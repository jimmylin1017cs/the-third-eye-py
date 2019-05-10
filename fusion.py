import time

import cv2
import numpy as np

from scipy.spatial.distance import euclidean

from fastdtw import fastdtw


beacon_location = [[206.30429, 567.3016], [306.30429, 667.3016]]
beacon_on_image = np.array([[1824, 840], [1786, 215], [272, 258], [190, 893]], dtype = "float32")
beacon_on_world = np.array([[540, 1100], [540, 100], [10, 100], [10, 1100]], dtype = "float32")

# box = [x, y, w, h]
# Data = [x, y]
# Fusion_result = [num, name]
# Video_data = [num, x, y]

def generate_transform_matrix(src_pts, dest_pts):

    transform_matrix = cv2.getPerspectiveTransform(src_pts, dest_pts)

    return transform_matrix

def convert_coordinate(pts, transform_matrix):
    
    convert_pts = cv2.perspectiveTransform(pts, transform_matrix)

    return convert_pts




def fusion_model(track_bbs_ids):

    p1 = np.array([[983, 294], 
                    [974, 293], 
                    [972, 293], 
                    [967, 294], 
                    [961, 294]])
    b1 = np.array([[258.401611328125, 195.64553833007812], 
                    [255.2572021484375, 193.5176544189453], 
                    [254.56155395507812, 193.42044067382812], 
                    [252.8370361328125, 194.86778259277344], 
                    [250.7504425048828, 194.57614135742188]])
    p2 = np.array([[195, 205], 
                    [194, 205], 
                    [195, 204], 
                    [195, 204], 
                    [196, 206]])
    b2 = np.array([[-19.362390518188477, 5.228209495544434], 
                    [-19.712507247924805, 5.17970609664917], 
                    [-19.41131019592285, 3.4987947940826416], 
                    [-19.41131019592285, 3.4987947940826416], 
                    [-18.963407516479492, 7.005692005157471]])
    
    distance1, path = fastdtw(p1, b1, dist=euclidean)
    print("p1 - b1 : {}".format(distance1))
    distance2, path = fastdtw(p1, b2, dist=euclidean)
    print("p1 - b2 : {}".format(distance2))
    print("1 : {}".format(distance2 - distance1))

    distance1, path = fastdtw(p2, b1, dist=euclidean)
    print("p2 - b1 : {}".format(distance1))
    distance2, path = fastdtw(p2, b2, dist=euclidean)
    print("p2 - b2 : {}".format(distance2))
    print("2 : {}".format(distance2 - distance1))


def do_fustion(id, pts):

    transform_matrix = generate_transform_matrix(beacon_on_image, beacon_on_world)

    #print(transform_matrix)

    pts = np.array([pts], dtype = "float32")
    pts = np.array([pts])
    #pts = np.array([983, 294], dtype = "float32")
    #print(pts)

    convert_pts = convert_coordinate(pts, transform_matrix)

    #print(convert_pts)
    print("b{} = {}, {}".format(id, convert_pts[0][0][0], convert_pts[0][0][1]))



'''
void convertCoordinate(CvMat  *srcPts, CvMat  *dstPts, image im){
    CvPoint2D32f  src_coordinate[4] = {cvPoint2D32f(813, 934), cvPoint2D32f(783, 358), cvPoint2D32f(245, 362), cvPoint2D32f(256, 927)};
    CvPoint2D32f  dst_coordinate[4] = {cvPoint2D32f(540, 1100),cvPoint2D32f(540, 100),cvPoint2D32f(10, 100),cvPoint2D32f(10, 1100)};
    //CvMat* warp_matrix = cvCreateMat(im.h, im.w, CV_32FC1);
    CvMat* warp_mat = cvCreateMat( 3, 3, CV_32FC1 );
    cvGetPerspectiveTransform(src_coordinate, dst_coordinate, warp_mat);
    //printf("%f %f\n", srcPts->data.fl[0], srcPts->data.fl[1]);
    cvPerspectiveTransform(srcPts, dstPts, warp_mat);
    printf("%f %f\n", dstPts->data.fl[0], dstPts->data.fl[1]);
    //cvWarpPerspective(srcPts, dstPts, warp_matrix, CV_INTER_LINEAR+CV_WARP_FILL_OUTLIERS, cvScalarAll(0));
}'''

if __name__ == "__main__":
    fusion_model([])

class FusionServer():

    def __init__(self):
        pass

