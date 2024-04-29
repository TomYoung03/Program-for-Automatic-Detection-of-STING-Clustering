# Program-for-Automatic-Detection-of-STING-Clustering
A program written for the PhD of Thomas Young. This program uses thresholding and edge detection to detect the presence of STING clustering events on confocal images.
Program lisenced under Creative Commons Attribution-NonCommercial (CC-BY-NC) http://creativecommons.org/licenses/by-nc/4.0/ 

This program has been designed to detect clustering events in cells which is acheived through determining which areas
of the tagged protein are more intense than others.

CLUSTER DETECTION:

Cluster detection works first by providing the program with a single channel image of a fluorescently tagged protein
(note single channel here means that there is no other staining or tagged protein visible in the image, it can still be
a full colour RGB image). The "clusters" are detected by using thresholding, by this method any pixel that is less intense
than a given number is set to 0. This allows the isolation of the much more intense clusters compared to the less intense
background protein. Additionally Gaussian blur is also applied to the image, this reduces noise and can make the edges
of the clusters smoother. Once thresholding has been applied contour (edge) detection is applied to the image, this identifies
all the edges in the image, which given the correct thresholding will align with the edges of the clusters. Once all
edges have been detected they are filtered by size excluding any that are not within the minimum and maximum limits.
This helps reduce identification of small areas of noise that may not correspond to clustering additionally limiting the
maximum size prevents the identification of the entire cytoplasm as one large cluster. These values need to be decided on
by the user and are not universal

CELL DETECTION:

Cells are detected in the same way as clusters, using a single channel image of DAPI stained nuclei and thresholding to
determine edge locations. The same filtering of max and minimum size can also be applied. Different to the cluster detection
is the estimation of cell perimeter which is determined by drawing a circle within which fits all points of the Cell edge.
Note that filtering by size uses the perimeter of the edge detected and not the estimated perimeter from the circle.

lINKING CLUSTERS AND CELLS:

Clusters are linked to their nearest cell. First an estimation is taken of the distance using the center of the cluster
and the center of the cell, this identifies the nearest 3 cells. From these 3 cells it is determined which cells perimeter
is closest to the center of the cluster. This first distance filtering step makes the process a lot faster as it reduces
the number of perimeter pixels that the program has to check for each cluster. Once the cluster identifies the nearest cell
it is assigned as belonging to that cell.

HOW TO USE THE PROGRAM:

First select the nucleus and cluster images to be used and add them to the program using the select Nucleus Image and
select Fluorescent label image buttons. These images must be in .tif format no other format of image can/should be used.

Now select the "Cluster Detection" tab. Here there are 4 values you can manipulate:
1. Minimum cluster perimeter
2. Maximum cluster perimeter
3. Intensity threshold
4. Blur intensity

Minimum cluster perimeter is the smallest perimeter that will still be counted as a cluster
Maximum cluster perimeter is the largest perimeter that will still be counted as a cluster
Intensity threshold is the intensity value below which the program will remove
Blur intensity is the amount of blur applied to the image, this must always be an odd number

These numbers will need to be adjusted per image/set of conditions they will not be the same across images due to differences
in imaging and staining.

Clicking the "Show cluster detection" button will bring up two images, on the left is a black and white image showing
exactly what the program is "seeing", on the right is a colour image with any clusters detected outlined in white.
Adjust the values until you are happy with the detection. IMPORTANT if you change the values, you must press the show cluster
detection for the changes to take effect.

This same process is then used in the "Cell Detection" tab, the image shown here on the right will circle all cells with
the a different coloured circle per cell. As nuclei are more easily defined this detection is likely to have lower values
than the cluster detection.

At the bottom of both of these tabs is the ability to save the cluster/cell detection image, this will save an image in
the same location as the program is running in with the name of the experiment (given in the first tab) along with all the
conditions used to produce that detection.

Once detection of BOTH cells and clusters has been carried out go to the main tab and click the "Analyse Images" button
This will produce an image in which cells and clusters are highlighted with matching colours depending on the cell, use
the save image button to save this image. In this image only cells with clusters are highlighted
Additionally an excel file will be created using the name given in the "Image Analysis Experiment Name" box, this file
will contain a list of all the detected cells, identified by their center coordinates and the values associated with
their clusters. The table is split into cells with clusters and cells without.
Also provided is the values used to produce this image and the percentage of cells with clusters

ADDITIONAL NOTES:

- While colour images are supplied all analysis of the images is done in greyscale
- Using the same settings on the same images will produce the same results
- If at any point during analysis or detection the program displays not responding just wait for the program to finish
it hasn't actually crashed
- If there is an error is saving the data the program will attempt to save it as an excel document titled DATA RECOVERED
- Having the maximum cluster perimeter value too high can lead the program to class lots of seperate clusters together
